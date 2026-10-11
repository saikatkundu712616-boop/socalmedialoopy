# posts/templatetags/post_extras.py
from django import template

register = template.Library()


@register.filter
def in_set(value, the_set):
    if not the_set:
        return False
    try:
        return value in the_set
    except TypeError:
        return False