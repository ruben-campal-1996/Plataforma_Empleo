from django import template

register = template.Library()

@register.filter
def times(number):
    if number is None or not isinstance(number, int):
        return range(1, 2)  # Devuelve un rango mínimo (1 página) si number es None o no es entero
    return range(1, number + 1)  # Genera páginas desde 1 hasta total_pages