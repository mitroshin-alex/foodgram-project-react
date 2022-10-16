from colorfield.fields import ColorField
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Q, F

User = get_user_model()


class Tag(models.Model):
    """Модель тегов."""
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Имя тега'
    )
    color = ColorField(
        null=True,
        verbose_name='Цвет тега'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Короткое название тега'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.slug


class Subscription(models.Model):
    """Модель подписок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписки'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Подписчики'
    )

    class Meta:
        unique_together = ('user', 'author')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_following'),
            models.CheckConstraint(check=~Q(user_id=F('author_id')),
                                   name='not_following_self',),
        ]

    def __str__(self):
        return self.user.username + ' подписан на ' + self.author.username