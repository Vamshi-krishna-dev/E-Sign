from sqlalchemy.orm import Session
from app.models.models import DisbursementRecord
from app.services.provider.provider_client import ProviderClient
from app.core.logger import logger
from app.core.exceptions import throw_error
from app.utils.response import success_response
from app.db.db_helper import safe_commit
import datetime
from app.services.provider.factory import get_esign_provider

provider = get_esign_provider()


class DisbursementService:

    async def check_status(self, loan_id: int, db: Session):
        logger.info(f"[DISBURSEMENT] Checking status for loan_id={loan_id}")

        if loan_id <= 0:
            throw_error("Invalid loan ID", 400)

        try:
            provider_status = await provider.disbursement_status(loan_id)
        except Exception as e:
            logger.error(f"[Provider ERROR] {e}")
            throw_error("Unable to fetch disbursement status", 503)

        return success_response(
            "Disbursement status fetched",
            provider_status
        )

    async def confirm_disbursement(self, data, db: Session):
        payload = data.model_dump()
        loan_id = payload["loan_id"]

        logger.info(f"[DISBURSEMENT] Confirm request for loan_id={loan_id}")

        # Idempotency
        existing = db.query(DisbursementRecord).filter(
            DisbursementRecord.loan_id == loan_id
        ).first()

        if existing:
            return success_response(
                "Disbursement already confirmed",
                {
                    "loan_id": existing.loan_id,
                    "utr_number": existing.utr_number,
                    "status": existing.status
                }
            )

        # Provider confirm
        try:
            provider_resp = await provider.confirm_disbursement(payload)
        except Exception as e:
            logger.error(f"[Provider ERROR] {e}")
            throw_error("Disbursement confirmation failed", 503)

        if "utr_number" not in provider_resp:
            throw_error("Invalid provider response", 500)

        utr = provider_resp["utr_number"]

        record = DisbursementRecord(
            loan_id=loan_id,
            user_id=1,  # TEMP: remove after loan module integration
            utr_number=utr,
            status=provider_resp.get("status", "SUCCESS"),
            remarks=payload.get("remarks"),
            disbursed_at=datetime.datetime.utcnow()
        )

        db.add(record)
        safe_commit(db)
        db.refresh(record)

        return success_response(
            "Disbursement confirmed successfully",
            {
                "loan_id": loan_id,
                "utr_number": utr,
                "status": record.status
            }
        )