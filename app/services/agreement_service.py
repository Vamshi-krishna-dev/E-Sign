from sqlalchemy.orm import Session
from app.models.models import Agreement
from app.core.logger import logger
from app.core.exceptions import throw_error
from app.pdf.pdf_generator import PDFGenerator
from app.services.loan_client import LoanClient
from app.middleware.correlation_id import get_correlation_id
from app.models.loan_dummy import DummyLoan
from app.utils.response import success_response
from app.core.config import settings


class AgreementService:

    def __init__(self, pdf: PDFGenerator, loan_client: LoanClient):
        self.pdf = pdf
        self.loan_client = loan_client

    def fetch_agreement(self, loan_id: int, db: Session):
        cid = get_correlation_id()
        logger.info(f"[Agreement] CID={cid} Fetching agreement for loan_id={loan_id}")

        if loan_id <= 0:
            throw_error("Invalid loan id", 400)

        # -------- Loan Fetch Logic (DEV vs PROD) --------
        if settings.ENV == "DEV":
            loan = db.query(DummyLoan).filter(DummyLoan.id == loan_id).first()

            if not loan:
                throw_error("Loan not found in dummy DB", 404)

            loan = {
                "borrower_name": loan.borrower_name,
                "loan_amount": loan.loan_amount,
                "loan_status": loan.loan_status,
            }

        else:
            # REAL LOAN SERVICE
            loan = self.loan_client.get_loan_sync(loan_id)
            if not loan:
                throw_error("Loan not found", 404)
        
        if loan["loan_status"] != "APPROVED":
            throw_error("Loan is not approved", 403)

        # -------- Check Active Agreement --------
        existing = db.query(Agreement).filter(
            Agreement.loan_id == loan_id,
            Agreement.is_active == True
        ).first()

        if existing:
            return success_response(
                "Agreement already exists",
                {
                    "exists": True,
                    "loan_id": loan_id,
                    "version": existing.version,
                    "pdf_path": existing.agreement_pdf_path,
                }
            )

        # -------- Determine Version --------
        latest = db.query(Agreement).filter(
            Agreement.loan_id == loan_id
        ).order_by(Agreement.version.desc()).first()

        new_version = 1 if not latest else latest.version + 1

        # -------- Generate PDF --------
        pdf_output = self.pdf.generate_agreement(
            loan_id=loan_id,
            borrower_name=loan["borrower_name"],
            loan_amount=loan["loan_amount"],
        )

        # pdf_output = { "file_path": "xxx", "file_name": "yyy" }
        file_path = pdf_output["file_path"]

        # -------- Generate Hash --------
        file_hash = self.pdf.generate_hash(file_path)

        # -------- Save Agreement Record --------
        agreement = Agreement(
            loan_id=loan_id,
            user_id=1,  # REPLACE AFTER AUTH INTEGRATION
            version=new_version,
            agreement_pdf_path=file_path,
            file_hash=file_hash,
            is_active=True,
        )

        db.add(agreement)
        db.commit()
        db.refresh(agreement)

        return success_response(
            "Agreement generated successfully",
            {
                "exists": False,
                "loan_id": loan_id,
                "version": new_version,
                "pdf_path": file_path,
                "file_hash": file_hash,
            }
        )


    def verify_hash(self, loan_id: int, db: Session):
        cid = get_correlation_id()
        logger.info(f"[Agreement] CID={cid} Verifying hash for loan_id={loan_id}")

        agreement = db.query(Agreement).filter(
            Agreement.loan_id == loan_id,
            Agreement.is_active == True
        ).first()

        if not agreement:
            throw_error("Agreement not found", 404)

        generated_hash = self.pdf.generate_hash(agreement.agreement_pdf_path)

        if generated_hash != agreement.file_hash:
            throw_error("Document has been modified", 409)

        return success_response(
            "Hash verified",
            {
                "loan_id": loan_id,
                "hash": generated_hash
            }
        )