import re
import jdatetime
from datetime import date as gdate ,datetime

_PERSIAN_DIGITS = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
_ARABIC_DIGITS  = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')

def _normalize_digits(s: str) -> str:
    return s.translate(_PERSIAN_DIGITS).translate(_ARABIC_DIGITS)

def parse_jalali_to_gregorian(jstr: str) -> gdate:
    """
    قبول: 1404/06/12 یا 1404-06-12 با اعداد فارسی/عربی/انگلیسی
    """
    if not jstr:
        raise ValueError("تاریخ جلالی خالی است.")
    s = _normalize_digits(jstr.strip()).replace('-', '/')
    m = re.match(r'^(\d{4})/(\d{1,2})/(\d{1,2})$', s)
    if not m:
        raise ValueError("فرمت تاریخ جلالی معتبر نیست. مثل 1404/06/12")
    jy, jm, jd = map(int, m.groups())
    return jdatetime.date(jy, jm, jd).togregorian()

def gregorian_to_jalali_str(value) -> str:
    """
    value می‌تواند datetime.date / datetime.datetime / 'YYYY-MM-DD' باشد.
    خروجی: 'YYYY/MM/DD' جلالی
    """
    if isinstance(value, datetime):
        value = value.date()
    elif isinstance(value, str):
        y, m, d = [int(x) for x in value.split('-')]
        value = gdate(y, m, d)
    jd = jdatetime.date.fromgregorian(date=value)
    return jd.strftime('%Y/%m/%d')
