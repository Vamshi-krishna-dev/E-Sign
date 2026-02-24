from pydantic import BaseModel, Field, field_validator
from typing import Optional


class InitiateRequest(BaseModel):
    loan_id: int = Field(..., gt=0)
    aadhar_number: str = Field(..., min_length=12, max_length=12)

    @field_validator("aadhar_number")
    def validate_aadhar(cls, v):
        if not v.isdigit():
            raise ValueError("Aadhaar must contain only digits")
        if len(v) != 12:
            raise ValueError("Aadhaar must be 12 digits")
        return v


class InitiateResponse(BaseModel):
    transaction_id: str
    masked_aadhaar: str


class VerifyRequest(BaseModel):
    transaction_id: str
    otp: str = Field(..., min_length=6, max_length=6)

    @field_validator("otp")
    def validate_otp(cls, v):
        if not v.isdigit():
            raise ValueError("OTP must contain only digits")
        return v


class VerifyResponse(BaseModel):
    signed_pdf: Optional[str]
    file_hash: Optional[str]
    status: str
