from django.contrib.auth.mixins import UserPassesTestMixin
from kavenegar import *

import logging
from django.conf import settings
from kavenegar import KavenegarAPI, APIException, HTTPException

from datetime import datetime
from django.utils import timezone
import pytz

def make_tehran_aware(dt):
    tz = timezone.get_default_timezone()   # از settings.TIME_ZONE
    if timezone.is_naive(dt):
        return timezone.make_aware(dt, tz)
    return timezone.localtime(dt, tz)


# utils/sms_otp.py (مثال)

logger = logging.getLogger(__name__)

def _normalize_ir_mobile(m: str) -> str:
    if not m: return ""
    m = m.strip().replace(" ", "").replace("-", "")
    if m.startswith("+98"): return "98" + m[3:]
    if m.startswith("0098"): return "98" + m[4:]
    if m.startswith("98"): return m
    if m.startswith("0"): return "98" + m[1:]
    if len(m) == 10 and m.startswith("9"): return "98" + m
    return m

def send_otp_code(phone_number: str, code: int) -> bool:
    """ارسال OTP با کاوه‌نگار – برمی‌گرداند True/False و خطا را لاگ می‌کند."""
    api_key = getattr(settings, "KAVENEGAR_API_KEY", "")
    sender  = getattr(settings, "KAVENEGAR_SENDER", "")
    if not api_key:
        logger.error("KAVENEGAR_API_KEY is missing; OTP not sent.")
        return False
    receptor = _normalize_ir_mobile(phone_number)
    try:
        api = KavenegarAPI(api_key)
        params = {"receptor": receptor, "message": f"{code} کد تایید شما"}
        if sender:
            params["sender"] = sender
        res = api.sms_send(params)
        logger.info("OTP sent to %s", receptor[-4:].rjust(len(receptor), "*"))
        return True
    except (APIException, HTTPException) as e:
        logger.warning("Kavenegar send failed: %s", e)
        return False
    except Exception as e:
        logger.exception("Unexpected error sending OTP: %s", e)
        return False



class IsAdminUserMixin(UserPassesTestMixin):
    def test_func(self):
        u = self.request.user
        return u.is_authenticated and (u.is_staff or u.is_superuser)

