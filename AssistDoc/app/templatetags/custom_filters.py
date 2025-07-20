from django import template
from datetime import date

register = template.Library()

@register.filter
def age(birth_date):
    """Calcule l'âge à partir de la date de naissance"""
    if birth_date:
        today = date.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return None
