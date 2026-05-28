from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Менеджер для кастомной модели пользователя."""

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