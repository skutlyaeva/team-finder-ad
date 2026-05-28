from django import forms

from .models import Project
from .utils import validate_github_url


class ProjectForm(forms.ModelForm):
    """Форма создания и редактирования проекта."""

    github_url = forms.URLField(
        label='Ссылка на GitHub',
        required=False,
        validators=[validate_github_url],
        widget=forms.URLInput(attrs={
            'class': 'form__input',
            'placeholder': 'https://github.com/...',
        }),
    )

    class Meta:
        model = Project
        fields = ['name', 'description', 'github_url', 'status']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form__input',
                'placeholder': 'Название проекта',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form__textarea',
                'rows': 6,
                'placeholder': 'Опишите проект',
            }),
            'status': forms.Select(attrs={
                'class': 'form__select',
            }),
        }
        labels = {
            'name': 'Название',
            'description': 'Описание',
            'github_url': 'GitHub',
            'status': 'Статус',
        }