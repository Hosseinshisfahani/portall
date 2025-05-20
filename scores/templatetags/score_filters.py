from django import template
from django.db.models import Avg

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def avg_score(scores):
    """Calculate average score for a list of scores"""
    if not scores:
        return 0
    return sum(score.score for score in scores) / len(scores) 