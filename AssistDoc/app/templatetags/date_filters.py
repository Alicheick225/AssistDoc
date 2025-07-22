# your_app/templatetags/date_filters.py

from django import template
from datetime import date

register = template.Library()

@register.filter
def age(value):
    if not value:
        return ""
    today = date.today()
    return today.year - value.year - ((today.month, today.day) < (value.month, value.day))
