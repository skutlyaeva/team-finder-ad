from django import forms
from django.core.validators import URLValidator
from .models import Project


def check_github_link(url):
    """Проверка, что ссылка ведёт на GitHub"""
    if url and 'github.com' not in url:
        raise forms.ValidationError('Ссылка должна быть на GitHub (github.com)')


class ProjectForm(forms.ModelForm):
    """Форма создания и редактирования проекта"""

    github_url = forms.URLField(
        label='Ссылка на GitHub',
        required=False,
        validators=[check_github_link],
        widget=forms.URLInput(attrs={
            'class': 'form__input',
            'placeholder': 'https://github.com/...'
        })
    )

    class Meta:
        model = Project
        fields = ['name', 'description', 'github_url', 'status']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form__input',
                'placeholder': 'Название проекта'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form__textarea',
                'rows': 6,
                'placeholder': 'Опишите проект'
            }),
            'status': forms.Select(attrs={
                'class': 'form__select'
            }),
        }
        labels = {
            'name': 'Название',
            'description': 'Описание',
            'github_url': 'GitHub',
            'status': 'Статус',
        }