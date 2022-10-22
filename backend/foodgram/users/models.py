from django.contrib.auth.models import (AbstractUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator


class UserManager(BaseUserManager):
    """Собственная модель пользователя."""

    def create_user(self, email, username, first_name, last_name, password):
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username,
                         first_name, last_name, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser, PermissionsMixin):
    """Собственная модель пользователя."""

    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Email адрес'
    )

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=(UnicodeUsernameValidator(),),
        verbose_name='Имя пользователя'
    )

    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя'
    )

    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия'
    )

    password = models.CharField(
        max_length=150,
        verbose_name='Пароль'
    )

    is_active = models.BooleanField(
        default=True, verbose_name='Активна'
    )

    is_staff = models.BooleanField(
        default=False,
        verbose_name='Персонал'
    )

    is_superuser = models.BooleanField(
        default=False,
        verbose_name='Суперпользователь'
    )

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ('email', 'first_name', 'last_name', 'password')

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
