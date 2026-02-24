import uuid
import random
from app.services.provider.base_provider import BaseESignProvider

class MockESignProvider(BaseESignProvider):

    async def initiate_esign(self, payload: dict):
        aadhaar = payload["aadhar_number"]
        last4 = aadhaar[-4:]
        masked = f"XXXX-XXXX-{last4}"

        return {
            "transaction_id": uuid.uuid4().hex,
            "status": "OTP_SENT",
            "masked_aadhaar": masked,
            "message": "Mock OTP sent"
        }

    async def verify_esign(self, payload: dict):
        if random.random() < 0.1:
            return {"status": "FAILED", "message": "Mock OTP fail"}

        return {
            "transaction_id": payload["transaction_id"],
            "status": "SIGNED",
            "signed_pdf_url": "LOCAL"
        }

    async def fetch_agreement(self, loan_id: int):
        return {
            "loan_id": loan_id,
            "pdf_url": "LOCAL",
            "borrower_name": "Mock User",
            "loan_amount": 50000,
            "interest_rate": 12.5
        }

    async def disbursement_status(self, loan_id: int):
        return {
            "loan_id": loan_id,
            "status": "IN_PROGRESS",
            "utr_number": None
        }

    async def confirm_disbursement(self, payload: dict):
        return {
            "loan_id": payload["loan_id"],
            "utr_number": uuid.uuid4().hex[:12].upper(),
            "status": "SUCCESS"
        }