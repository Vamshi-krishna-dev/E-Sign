import httpx
from typing import Dict, Any
from app.core.config import settings
from app.core.exceptions import throw_error
from app.core.logger import logger
from app.middleware.correlation_id import get_correlation_id


class ProviderClient:
    """
    Low-level HTTP client for real eSign providers.
    Does NOT contain business logic or mock logic.
    """

    def __init__(self):
        self.base_url = settings.ESIGN_BASE_URL.rstrip("/")

        self.timeout = httpx.Timeout(
            connect=3.0,
            read=10.0,
            write=5.0,
            pool=5.0,
        )

        self.retry_statuses = {502, 503, 504}

    def _headers(self):
        cid = get_correlation_id()
        return {
            "X-API-Key": settings.ESIGN_API_KEY,
            "X-Client-Secret": settings.ESIGN_CLIENT_SECRET,
            "X-Request-ID": cid,
            "Content-Type": "application/json"
        }

    async def _post(self, path: str, payload: dict):
        url = f"{self.base_url}/{path.lstrip('/')}"

        for attempt in range(2):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.post(url, json=payload, headers=self._headers())
            except httpx.ConnectError:
                if attempt == 0:
                    continue
                throw_error("eSign provider unreachable", 503)

            if resp.status_code in self.retry_statuses and attempt == 0:
                continue

            break

        if resp.status_code != 200:
            logger.error(f"[Provider ERROR] status={resp.status_code}, url={url}")
            throw_error("Provider API error", 503)

        try:
            return resp.json()
        except Exception:
            throw_error("Invalid JSON from provider", 502)

    async def _get(self, path: str):
        url = f"{self.base_url}/{path.lstrip('/')}"

        for attempt in range(2):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.get(url, headers=self._headers())
            except httpx.ConnectError:
                if attempt == 0:
                    continue
                throw_error("Provider unreachable", 503)

            if resp.status_code in self.retry_statuses and attempt == 0:
                continue

            break

        if resp.status_code != 200:
            throw_error("Provider fetch failed", 503)

        try:
            return resp.json()
        except Exception:
            throw_error("Invalid JSON from provider", 502)

           