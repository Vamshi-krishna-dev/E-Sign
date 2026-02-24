from typing import Dict, Any
from app.services.provider.base_provider import BaseESignProvider
from app.services.provider.provider_client import ProviderClient


class EmudhraProvider(BaseESignProvider):
    """
    Real eMudhra integration.
    This class uses ProviderClient to make HTTP requests.
    """

    def __init__(self):
        self.client = ProviderClient()

    async def initiate_esign(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        resp = await self.client.post("/esign/initiate", payload)
        # Map provider-specific fields to internal structure
        return {
            "transaction_id": resp["txnId"],
            "masked_aadhaar": resp["maskedAadhaar"],
            "status": resp.get("status", "OTP_SENT")
        }

    async def verify_esign(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        resp = await self.client.post("/esign/verify", payload)
        return {
            "transaction_id": resp["txnId"],
            "status": resp["status"],
            "signed_pdf_url": resp.get("signedPdfUrl", None)
        }

    async def parse_callback(self, raw_body: bytes) -> Dict[str, Any]:
        """
        Provider sends callback payload. Convert it to unified format.
        """
        import json
        data = json.loads(raw_body)

        return {
            "transaction_id": data["txnId"],
            "status": data["status"]
        }

    def map_provider_status(self, provider_resp: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "transaction_id": provider_resp.get("txnId"),
            "status": provider_resp.get("status"),
            "signed_pdf_url": provider_resp.get("signedPdfUrl")
        }