from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404

from .mixins import ListRetrieveViewSet, ListViewSet
from .serializers import (
    TagSerializer, IngredientSerializer, RecipeSerializer, FavoriteSerializer,
    SubscriptionSerializer
)
from .permissions import ReadOnly, IsAutherOrAdminOrReadOnly
from .filters import IngredientFilter, RecipeFilter
from .paginations import RecipePagination, SubscriptionPagination
from recipes.models import (
    Tag, Ingredient, Recipe, Favorite, User, Subscription
)


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
            permission_classes=(IsAuthenticated,), name='favorite')
    def favorite(self, request, pk):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = FavoriteSerializer(
            data=data,
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


class SubscriptionListViewSet(ListViewSet):
    """List для подписок на пользователей."""
    permission_classes = (IsAuthenticated,)
    serializer_class = SubscriptionSerializer
    pagination_class = SubscriptionPagination

    def get_queryset(self):
        return User.objects.filter(subscriptions__user=self.request.user)


class SubscribeView(APIView):
    """Post, delete для подписок на пользователей."""
    permission_classes = (IsAuthenticated,)
    serializer_class = SubscriptionSerializer
    pagination_class = None

    def post(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        author = get_object_or_404(User, pk=user_id)
        if Subscription.objects.filter(user=request.user, author=author
                                       ).exists():
            return Response({'errors': 'нельзя подписаться дважды'},
                            status=status.HTTP_400_BAD_REQUEST)
        if author == request.user:
            return Response({'errors': 'нельзя подписаться на себя'},
                            status=status.HTTP_400_BAD_REQUEST)

        Subscription.objects.create(
            user=request.user,
            author=author
        )

        return Response(
            self.serializer_class(author, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        author = get_object_or_404(User, pk=user_id)
        subscription = Subscription.objects.filter(
            user=request.user,
            author=author
        )
        if not subscription.exists():
            return Response({'errors': 'вы не были подписаны на автора'},
                            status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
