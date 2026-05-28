from django.db import models
from django.conf import settings


class Project(models.Model):
    """Модель проекта"""

    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        CLOSED = 'closed', 'Closed'

    name = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects',
        verbose_name='Автор'
    )
    github_url = models.URLField('Ссылка на GitHub', blank=True)
    status = models.CharField(
        'Статус',
        max_length=6,
        choices=Status.choices,
        default=Status.OPEN
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='participated_projects',
        verbose_name='Участники'
    )

    class Meta:
        verbose_name = 'проект'
        verbose_name_plural = 'проекты'
        ordering = ['-created_at']

    def __str__(self):
        return self.name