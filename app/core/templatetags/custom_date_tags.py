from django import template

from app.search.utils.date import format_partial_date_govuk

register = template.Library()


@register.filter
def format_partial_date(date_str):
    return format_partial_date_govuk(date_str)
