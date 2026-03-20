# courses/templatetags/file_extras.py
from django import template

register = template.Library()

@register.filter
def is_image(value):
    """
    Returns True if the URL ends with a common image extension.
    """
    if not value:
        return False
    return any(value.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"])