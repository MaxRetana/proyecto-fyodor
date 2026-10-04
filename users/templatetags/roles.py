from django import template

from ..roles import ROLE_LABELS, is_administrator

register = template.Library()


@register.filter(name='is_administrator')
def is_administrator_filter(user):
    return is_administrator(user)


@register.filter
def role_label(group):
    return ROLE_LABELS.get(group.name, group.name)
