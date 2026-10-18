"""Мелкие шаблонные фильтры для интерфейса."""

from django import template

register = template.Library()


@register.filter
def plural_uk(number, forms):
    """Украинские формы множественного числа.

    Использование: {{ count|plural_uk:"документ,документи,документів" }}
    Для 1 → «документ», для 2–4 → «документи», иначе — «документів».
    """
    try:
        value = abs(int(number))
    except (TypeError, ValueError):
        return forms.split(',')[-1].strip()

    one, few, many = [form.strip() for form in forms.split(',')]
    if value % 10 == 1 and value % 100 != 11:
        return one
    if 2 <= value % 10 <= 4 and not 12 <= value % 100 <= 14:
        return few
    return many
