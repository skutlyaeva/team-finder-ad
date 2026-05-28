from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
import io
import random
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile


class UserManager(BaseUserManager):
    """Менеджер для кастомной модели пользователя"""
    
    def _create_user(self, email, name, surname, password, **extra):
        if not email:
            raise ValueError('Поле email должно быть заполнено')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, surname=surname, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, name, surname, password=None, **extra):
        extra.setdefault('is_active', True)
        return self._create_user(email, name, surname, password, **extra)

    def create_superuser(self, email, name, surname, password=None, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        extra.setdefault('is_active', True)
        return self._create_user(email, name, surname, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    """Кастомная модель пользователя с email вместо username"""
    
    # Основные поля
    email = models.EmailField('Электронная почта', unique=True)
    name = models.CharField('Имя', max_length=124)
    surname = models.CharField('Фамилия', max_length=124)
    
    # Профиль
    avatar = models.ImageField('Фото профиля', upload_to='avatars/', blank=True)
    phone = models.CharField('Номер телефона', max_length=12, blank=True)
    github_url = models.URLField('Ссылка на GitHub', blank=True)
    about = models.TextField('О пользователе', max_length=256, blank=True)
    
    # Служебные поля
    date_joined = models.DateTimeField('Дата регистрации', default=timezone.now)
    is_active = models.BooleanField('Активен', default=True)
    is_staff = models.BooleanField('Персонал', default=False)
    
    # Связи
    favorites = models.ManyToManyField(
        'projects.Project',
        blank=True,
        related_name='interested_users',
        verbose_name='Избранные проекты'
    )

    # Настройки для аутентификации
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    objects = UserManager()

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ['-date_joined']

    def __str__(self):
        return f'{self.name} {self.surname}'

    def save(self, *args, **kwargs):
        """Автоматически создает аватар, если его нет"""
        if not self.avatar:
            self.avatar = self._make_default_avatar()
        super().save(*args, **kwargs)

    def _make_default_avatar(self):
        """Генерирует аватар: первая буква имени на цветном круге"""
        size = 256
        bg_colors = [
            '#4A90D9', '#E57373', '#81C784', '#FFB74D',
            '#BA68C8', '#4DB6AC', '#F06292', '#AED581'
        ]
        color = random.choice(bg_colors)
        
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse([0, 0, size, size], fill=color)
        
        letter = self.name[0].upper() if self.name else '?'
        
        font = None
        font_paths = [
            '/System/Library/Fonts/Helvetica.ttc',
            '/System/Library/Fonts/HelveticaNeue.ttc',
            '/Library/Fonts/Arial.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        ]
        
        for path in font_paths:
            try:
                font = ImageFont.truetype(path, 120)
                break
            except:
                continue
        
        if font is None:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), letter, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x = (size - w) / 2
        y = (size - h) / 2 - bbox[1]
        
        draw.text((x, y), letter, fill='white', font=font)
        
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        
        return ContentFile(buf.read(), name=f'{self.email.split("@")[0]}_avatar.png')