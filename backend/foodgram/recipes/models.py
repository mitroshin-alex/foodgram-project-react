from colorfield.fields import ColorField
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Q, F
from django.core.validators import MinValueValidator

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиентов."""
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Имя ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Единица измерения ингредиента'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


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
        related_name='subscribers',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Пользователь'
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


class Recipe(models.Model):
    """Модель рецепта."""
    name = models.CharField(max_length=200, verbose_name='Название рецепта')
    text = models.TextField(null=False, verbose_name='Описание рецепта')
    cooking_time = models.PositiveIntegerField(
        null=False,
        verbose_name='Время приготовления',
        validators=(MinValueValidator(1),),
    )
    image = models.ImageField(
        verbose_name='Картинка рецепта',
        upload_to='recipes/',
        blank=False
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    tags = models.ManyToManyField(Tag, blank=False, related_name='tags')
    ingredients = models.ManyToManyField(
        Ingredient,
        blank=False,
        related_name='ingredients',
        through='IngredientAmount'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    """Модель связи для рецепта и ингредиентов
    с учетом количества в рецепте."""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    amount = models.PositiveIntegerField(
        null=False,
        verbose_name='Количество в рецепте',
        validators=(MinValueValidator(1),),
    )

    class Meta:
        unique_together = ('ingredient', 'recipe')
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self):
        return f'{self.recipe.name}-{self.ingredient.name}'


class Favorite(models.Model):
    """Модель избранных рецептов."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Избранное'
    )

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_favorite'),
        ]

    def __str__(self):
        return self.user.username + ' следит за ' + self.recipe.name


class ShoppingCart(models.Model):
    """Модель списка покупок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name='Рецепт'
    )

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Список покупки'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_shopping_cart'),
        ]
