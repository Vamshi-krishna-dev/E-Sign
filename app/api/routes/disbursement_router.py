from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.disbursement_schema import DisbursementConfirmRequest
from app.services.disbursement_service import DisbursementService
from app.core.security.role_auth import require_admin
from app.middleware.correlation_id import get_correlation_id
from app.utils.response import success_response
from app.core.logger import logger


router = APIRouter(
    prefix="/api/v1/loan/disbursement",
    tags=["Disbursement"]
)


# Proper service dependency
def get_disbursement_service():
    return DisbursementService()


# 1. GET DISBURSEMENT STATUS  (User or Admin)
@router.get("/{loan_id}/status")
async def get_status(
    loan_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    service: DisbursementService = Depends(get_disbursement_service),
):
    cid = get_correlation_id()
    logger.info(f"[DISBURSEMENT] CID={cid} GET STATUS loan_id={loan_id}")

    # Service already returns a success_response
    return await service.check_status(loan_id, db)

# 2. CONFIRM DISBURSEMENT (Admin ONLY)
@router.post("/confirm", dependencies=[Depends(require_admin)])
async def confirm_disbursement(
    request: DisbursementConfirmRequest,
    db: Session = Depends(get_db),
    service: DisbursementService = Depends(get_disbursement_service),
):
    cid = get_correlation_id()
    logger.info(f"[DISBURSEMENT] CID={cid} CONFIRM loan_id={request.loan_id}")

    result = await service.confirm_disbursement(request, db)
    return result