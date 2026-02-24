from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.agreement_service import AgreementService
from app.pdf.pdf_generator import PDFGenerator
from app.services.loan_client import LoanClient
from app.schemas.agreement_schema import AgreementResponse

router = APIRouter(
    prefix="/api/v1/loan/agreement",
    tags=["Agreement"]
)


# --- Dependency Injection ---
def get_agreement_service():
    pdf = PDFGenerator()
    loan_client = LoanClient()
    return AgreementService(pdf=pdf, loan_client=loan_client)


# ---------------------------- ROUTES ---------------------------- #

@router.get("/{loan_id}")
def get_agreement(
    loan_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    service: AgreementService = Depends(get_agreement_service),
):
    """
    Async wrapper that calls sync service method using threadpool
    """
    return  service.fetch_agreement(loan_id, db)


@router.get("/{loan_id}/hash")
def verify_hash(
    loan_id: int,
    db: Session = Depends(get_db),
    service: AgreementService = Depends(get_agreement_service),
):
    """
    Async wrapper for hash verification.
    """
    return  service.verify_hash(loan_id, db)