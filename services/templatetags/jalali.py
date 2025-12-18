# services/templatetags/jalali.py
from django import template
import jdatetime
from datetime import date, datetime

register = template.Library()

def _to_greg_parts(v):
    if isinstance(v, (date, datetime)):
        d = v.date() if isinstance(v, datetime) else v
        return d.year, d.month, d.day
    if isinstance(v, str):
        y, m, d = [int(x) for x in v.split('-')]
        return y, m, d
    raise ValueError("Unsupported date type")

@register.filter
def to_jalali_date(value):
    if not value:
        return ''
    try:
        y, m, d = _to_greg_parts(value)
        jd = jdatetime.date.fromgregorian(day=d, month=m, year=y)
        return jd.strftime('%Y/%m/%d')
    except Exception:
        return value

@register.filter
def persian_weekday(value):
    if not value:
        return ''
    try:
        y, m, d = _to_greg_parts(value)
        jd = jdatetime.date.fromgregorian(day=d, month=m, year=y)
        # 1=Mon ... 7=Sun  → نام‌های فارسی
        names = {1:'دوشنبه', 2:'سه‌شنبه', 3:'چهارشنبه', 4:'پنجشنبه', 5:'جمعه', 6:'شنبه', 7:'یکشنبه'}
        return names.get(jd.isoweekday(), '')
    except Exception:
        return ''
