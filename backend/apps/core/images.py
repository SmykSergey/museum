"""Генерация уменьшенных копий изображений.

Карточки списков показывают фото размером ~250–400 px, а исходники бывают
по 0.9 МБ. Отдавать полноразмерные файлы в списке из 500 героев — это десятки
мегабайт трафика, поэтому для каждого фото делается миниатюра.
"""

from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image, ImageFile, ImageOps

# в архиве есть слегка обрезанные файлы — не падаем на них
ImageFile.LOAD_TRUNCATED_IMAGES = True


def _flatten(img):
    """Прозрачность переносим на белый фон: JPEG не умеет альфа-канал."""
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        img = img.convert('RGBA')
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[-1])
        return background
    if img.mode != 'RGB':
        return img.convert('RGB')
    return img


def make_thumbnail(file_field, max_size=400, quality=80):
    """Возвращает ContentFile с уменьшенной копией изображения.

    Вписывает картинку в квадрат max_size × max_size, сохраняя пропорции.
    """
    with Image.open(file_field) as img:
        img = ImageOps.exif_transpose(img)
        img = _flatten(img)
        img.thumbnail((max_size, max_size), Image.LANCZOS)

        buffer = BytesIO()
        img.save(
            buffer, format='JPEG', quality=quality, optimize=True, progressive=True,
        )

    return ContentFile(buffer.getvalue())


def thumbnail_filename(image_name):
    """heroes/x/1.png → 1.jpg (миниатюра всегда JPEG)."""
    return Path(image_name).stem + '.jpg'
