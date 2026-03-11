from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class EsignCallbackRequest(BaseModel):
    transaction_id: str
    status: str
    signed_pdf_url: str | None = None
