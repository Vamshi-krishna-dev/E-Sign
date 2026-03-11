from fastapi import APIRouter, Depends, Request, Header, Body
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.services.esign_service import EsignService
from app.schemas.esign_schema import InitiateRequest, VerifyRequest
from app.schemas.callback_schema import EsignCallbackRequest
from app.utils.signature import verify_callback_signature
from app.core.exceptions import throw_error
from app.utils.response import success_response
from app.core.logger import logger


router = APIRouter(
    prefix="/api/v1/loan/esign",
    tags=["E-Sign"]
)


# Dependency Injection
def get_esign_service() -> EsignService:
    return EsignService()


# Initiate eSign (Send OTP)
@router.post("/initiate")
async def initiate_esign(
    request_data: InitiateRequest,
    db: Session = Depends(get_db),
    service: EsignService = Depends(get_esign_service),
):
    logger.info(f"E-Sign initiate request for loan_id={request_data.loan_id}")

    result = await service.initiate_esign(request_data, db)
    return success_response(result)


# Verify OTP
@router.post("/verify")
async def verify_esign(
    request_data: VerifyRequest,
    db: Session = Depends(get_db),
    service: EsignService = Depends(get_esign_service),
):
    logger.info(f"E-Sign verify request for txn={request_data.transaction_id}")

    result = await service.verify_esign(request_data, db)
    return success_response(result)


# Provider Callback
@router.post("/callback")
async def esign_callback(
    request: Request,
    callback_body: EsignCallbackRequest = Body(...),
    db: Session = Depends(get_db),
    service: EsignService = Depends(get_esign_service),
    x_signature: str | None = Header(None, alias="X-Signature"),
):
    logger.info(f"E-Sign callback received for txn={callback_body.transaction_id}")

    raw_body = await request.body()

    # DEV mode → skip signature validation
    if settings.ENV.upper() == "DEV":
        logger.info("DEV mode: skipping signature validation")
        return await service.handle_callback(callback_body, db)

    # PROD mode → validate signature
    if not x_signature:
        throw_error("Missing X-Signature header", 401)

    if not verify_callback_signature(raw_body, x_signature):
        logger.warning(f"Invalid callback signature for txn={callback_body.transaction_id}")
        throw_error("Invalid callback signature", 403)

    result = await service.handle_callback(callback_body, db)

    logger.info(f"E-Sign callback processed for txn={callback_body.transaction_id}")
    return result