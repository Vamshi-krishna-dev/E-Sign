from fastapi import APIRouter, Depends, Path, Body
from sqlalchemy.orm import Session

from db.database import get_db
from services.disbursement_service import DisbursementService
from schemas.disbursement_schema import DisbursementConfirmRequest



router = APIRouter(
    prefix="/api/v1/loan/disbursement",
    tags=["Disbursement"]
)


# ------------------------------------------------
# Dependency Injection
# ------------------------------------------------
def get_disbursement_service() -> DisbursementService:
    return DisbursementService()


# ------------------------------------------------
# GET DISBURSEMENT STATUS
# ------------------------------------------------
@router.get("/{loan_id}/status")
def get_disbursement_status(
    loan_id: int = Path(..., gt=0, description="Loan ID"),
    db: Session = Depends(get_db),
    service: DisbursementService = Depends(get_disbursement_service),
):
    return service.get_status(loan_id, db)


# ------------------------------------------------
# CONFIRM DISBURSEMENT
# ------------------------------------------------
@router.post("/confirm")
def confirm_disbursement(
    payload: DisbursementConfirmRequest,
    db: Session = Depends(get_db),
    service: DisbursementService = Depends(get_disbursement_service),
):
    # NOTE:
    # Admin/manual trigger only.
    # Primary flow is automatic via e-sign callback.

    loan_id = payload.loan_id
    return service.confirm(loan_id, db)