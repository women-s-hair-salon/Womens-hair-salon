# services/utils/sms.py
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

KAVENEGAR_BASE = "https://api.kavenegar.com/v1/{api_key}/sms/send.json"

def _normalize_ir_mobile(m: str) -> str:
    if not m:
        return ""
    m = m.strip().replace(" ", "").replace("-", "")
    if m.startswith("+98"): return "98" + m[3:]
    if m.startswith("0098"): return "98" + m[4:]
    if m.startswith("98"): return m
    if m.startswith("0"): return "98" + m[1:]
    if len(m) == 10 and m.startswith("9"): return "98" + m
    return m

def _format_date_fa(gregorian_date) -> str:
    try:
        import jdatetime
        jd = jdatetime.date.fromgregorian(date=gregorian_date)
        months = ["فروردین","اردیبهشت","خرداد","تیر","مرداد","شهریور",
                  "مهر","آبان","آذر","دی","بهمن","اسفند"]
        return f"{jd.day} {months[jd.month-1]} {jd.year}"
    except Exception:
        return gregorian_date.isoformat()

def _safe_name(user) -> str:
    # از full_name پراپرتی شما استفاده می‌کنیم، وگرنه فیلدها
    name = getattr(user, "full_name", None)
    if callable(name): name = name()  # در صورت متد بودن
    if not name:
        name = f"{getattr(user,'first_name','').strip()} {getattr(user,'last_name','').strip()}".strip()
    return name or "بدون‌نام"

def _short_res_id(reservation) -> str:
    # آی‌دی کوتاه برای اشاره‌ی سریع در پیامک
    return f"R{reservation.id}"

def send_sms(receptor: str, message: str, sender: str | None = None) -> bool:
    api_key = getattr(settings, "KAVENEGAR_API_KEY", "")
    if not api_key:
        logger.warning("Kavenegar API key is not set; SMS skipped.")
        return False

    url = KAVENEGAR_BASE.format(api_key=api_key)
    payload = {
        "receptor": _normalize_ir_mobile(receptor),
        "message": message.strip(),
    }
    s = sender or getattr(settings, "KAVENEGAR_SENDER", "")
    if s:
        payload["sender"] = s

    try:
        r = requests.post(url, data=payload, timeout=10)
        data = {}
        try:
            if r.headers.get("content-type","").startswith("application/json"):
                data = r.json()
        except Exception:
            pass
        ok_flag = (200 <= r.status_code < 300)
        kav_ok = str(data.get("return", {}).get("status")) in ("200", "success")
        if ok_flag and (not data or kav_ok):
            return True
        logger.error("Kavenegar send failed: status=%s body=%s", r.status_code, data or r.text)
        return False
    except Exception as e:
        logger.exception("Kavenegar send exception: %s", e)
        return False

def send_bulk_sms(receptors: list[str], message: str) -> None:
    for rec in receptors:
        send_sms(rec, message)

def sms_text_for_admin(reservation) -> str:
    salon = getattr(settings, "SALON_NAME", "سیندخت بیوتی")
    svc   = reservation.service.title
    date  = _format_date_fa(reservation.slot.date)
    st    = reservation.slot.start_time.strftime("%H:%M")
    en    = reservation.slot.end_time.strftime("%H:%M")
    name  = _safe_name(reservation.user)
    mob   = getattr(reservation.user, "phone_number", "")  # الزامی است، پس همیشه پر است
    rid   = _short_res_id(reservation)
    ref   = reservation.zarinpal_ref_id or ""  # فقط اگر هست، اضافه می‌کنیم

    text = (
        f"{salon}\n"
        f"رزرو جدید ✅ {rid}\n"
        f"{svc}\n"
        f"{date} | {st} تا {en}\n"
        f"مشتری: {name}\n"
        f"موبایل: {mob}"
    )
    if ref:
        text += f"\nرهگیری زرین‌پال: {ref}"
    return text


def sms_text_for_user(reservation) -> str:
    salon = getattr(settings, "SALON_NAME", "سیندخت بیوتی")
    phone = getattr(settings, "SALON_PHONE", "")
    svc   = reservation.service.title
    date  = _format_date_fa(reservation.slot.date)
    st    = reservation.slot.start_time.strftime("%H:%M")
    en    = reservation.slot.end_time.strftime("%H:%M")
    rid   = _short_res_id(reservation)
    ref   = reservation.zarinpal_ref_id or "-"
    footer = f"\nتماس: {phone}" if phone else ""
    return (
        f"{salon}\n"
        f"پرداخت موفق ✅ {rid}\n"
        f"{svc}\n"
        f"{date} | {st} تا {en}\n"
        f"رهگیری: {ref}{footer}"
    )

def notify_after_booking(reservation) -> None:
    # Admin(s)
    admins_raw = getattr(settings, "ADMIN_MOBILE", "")
    admin_list = [a.strip() for a in admins_raw.split(",") if a.strip()]
    if admin_list:
        send_bulk_sms(admin_list, sms_text_for_admin(reservation))
    # User
    user_mobile = getattr(reservation.user, "phone_number", "")
    if user_mobile:
        send_sms(user_mobile, sms_text_for_user(reservation))
