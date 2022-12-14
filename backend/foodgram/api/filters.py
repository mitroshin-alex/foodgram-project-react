import django_filters

from recipes.models import Recipe, Ingredient, Tag


class IngredientFilter(django_filters.FilterSet):
    """Фильтр ингредиентов."""
    name = django_filters.CharFilter(
        field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name', )


class RecipeFilter(django_filters.FilterSet):
    """Фильтр рецептов."""
    author = django_filters.NumberFilter(field_name='author__id')
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )
    is_favorited = django_filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        """Переопределение фильтрации по избранным рецептам,
        если 1 то фильтруется."""
        if value == 1:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Переопределение фильтрации по рецептам в списке покупок,
        если 1 то фильтруется."""
        if value == 1:
            return queryset.filter(carts__user=self.request.user)
        return queryset
