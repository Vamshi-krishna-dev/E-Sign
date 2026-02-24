from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class EsignCallbackRequest(BaseModel):
    transaction_id: str
    loan_id: int
    status: Optional[str] = None
    signed_pdf_url: Optional[str] = None    
    provider_signature_id: Optional[str] = None
    timestamp: Optional[datetime] = None
