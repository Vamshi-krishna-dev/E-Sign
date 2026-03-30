from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from db.database import get_db
from services.agreement_service import AgreementService
from services.loan_client import LoanClient


router = APIRouter(
    prefix="/api/v1/loan/agreement",
    tags=["Agreement"]
)


# ------------------------------------------------
# Dependency Injection (UPDATED)
# ------------------------------------------------
def get_agreement_service() -> AgreementService:
    loan_client = LoanClient()
    return AgreementService(loan_client=loan_client)


# ------------------------------------------------
# GET / CREATE AGREEMENT
# ------------------------------------------------
@router.get("/{loan_id}")
def get_agreement(
    loan_id: int = Path(..., gt=0, description="Loan ID"),
    db: Session = Depends(get_db),
    service: AgreementService = Depends(get_agreement_service),
):
    return service.fetch_agreement(loan_id, db)


# ------------------------------------------------
# PDF VIEWER (NEW)
# ------------------------------------------------
@router.get("/{loan_id}/view")
def view_agreement(
    loan_id: int = Path(..., gt=0, description="Loan ID"),
    db: Session = Depends(get_db),
    service: AgreementService = Depends(get_agreement_service),
):
    return service.get_agreement_view(loan_id, db)


# ------------------------------------------------
# VERIFY HASH
# ------------------------------------------------
@router.get("/{loan_id}/hash")
def verify_hash(
    loan_id: int = Path(..., gt=0, description="Loan ID"),
    db: Session = Depends(get_db),
    service: AgreementService = Depends(get_agreement_service),
):
    return service.verify_hash(loan_id, db)