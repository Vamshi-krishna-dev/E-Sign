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


# Dependency Injection
def get_agreement_service() -> AgreementService:
    pdf = PDFGenerator()
    loan_client = LoanClient()
    return AgreementService(pdf=pdf, loan_client=loan_client)


# Get agreement (generate if not exists)
@router.get("/{loan_id}", response_model=AgreementResponse)
def get_agreement(
    loan_id: int = Path(..., gt=0, description="Loan ID"),
    db: Session = Depends(get_db),
    service: AgreementService = Depends(get_agreement_service),
):
    return service.fetch_agreement(loan_id, db)


# Verify agreement hash
@router.get("/{loan_id}/hash")
def verify_hash(
    loan_id: int = Path(..., gt=0, description="Loan ID"),
    db: Session = Depends(get_db),
    service: AgreementService = Depends(get_agreement_service),
):
    return service.verify_hash(loan_id, db)