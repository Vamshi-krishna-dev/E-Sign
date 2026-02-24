import httpx
from typing import Optional, Dict
from app.core.config import settings
from app.core.exceptions import throw_error
from app.middleware.correlation_id import get_correlation_id


class LoanClient:
    """
    Loan client for talking to the Loan Service microservice.
    Includes async + sync variants, retry logic, CID propagation, and strong error handling.
    """

    def __init__(self):
        self.base_url = settings.LOAN_SERVICE_BASE_URL.rstrip("/")  # from .env

        # Timeouts
        self.timeout = httpx.Timeout(
            connect=2.0,
            read=5.0,
            write=5.0,
            pool=5.0
        )

        # Retry strategy
        self.retry_statuses = {502, 503, 504}

    # ASYNC VERSION
    async def get_loan(self, loan_id: int) -> Dict:
        url = f"{self.base_url}/{loan_id}"

        cid = get_correlation_id()

        for attempt in range(2):  # 1 retry
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.get(
                        url,
                        headers={"X-Request-ID": cid}
                    )
            except httpx.ConnectError:
                if attempt == 0:
                    continue
                throw_error("Loan service unreachable", 503)
            except Exception as exc:
                throw_error(f"Loan service error: {exc}", 503)

            # Retry only on server issues
            if resp.status_code in self.retry_statuses and attempt == 0:
                continue

            break

        if resp.status_code == 404:
            throw_error("Loan not found", 404)

        if resp.status_code != 200:
            throw_error("Loan service failed", 503)

        body = resp.json()

        if "data" not in body:
            throw_error("Invalid response from loan service", 502)

        return body["data"]

    # SYNC VERSION (for services)
    def get_loan_sync(self, loan_id: int) -> Dict:
        url = f"{self.base_url}/{loan_id}"

        cid = get_correlation_id()

        for attempt in range(2):  # 1 retry
            try:
                resp = httpx.get(
                    url,
                    timeout=self.timeout,
                    headers={"X-Request-ID": cid}
                )
            except httpx.ConnectError:
                if attempt == 0:
                    continue
                throw_error("Loan service unreachable", 503)
            except Exception as exc:
                throw_error(f"Loan service error: {exc}", 503)

            if resp.status_code in self.retry_statuses and attempt == 0:
                continue

            break

        if resp.status_code == 404:
            throw_error("Loan not found", 404)

        if resp.status_code != 200:
            throw_error("Loan service failed", 503)

        try:
            body = resp.json()
        except Exception:
            throw_error("Invalid JSON from Loan Service", 502)

        if "data" not in body:
            throw_error("Loan Service missing 'data' field", 502)

        return body["data"]