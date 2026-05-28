from django import forms


def validate_github_url(value):
    """Проверяет, что ссылка ведёт на github.com."""
    if value and 'github.com' not in value:
        raise forms.ValidationError('Ссылка должна быть на GitHub (github.com)')