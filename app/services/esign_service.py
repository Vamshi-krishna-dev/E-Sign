from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import httpx

from app.models.esign_session import EsignSession, EsignStatus
from app.models.audit_logs import EsignAuditLog
from app.models.signed_documents import SignedDocument
from app.provider.factory import get_esign_provider
from app.core.exceptions import throw_error
from app.core.logger import logger
from app.core.config import settings
from app.db.db_helper import safe_commit
from app.utils.file_handler import FileHandler


class EsignService:

    def __init__(self):
        self.file_handler = FileHandler()

    # INITIATE E-SIGN
    async def initiate_esign(self, data, db: Session):

        logger.info(f"[E-SIGN INIT] loan_id={data.loan_id}")

        provider = get_esign_provider()
        payload = data.model_dump()

        try:
            provider_resp = await provider.initiate_esign(payload)
        except Exception as exc:
            logger.error(f"[E-SIGN INIT] Provider error: {exc}")
            throw_error("eSign provider unreachable", 503)

        txn = provider_resp.get("transaction_id")

        if not txn:
            throw_error("Invalid provider response", 502)

        session = EsignSession(
            loan_id=data.loan_id,
            user_id=1,  # TODO: replace after auth integration
            transaction_id=txn,
            request_payload=payload,
            response_payload=provider_resp,
            status=EsignStatus.OTP_SENT
        )

        log = EsignAuditLog(
            session_id=None,
            event_type="OTP_SENT",
            event_description=f"OTP sent for txn={txn}"
        )

        try:
            db.add(session)
            db.flush()  # get session.id

            log.session_id = session.id
            db.add(log)

            safe_commit(db)

        except IntegrityError:
            db.rollback()
            throw_error("Duplicate transaction id", 409)

        return {
            "transaction_id": txn,
            "masked_aadhaar": provider_resp.get("masked_aadhaar")
        }

    # VERIFY OTP
    async def verify_esign(self, data, db: Session):

        logger.info(f"[E-SIGN VERIFY] txn={data.transaction_id}")

        provider = get_esign_provider()

        session = db.query(EsignSession).filter(
            EsignSession.transaction_id == data.transaction_id
        ).first()

        if not session:
            throw_error("Invalid transaction ID", 404)

        if session.status == EsignStatus.SIGNED:
            return {"transaction_id": session.transaction_id, "status": "SIGNED"}

        if session.status != EsignStatus.OTP_SENT:
            throw_error("Invalid signing state", 400)

        try:
            provider_resp = await provider.verify_esign(data.model_dump())
        except Exception as exc:
            logger.error(f"[E-SIGN VERIFY] Provider error: {exc}")
            throw_error("OTP verification failed", 503)

        if provider_resp.get("status") != "SIGNED":

            log = EsignAuditLog(
                session_id=session.id,
                event_type="OTP_FAILED",
                event_description="OTP verification failed"
            )

            db.add(log)
            safe_commit(db)

            throw_error("Invalid OTP", 400)

        session.status = EsignStatus.SIGNED

        log = EsignAuditLog(
            session_id=session.id,
            event_type="SIGNED",
            event_description="OTP verified successfully"
        )

        db.add(log)
        safe_commit(db)

        return {
            "transaction_id": session.transaction_id,
            "status": "SIGNED"
        }

    # CALLBACK HANDLER
    async def handle_callback(self, data, db: Session):

        logger.info(f"[CALLBACK] txn={data.transaction_id}")

        session = db.query(EsignSession).filter(
            EsignSession.transaction_id == data.transaction_id
        ).first()

        if not session:
            throw_error("Unknown transaction ID", 404)

        if session.status == EsignStatus.SIGNED:
            logger.info("[CALLBACK] already processed")
            return {"status": "already_processed"}

        if data.status != "SIGNED":
            session.status = EsignStatus.FAILED
            safe_commit(db)
            throw_error("Callback status FAILED", 400)

        signed_url = data.signed_pdf_url

        # DOWNLOAD PDF
        if signed_url == "LOCAL":

            file_path, file_hash = self.file_handler.generate_mock_signed_pdf()

        else:

            async with httpx.AsyncClient(timeout=10) as client:

                resp = await client.get(signed_url)

                if resp.status_code != 200:
                    throw_error("Failed to download signed PDF", 502)

                file_path, file_hash = self.file_handler.save_signed_pdf_async(
                    content=resp.content,
                    txn=session.transaction_id
                )

        signed_doc = SignedDocument(
            session_id=session.id,
            signed_pdf_path=file_path,
            file_hash=file_hash
        )

        session.status = EsignStatus.SIGNED
        session.callback_payload = data.model_dump()

        log = EsignAuditLog(
            session_id=session.id,
            event_type="CALLBACK_RECEIVED",
            event_description=f"Signed document stored: {file_path}"
        )

        db.add(signed_doc)
        db.add(log)

        safe_commit(db)

        return {
            "status": "ok",
            "file_path": file_path
        }