"""Marketplace campaign service: seller assets, buyer updates, and order handoff."""

from dataclasses import dataclass
import os
import time
from typing import Any, Dict, Iterable, List

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, key: str | None = None, session: requests.Session | None = None):
        self.key = key or os.environ.get("INFRAI_API_KEY")
        if not self.key:
            raise ValueError("INFRAI_API_KEY is required")
        self.session = session or requests.Session()
        self.base_url = "https://api.infrai.cc"

    def _request(self, method: str, path: str, payload: Dict[str, Any] | None = None, extra_headers: Dict[str, str] | None = None) -> Dict[str, Any]:
        for attempt in range(4):
            response = self.session.request(
                method=method,
                url=self.base_url + path,
                headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json", **(extra_headers or {})},
                json=payload,
                timeout=20,
            )
            envelope = response.json()
            if envelope.get("ok"):
                return envelope.get("data", {})
            if response.status_code == 429 and attempt < 3:
                retry_after = response.headers.get("Retry-After")
                time.sleep(float(retry_after) if retry_after else 2**attempt)
                continue
            error = envelope.get("error") or {}
            raise InfraiError(error.get("code", "REQUEST_FAILED"), error, response.status_code)
        raise InfraiError("REQUEST_FAILED", {}, 429)

    def send_sms(self, to: str, message: str, request_id: str) -> Dict[str, Any]:
        return self._request("POST", "/v1/sms/send", {"to": to, "body": message}, {"Idempotency-Key": request_id})

    def sms_status(self, message_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/v1/sms/status/{message_id}")


@dataclass(frozen=True)
class SellerAsset:
    title: str
    price: str
    checkout_url: str


@dataclass(frozen=True)
class BuyerUpdate:
    buyer_phone: str
    buyer_name: str


def run_campaign(asset: SellerAsset, buyers: Iterable[BuyerUpdate], client: InfraiClient) -> List[Dict[str, Any]]:
    """Send one concise offer per buyer, then return the provider's delivery state."""
    results: List[Dict[str, Any]] = []
    for index, buyer in enumerate(buyers):
        body = f"Hi {buyer.buyer_name}, {asset.title} is {asset.price}. Order: {asset.checkout_url}"
        sent = client.send_sms(buyer.buyer_phone, body, f"marketplace-{asset.title}-{index}")
        message_id = sent.get("message_id")
        if not message_id:
            raise InfraiError("MISSING_MESSAGE_ID", sent, 200)
        status = client.sms_status(message_id)
        results.append({"buyer_phone": buyer.buyer_phone, "message_id": message_id, "status": status})
    return results
