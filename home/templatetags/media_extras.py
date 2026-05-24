from django import template
import re

register = template.Library()

_YT = re.compile(r'(?:youtube\.com/watch\?v=|youtu\.be/)([\w\-]{6,})', re.I)
_VM = re.compile(r'vimeo\.com/(?:video/)?(\d+)', re.I)

@register.filter
def embed_url(url: str) -> str:
    """
    اگر یوتیوب/ویمئو بود، URL امبد برمی‌گرداند؛
    در غیر این صورت همان URL را (برای <video> مستقیم) برمی‌گرداند.
    """
    if not url:
        return ""
    m = _YT.search(url)
    if m:
        return f"https://www.youtube.com/embed/{m.group(1)}"
    m = _VM.search(url)
    if m:
        return f"https://player.vimeo.com/video/{m.group(1)}"
    return url
