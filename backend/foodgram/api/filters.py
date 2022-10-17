import django_filters as filters_dj

from recipes.models import Ingredient


class IngredientFilter(filters_dj.FilterSet):
    """Фильтр ингредиентов."""
    name = filters_dj.CharFilter(
        field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name', )
