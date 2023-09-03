from django import template


register = template.Library()


@register.simple_tag
def generate_values():
    return [22, 44, 66, 88]
