import httpx
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import throw_error
from app.middleware.correlation_id import get_correlation_id
from app.models.loan_dummy import DummyLoan  # <-- Only used in DEV


class LoanClient:
    """
    Loan client that handles both:
    - DEV mode: reads loan data from local DummyLoan table
    - PROD mode: communicates with real Loan Service via HTTP
    """

    def __init__(self):
        self.base_url = settings.LOAN_SERVICE_BASE_URL.rstrip("/")

        # Configurable timeouts
        self.timeout = httpx.Timeout(
            connect=2.0,
            read=5.0,
            write=5.0,
            pool=5.0,
        )

        # Retry on temporary server failure
        self.retry_status = {502, 503, 504}

    # INTERNAL: Call Real Loan Service API (async)
    async def _call_real_async(self, loan_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/{loan_id}"
        cid = get_correlation_id()

        for attempt in range(2):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.get(url, headers={"X-Request-ID": cid})

            except httpx.ConnectError:
                if attempt == 0:
                    continue
                throw_error("Loan service unreachable", 503)

            if resp.status_code in self.retry_status and attempt == 0:
                continue

            break

        if resp.status_code == 404:
            throw_error("Loan not found", 404)

        if resp.status_code != 200:
            throw_error("Loan Service Failure", 503)

        try:
            body = resp.json()
        except Exception:
            throw_error("Invalid JSON from Loan Service", 502)

        if "data" not in body:
            throw_error("Loan Service missing 'data' field", 502)

        return body["data"]

    # INTERNAL: Call Real Loan Service API (sync)
    def _call_real_sync(self, loan_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/{loan_id}"
        cid = get_correlation_id()

        for attempt in range(2):
            try:
                resp = httpx.get(url, timeout=self.timeout, headers={"X-Request-ID": cid})

            except httpx.ConnectError:
                if attempt == 0:
                    continue
                throw_error("Loan service unreachable", 503)

            if resp.status_code in self.retry_status and attempt == 0:
                continue

            break

        if resp.status_code == 404:
            throw_error("Loan not found", 404)

        if resp.status_code != 200:
            throw_error("Loan Service Failure", 503)

        try:
            body = resp.json()
        except Exception:
            throw_error("Invalid JSON from Loan Service", 502)

        if "data" not in body:
            throw_error("Loan Service missing 'data' field", 502)

        return body["data"]

    # PUBLIC: GET LOAN (ASYNC)
    async def get_loan(self, loan_id: int, db: Optional[Session] = None) -> Dict[str, Any]:

        # DEV → Read from Dummy DB
        if settings.ENV.upper() == "DEV":
            if db is None:
                throw_error("DB session required in DEV mode", 500)

            loan = db.query(DummyLoan).filter(DummyLoan.id == loan_id).first()

            if not loan:
                throw_error("Loan not found in dummy DB", 404)

            return {
                "loan_id": loan.id,
                "borrower_name": loan.borrower_name,
                "loan_amount": loan.loan_amount,
                "loan_status": loan.loan_status,
            }

        # PROD → Real provider
        return await self._call_real_async(loan_id)

    # PUBLIC: GET LOAN (SYNC)
    def get_loan_sync(self, loan_id: int, db: Optional[Session] = None) -> Dict[str, Any]:

        # DEV → Read from Dummy DB
        if settings.ENV.upper() == "DEV":
            if db is None:
                throw_error("DB session required in DEV mode", 500)

            loan = db.query(DummyLoan).filter(DummyLoan.id == loan_id).first()

            if not loan:
                throw_error("Loan not found in dummy DB", 404)

            return {
                "loan_id": loan.id,
                "borrower_name": loan.borrower_name,
                "loan_amount": loan.loan_amount,
                "loan_status": loan.loan_status,
            }

        # PROD → Real provider
        return self._call_real_sync(loan_id)