from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.models import EsignSession, SignedDocument, EsignAuditLog, EsignStatus
from app.services.provider.factory import get_esign_provider
from app.core.exceptions import throw_error
from app.core.logger import logger
from app.core.config import settings
from app.db.db_helper import safe_commit
from app.pdf.signature import verify_callback_signature
from app.pdf.file_handler import FileHandler
from app.middleware.correlation_id import get_correlation_id

from datetime import datetime
import httpx


class EsignService:

    def __init__(self):
        # per-instance creation
        self.file_handler = FileHandler()

    # INITIATE E-SIGN (SEND OTP)
    async def initiate_esign(self, data, db: Session):
        cid = get_correlation_id()
        logger.info(f"[E-SIGN INIT] CID={cid} loan_id={data.loan_id}")

        provider = get_esign_provider()

        payload = data.model_dump()

        # 1. Call provider API
        try:
            provider_resp = await provider.initiate_esign(payload)
        except Exception as exc:
            logger.error(f"[E-SIGN INIT] Provider error: {exc}")
            throw_error("eSign provider unreachable", 503)

        if "transaction_id" not in provider_resp:
            throw_error("Invalid provider response", 502)

        txn = provider_resp["transaction_id"]

        # 2. Create session record
        session = EsignSession(
            loan_id=data.loan_id,
            user_id=1,  # TODO: replace with actual user ID from auth
            transaction_id=txn,
            request_payload=payload,
            response_payload=provider_resp,
            status=EsignStatus.OTP_SENT,
        )

        db.add(session)
        safe_commit(db)
        db.refresh(session)

        # 3. Audit log
        log = EsignAuditLog(
            session_id=session.id,
            event_type="OTP_SENT",
            event_description=f"OTP sent for txn={txn}",
        )
        db.add(log)
        safe_commit(db)

        return {
            "transaction_id": txn,
            "masked_aadhaar": provider_resp.get("masked_aadhaar", "XXXX-XXXX-1234")
        }

    # VERIFY E-SIGN (VERIFY OTP + GENERATE SIGNATURE)
    async def verify_esign(self, data, db: Session):
        cid = get_correlation_id()
        logger.info(f"[E-SIGN VERIFY] CID={cid} txn={data.transaction_id}")

        provider = get_esign_provider()

        # 1. Get session
        session = db.query(EsignSession).filter(
            EsignSession.transaction_id == data.transaction_id
        ).first()

        if not session:
            throw_error("Invalid transaction ID", 404)

        # 2. Idempotency
        if session.status == EsignStatus.SIGNED:
            logger.info(f"[E-SIGN VERIFY] Already signed → return OK")
            return {"transaction_id": session.transaction_id, "status": "SIGNED"}

        if session.status != EsignStatus.OTP_SENT:
            throw_error("Invalid signing state", 400)

        # 3. Verify OTP with provider
        try:
            provider_resp = await provider.verify_esign(data.model_dump())
        except Exception as exc:
            logger.error(f"[E-SIGN VERIFY] Provider error: {exc}")
            throw_error("OTP verification failed", 503)

        if provider_resp.get("status") != "SIGNED":
            # Audit failure
            log = EsignAuditLog(
                session_id=session.id,
                event_type="OTP_FAILED",
                event_description="OTP verification failed"
            )
            db.add(log)
            safe_commit(db)

            throw_error("Invalid OTP", 400)

        # 4. Mark session signed
        session.status = EsignStatus.SIGNED
        session.callback_payload = provider_resp
        safe_commit(db)

        # 5. Save AUDIT LOG
        log = EsignAuditLog(
            session_id=session.id,
            event_type="SIGNED",
            event_description="Document signed successfully"
        )
        db.add(log)
        safe_commit(db)

        # 6. If provider sends LOCAL PDF (mock)
        if provider_resp.get("signed_pdf_url") == "LOCAL":
            return {
                "transaction_id": session.transaction_id,
                "file_path": "LOCAL",
                "file_hash": "LOCAL"
            }

        # 7. Download real PDF (ASYNC)
        file_url = provider_resp["signed_pdf_url"]

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(file_url)
            if resp.status_code != 200:
                throw_error("Failed to download signed PDF", 502)

            file_path, file_hash = self.file_handler.save_signed_pdf_async(
                content=resp.content,
                txn=session.transaction_id
            )

        # 8. Save document
        signed_doc = SignedDocument(
            session_id=session.id,
            signed_pdf_path=file_path,
            file_hash=file_hash,
        )

        db.add(signed_doc)
        safe_commit(db)

        return {
            "transaction_id": session.transaction_id,
            "file_path": file_path,
            "file_hash": file_hash
        }

    # CALLBACK HANDLER
    async def handle_callback(self, data, db: Session):
        cid = get_correlation_id()
        logger.info(f"[E-SIGN CALLBACK] CID={cid} txn={data.transaction_id}")

        # 1. Fetch eSign session
        session = db.query(EsignSession).filter(
            EsignSession.transaction_id == data.transaction_id
        ).first()

        if not session:
            throw_error("Unknown transaction ID", 404)

        # 2. Idempotency 
        if session.status == EsignStatus.SIGNED:
            logger.info("[CALLBACK] Already processed — ignoring")
            return {"status": "already_processed"}

        # 3. Handle failure from provider
        if data.status != "SIGNED":
            session.status = EsignStatus.FAILED
            safe_commit(db)
            throw_error("Callback status = FAILED", 400)

        # 4. Save callback JSON
        session.callback_payload = data.model_dump()
        safe_commit(db)

        # 5. DOWNLOAD SIGNED PDF
        signed_url = data.signed_pdf_url
        if signed_url == "LOCAL":
            # your mock PDF generator
            file_path, file_hash = self.file_handler.generate_mock_signed_pdf()
        else:
            file_path, file_hash = self.file_handler.download_and_save_pdf(
                signed_url,
                save_path=settings.SIGNED_PDF_PATH
            )

        # 6. Insert into signed_documents table
        signed_doc = SignedDocument(
            session_id=session.id,
            agreement_id=session.agreement_id,  # if you link agreement
            signed_pdf_path=file_path,
            file_hash=file_hash
        )
        db.add(signed_doc)

        # 7. Update session → SIGNED
        session.status = EsignStatus.SIGNED
        safe_commit(db)

        # 8. Add audit log
        log = EsignAuditLog(
            session_id=session.id,
            event_type="CALLBACK_RECEIVED",
            event_description=f"Signed PDF stored: {file_path}"
        )
        db.add(log)
        safe_commit(db)

        logger.info(f"[CALLBACK] PDF stored → {file_path}")

        return {"status": "ok", "file_path": file_path}