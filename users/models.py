from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone

from .managers import UserManager
from .utils import make_default_avatar

NAME_MAX_LENGTH = 124
PHONE_MAX_LENGTH = 12
ABOUT_MAX_LENGTH = 256


class User(AbstractBaseUser, PermissionsMixin):
    """Кастомная модель пользователя с email вместо username."""

    email = models.EmailField('Электронная почта', unique=True)
    name = models.CharField('Имя', max_length=NAME_MAX_LENGTH)
    surname = models.CharField('Фамилия', max_length=NAME_MAX_LENGTH)

    avatar = models.ImageField('Фото профиля', upload_to='avatars/', blank=True)
    phone = models.CharField('Номер телефона', max_length=PHONE_MAX_LENGTH, blank=True)
    github_url = models.URLField('Ссылка на GitHub', blank=True)
    about = models.TextField('О пользователе', max_length=ABOUT_MAX_LENGTH, blank=True)

    date_joined = models.DateTimeField('Дата регистрации', default=timezone.now)
    is_active = models.BooleanField('Активен', default=True)
    is_staff = models.BooleanField('Персонал', default=False)

    favorites = models.ManyToManyField(
        'projects.Project',
        blank=True,
        related_name='interested_users',
        verbose_name='Избранные проекты',
    )

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
        """Автоматически создаёт аватар, если его нет."""
        if not self.avatar:
            self.avatar = make_default_avatar(self.email, self.name)
        super().save(*args, **kwargs)
