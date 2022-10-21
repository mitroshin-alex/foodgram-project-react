from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .mixins import ListRetrieveViewSet
from .serializers import (
    TagSerializer, IngredientSerializer, RecipeSerializer, FavoriteSerializer,
)
from .permissions import ReadOnly, IsAutherOrAdminOrReadOnly
from .filters import IngredientFilter, RecipeFilter
from .paginations import RecipePagination
from recipes.models import Tag, Ingredient, Recipe, Favorite


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
    permission_classes = (IsAutherOrAdminOrReadOnly,)
    serializer_class = RecipeSerializer
    pagination_class = RecipePagination
    filterset_class = RecipeFilter

    @action(detail=True, methods=['post'],
            permission_classes=(IsAuthenticated, ), name='favorite')
    def favorite(self, request, pk):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = FavoriteSerializer(data=data,
                                        context={'request': request}
                                        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        favorite = Favorite.objects.filter(
            user_id=request.user.id, recipe_id=pk
        )
        if favorite.exists():
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'рецепт не в избранном'},
            status=status.HTTP_400_BAD_REQUEST)
