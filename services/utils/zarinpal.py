# services/utils/zarinpal.py
import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import uuid

PROD_API_BASE = "https://api.zarinpal.com/pg/v4/payment/"
PROD_STARTPAY = "https://www.zarinpal.com/pg/StartPay/"

class ZarinpalGateway:
    def __init__(self, merchant_id=None, callback_url=None, timeout=15):
        self.sandbox = bool(getattr(settings, "ZARINPAL_SANDBOX", False))
        self.merchant_id = merchant_id or getattr(settings, "ZARINPAL_MERCHANT_ID", "")
        self.callback_url = callback_url or getattr(settings, "ZARINPAL_CALLBACK_URL", "")
        self.timeout = timeout

        if not self.sandbox and not self.merchant_id:
            raise ImproperlyConfigured(
                "ZARINPAL_MERCHANT_ID is required when ZARINPAL_SANDBOX is False."
            )

    @staticmethod
    def _toman_to_rial(amount_toman: int) -> int:
        return int(amount_toman) * 10

    def startpay_url(self, authority: str) -> str:
        return f"{PROD_STARTPAY}{authority}"

    def request_payment(self, amount_toman: int, description: str, metadata: dict):
        # ✅ SANDBOX: Authority یکتا و دقیقاً 36 کاراکتر
        if self.sandbox:
            # "TEST-" (5 کاراکتر) + 31 کاراکتر از uuid → 36
            return f"TEST-{uuid.uuid4().hex[:31].upper()}"

        payload = {
            "merchant_id": self.merchant_id,
            "amount": self._toman_to_rial(amount_toman),
            "description": (description or "")[:500],
            "callback_url": self.callback_url,
            "metadata": metadata or {},
        }
        r = requests.post(PROD_API_BASE + "request.json", json=payload, timeout=self.timeout)

        # به جای raise_for_status، اول JSON را بخوانیم تا خطای دقیق را بدهیم
        try:
            data = r.json()
        except Exception:
            r.raise_for_status()  # اگر JSON نبود، بگذار همون HTTPError بیاد

        if 200 <= r.status_code < 300 and data.get("data") and data["data"].get("authority"):
            return data["data"]["authority"]

        # خطای معنادار
        raise ValueError({
            "http_status": r.status_code,
            "errors": data.get("errors") or data
        })

    def verify_payment(self, authority: str, amount_toman: int):
        if self.sandbox:
            # تست: همیشه موفق + ref_id ساختگی
            return True, f"SANDBOX-{uuid.uuid4().hex[:10].upper()}"

        payload = {
            "merchant_id": self.merchant_id,
            "amount": self._toman_to_rial(amount_toman),
            "authority": authority,
        }
        r = requests.post(PROD_API_BASE + "verify.json", json=payload, timeout=self.timeout)
        try:
            data = r.json()
        except Exception:
            r.raise_for_status()

        if 200 <= r.status_code < 300 and data.get("data") and data["data"].get("code") == 100:
            return True, data["data"].get("ref_id")
        return False, {"http_status": r.status_code, "errors": data.get("errors") or data}
