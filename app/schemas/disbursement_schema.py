from pydantic import BaseModel, Field
from typing import Optional


class DisbursementStatusResponse(BaseModel):
    loan_id: int
    status: str
    utr_number: Optional[str] = None
    expected_credit_time: Optional[str] = None
    disbursed_at: Optional[str] = None
    remarks: Optional[str] = None


class DisbursementConfirmRequest(BaseModel):
    loan_id: int = Field(..., gt=0)
    remarks: Optional[str] = None


class DisbursementConfirmResponse(BaseModel):
    loan_id: int
    utr_number: str
    status: str
    remarks: Optional[str] = None
