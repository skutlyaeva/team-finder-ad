from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm
from django.core.validators import RegexValidator
import re

from .models import User


# ──────────────────────────────────────────────
#  Валидаторы
# ──────────────────────────────────────────────

phone_validator = RegexValidator(
    regex=r'^(\+7|8)\d{10}$',
    message='Введите номер в формате 8XXXXXXXXXX или +7XXXXXXXXXX'
)


def validate_github_url(value):
    """Проверяет, что ссылка ведёт на github.com"""
    if value and 'github.com' not in value:
        raise forms.ValidationError('Ссылка должна вести на GitHub (github.com)')


# ──────────────────────────────────────────────
#  Регистрация
# ──────────────────────────────────────────────

class RegistrationForm(forms.ModelForm):
    """Форма создания нового пользователя"""
    
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form__input',
            'placeholder': 'Введите пароль'
        })
    )

    class Meta:
        model = User
        fields = ['name', 'surname', 'email']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form__input',
                'placeholder': 'Имя'
            }),
            'surname': forms.TextInput(attrs={
                'class': 'form__input',
                'placeholder': 'Фамилия'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form__input',
                'placeholder': 'Email'
            }),
        }
        labels = {
            'name': 'Имя',
            'surname': 'Фамилия',
            'email': 'Электронная почта',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


# ──────────────────────────────────────────────
#  Авторизация
# ──────────────────────────────────────────────

class AuthenticationForm(forms.Form):
    """Форма входа в систему"""
    
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form__input',
            'placeholder': 'Введите email'
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form__input',
            'placeholder': 'Введите пароль'
        })
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self._cached_user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get('email')
        password = cleaned.get('password')

        if email and password:
            self._cached_user = authenticate(
                self.request,
                username=email,
                password=password
            )
            if self._cached_user is None:
                raise forms.ValidationError('Неверный имейл или пароль')
            if not self._cached_user.is_active:
                raise forms.ValidationError('Учётная запись деактивирована')

        return cleaned

    def get_user(self):
        return self._cached_user


# ──────────────────────────────────────────────
#  Редактирование профиля
# ──────────────────────────────────────────────

class ProfileEditForm(forms.ModelForm):
    """Форма редактирования данных профиля"""
    
    phone = forms.CharField(
        label='Телефон',
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'class': 'form__input',
            'placeholder': '8XXXXXXXXXX или +7XXXXXXXXXX'
        })
    )
    github_url = forms.URLField(
        label='GitHub',
        required=False,
        validators=[validate_github_url],
        widget=forms.URLInput(attrs={
            'class': 'form__input',
            'placeholder': 'https://github.com/username'
        })
    )

    class Meta:
        model = User
        fields = ['name', 'surname', 'avatar', 'about', 'phone', 'github_url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form__input'}),
            'surname': forms.TextInput(attrs={'class': 'form__input'}),
            'about': forms.Textarea(attrs={
                'class': 'form__textarea',
                'rows': 4,
                'placeholder': 'Расскажите о себе'
            }),
        }
        labels = {
            'name': 'Имя',
            'surname': 'Фамилия',
            'avatar': 'Фото профиля',
            'about': 'О себе',
            'phone': 'Телефон',
            'github_url': 'Ссылка на GitHub',
        }

    def clean_phone(self):
        """Приводит номер к единому формату +7XXXXXXXXXX"""
        phone = self.cleaned_data.get('phone')
        if phone:
            phone = re.sub(r'\D', '', phone)
            if phone.startswith('8'):
                phone = '+7' + phone[1:]
            elif phone.startswith('7'):
                phone = '+' + phone
            # Проверка уникальности
            existing = User.objects.filter(phone=phone).exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError('Пользователь с таким номером уже существует')
        return phone


# ──────────────────────────────────────────────
#  Смена пароля
# ──────────────────────────────────────────────

class PasswordChangeForm(DjangoPasswordChangeForm):
    """Форма изменения пароля"""
    
    old_password = forms.CharField(
        label='Текущий пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form__input',
            'placeholder': 'Текущий пароль'
        })
    )
    new_password1 = forms.CharField(
        label='Новый пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form__input',
            'placeholder': 'Новый пароль'
        })
    )
    new_password2 = forms.CharField(
        label='Подтверждение',
        widget=forms.PasswordInput(attrs={
            'class': 'form__input',
            'placeholder': 'Повторите новый пароль'
        })
    )