from app.services.provider.base_provider import BaseESignProvider
from app.services.provider.provider_client import ProviderClient

class RealESignProvider(BaseESignProvider):

    def __init__(self):
        self.client = ProviderClient()

    async def initiate_esign(self, payload: dict):
        return await self.client._post("esign/initiate", payload)

    async def verify_esign(self, payload: dict):
        return await self.client._post("esign/verify", payload)

    async def fetch_agreement(self, loan_id: int):
        return await self.client._get(f"agreement/{loan_id}")

    async def disbursement_status(self, loan_id: int):
        return await self.client._get(f"disbursement/status/{loan_id}")

    async def confirm_disbursement(self, payload: dict):
        return await self.client._post("disbursement/confirm", payload)