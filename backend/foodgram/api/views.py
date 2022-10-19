from rest_framework import filters
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .mixins import ListRetrieveViewSet
from .serializers import (
    TagSerializer, IngredientSerializer, RecipeSerializer
)
from .permissions import ReadOnly
from .filters import IngredientFilter
from recipes.models import Tag, Ingredient, Recipe


class TagViewSet(ListRetrieveViewSet):
    """List, Retrieve для тегов."""
    permission_classes = (ReadOnly,)
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientViewSet(ListRetrieveViewSet):
    """List, Retrieve для ингредиентов."""
    permission_classes = (ReadOnly,)
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = RecipeSerializer
