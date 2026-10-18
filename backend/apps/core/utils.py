"""Общие утилиты для приложений проекта."""

from django.utils.text import slugify

# Украинский алфавит в порядке сортировки. Нужен, потому что PostgreSQL
# сортирует кириллицу по байтам, а не по алфавиту: і, ї, є, ґ встают не на место.
UA_ALPHABET = 'АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ'

# Символы, которые в украинской коллации идут раньше букв
_UA_SEPARATORS = " '’ʼ-–—"

# Транслитерация по постановлению КМУ № 55 (2010) — чтобы адреса страниц
# получались латиницей автоматически из украинских названий.
_UA_TRANSLIT = {
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'H', 'Ґ': 'G', 'Д': 'D', 'Е': 'E',
    'Ж': 'Zh', 'З': 'Z', 'И': 'Y', 'І': 'I', 'К': 'K', 'Л': 'L', 'М': 'M',
    'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
    'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch',
    'Ь': '',
}
# В начале слова эти буквы читаются иначе, чем в середине
_UA_TRANSLIT_START = {'Є': 'Ye', 'Ї': 'Yi', 'Й': 'Y', 'Ю': 'Yu', 'Я': 'Ya'}
_UA_TRANSLIT_MIDDLE = {'Є': 'ie', 'Ї': 'i', 'Й': 'i', 'Ю': 'iu', 'Я': 'ia'}
# Апостроф в адресе не нужен
_UA_SKIP = "'’ʼ"

_WORD_BOUNDARY = ' -\t\n\r–—'


def transliterate_uk(text):
    """«Шевченко Тарас» → «Shevchenko Taras»."""
    if not text:
        return ''
    parts = []
    at_word_start = True
    for char in text:
        upper = char.upper()
        if upper in _UA_TRANSLIT or upper in _UA_TRANSLIT_START:
            table = _UA_TRANSLIT_START if at_word_start else _UA_TRANSLIT_MIDDLE
            value = table.get(upper) or _UA_TRANSLIT.get(upper, '')
            # «Шевченко» → «Shevchenko», а не «ShEVChENKO»
            parts.append(value.lower() if char.islower() else value)
            at_word_start = False
        elif char in _UA_SKIP:
            continue
        else:
            parts.append(char)
            if char in _WORD_BOUNDARY:
                at_word_start = True
    return ''.join(parts)


def make_sort_key(name):
    """Строка, по которой PostgreSQL сортирует имена правильно по-украински.

    Каждая буква заменяется на её двузначный номер в украинском алфавите,
    разделители — на '00' (идут раньше букв), всё остальное — на '99'.
    """
    if not name:
        return ''
    parts = []
    for char in name.upper():
        index = UA_ALPHABET.find(char)
        if index >= 0:
            parts.append('%02d' % index)
        elif char in _UA_SEPARATORS:
            parts.append('00')
        else:
            parts.append('99')
    return ''.join(parts)


def unique_slug(instance, value, field='slug', max_length=200):
    """Подбирает свободный slug: 'kovalenko', 'kovalenko-2', 'kovalenko-3'..."""
    Model = type(instance)
    manager = Model._default_manager
    value = value[:max_length]

    if not manager.filter(**{field: value}).exclude(pk=instance.pk).exists():
        return value

    counter = 2
    while manager.filter(**{field: '%s-%s' % (value, counter)}).exclude(pk=instance.pk).exists():
        counter += 1
    return '%s-%s' % (value, counter)


def transliterated_slug(instance, text, field='slug', max_length=200):
    """slug из украинского текста: транслитерация + подбор свободного имени."""
    base = slugify(transliterate_uk(text))[:max_length]
    if not base:
        return ''
    return unique_slug(instance, base, field=field, max_length=max_length)
