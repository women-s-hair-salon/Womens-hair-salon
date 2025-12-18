# core/templatetags/custom_filters.py
from django import template
register = template.Library()

@register.filter
def to(start, end):
    """استفاده: 1300|to:1403 → range(1300, 1403+1)"""
    try:
        s = int(start)
        e = int(end)
        return range(s, e + 1)
    except Exception:
        return []
