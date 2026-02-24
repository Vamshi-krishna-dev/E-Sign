from fastapi import APIRouter, Depends, Request, Header, Body
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.services.esign_service import EsignService
from app.schemas.esign_schema import InitiateRequest, VerifyRequest
from app.schemas.callback_schema import EsignCallbackRequest
from app.pdf.signature import verify_callback_signature
from app.core.exceptions import throw_error
from app.utils.response import success_response
from app.middleware.correlation_id import get_correlation_id
from app.core.logger import logger


router = APIRouter(
    prefix="/api/v1/loan/esign",
    tags=["E-Sign"]
)

# Proper DI
def get_esign_service():
    return EsignService()


# INITIATE E-SIGN (SEND OTP)
@router.post("/initiate")
async def initiate_esign(
    request_data: InitiateRequest,
    db: Session = Depends(get_db),
    service: EsignService = Depends(get_esign_service),
):
    cid = get_correlation_id()
    logger.info(f"[E-SIGN] CID={cid} Initiating eSign for loan_id={request_data.loan_id}")

    result = await service.initiate_esign(request_data, db)
    return success_response(result)


# VERIFY E-SIGN (VERIFY OTP + GENERATE SIGNATURE)
@router.post("/verify")
async def verify_esign(
    request_data: VerifyRequest,
    db: Session = Depends(get_db),
    service: EsignService = Depends(get_esign_service),
):
    cid = get_correlation_id()
    logger.info(f"[E-SIGN] CID={cid} Verifying OTP for txn={request_data.transaction_id}")

    result = await service.verify_esign(request_data, db)
    return success_response(result)


# PROVIDER CALLBACK (SECURE)
@router.post("/callback")
async def esign_callback(
    request: Request,
    callback_body: EsignCallbackRequest = Body(...),   # <--- forces Swagger to show body # pyright: ignore[reportUndefinedVariable]
    db: Session = Depends(get_db),
    service: EsignService = Depends(get_esign_service),
    x_signature: str = Header(None, alias="X-Signature"),
):
    cid = get_correlation_id()
    logger.info(f"[E-SIGN CALLBACK] CID={cid} Callback received")

    # Get raw payload for signature verification
    raw_body = await request.body()

    # DEV MODE → Skip signature verification completely
    if settings.ENV.upper() == "DEV":
        logger.info("[CALLBACK] DEV MODE -> Signature ignored")
        return await service.handle_callback(callback_body, db)

    # PROD MODE → Strict signature validation
    if not x_signature:
        throw_error("Missing X-Signature header", 401)

    if not verify_callback_signature(raw_body, x_signature):
        logger.warning(f"[CALLBACK] CID={cid} Invalid callback signature")
        throw_error("Invalid callback signature", 403)

    # Body already parsed by FastAPI (callback_body)
    response = await service.handle_callback(callback_body, db)

    logger.info(f"[E-SIGN CALLBACK] CID={cid} Callback processed")
    return response