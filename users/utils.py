import io
import random
import re

from django import forms
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile

AVATAR_SIZE = 256
AVATAR_FONT_SIZE = 120
AVATAR_BG_COLORS = [
    '#4A90D9', '#E57373', '#81C784', '#FFB74D',
    '#BA68C8', '#4DB6AC', '#F06292', '#AED581',
]
AVATAR_FONT_PATHS = [
    '/System/Library/Fonts/Helvetica.ttc',
    '/System/Library/Fonts/HelveticaNeue.ttc',
    '/Library/Fonts/Arial.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
]


def validate_github_url(value):
    """Проверяет, что ссылка ведёт на github.com."""
    if value and 'github.com' not in value:
        raise forms.ValidationError('Ссылка должна вести на GitHub (github.com)')


def normalize_phone(phone, instance_pk=None):
    """
    Приводит номер к единому формату +7XXXXXXXXXX.
    Если передан instance_pk — исключает текущего пользователя из проверки уникальности.
    Импорт User делается локально, чтобы избежать циклических зависимостей.
    """
    from .models import User

    if not phone:
        return phone

    phone = re.sub(r'\D', '', phone)
    if phone.startswith('8'):
        phone = '+7' + phone[1:]
    elif phone.startswith('7'):
        phone = '+' + phone

    qs = User.objects.filter(phone=phone)
    if instance_pk is not None:
        qs = qs.exclude(pk=instance_pk)
    if qs.exists():
        raise forms.ValidationError('Пользователь с таким номером уже существует')

    return phone


def make_default_avatar(email, first_name):
    """Генерирует аватар: первая буква имени на цветном круге."""
    color = random.choice(AVATAR_BG_COLORS)

    img = Image.new('RGBA', (AVATAR_SIZE, AVATAR_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([0, 0, AVATAR_SIZE, AVATAR_SIZE], fill=color)

    letter = first_name[0].upper() if first_name else '?'

    font = None
    for path in AVATAR_FONT_PATHS:
        try:
            font = ImageFont.truetype(path, AVATAR_FONT_SIZE)
            break
        except OSError:
            continue

    if font is None:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), letter, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = (AVATAR_SIZE - w) / 2
    y = (AVATAR_SIZE - h) / 2 - bbox[1]

    draw.text((x, y), letter, fill='white', font=font)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    filename = f'{email.split("@")[0]}_avatar.png'
    return ContentFile(buf.read(), name=filename)