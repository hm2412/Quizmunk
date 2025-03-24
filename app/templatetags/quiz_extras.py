# app/templatetags/quiz_extras.py
from django import template
from app.question_registry import QUESTION_MODELS

register = template.Library()

@register.filter
def get_question_type(question):
    """Return the key for the question type based on its model."""
    for key, model in QUESTION_MODELS.items():
        if isinstance(question, model):
            return key
    return ""
