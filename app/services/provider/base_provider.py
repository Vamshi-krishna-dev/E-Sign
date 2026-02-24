class BaseESignProvider:

    async def initiate_esign(self, payload: dict):
        raise NotImplementedError

    async def verify_esign(self, payload: dict):
        raise NotImplementedError

    async def fetch_agreement(self, loan_id: int):
        raise NotImplementedError

    async def disbursement_status(self, loan_id: int):
        raise NotImplementedError

    async def confirm_disbursement(self, payload: dict):
        raise NotImplementedError