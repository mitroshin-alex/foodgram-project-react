from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from recipes.models import (
    Tag, Ingredient, Recipe, Favorite, User, Subscription, ShoppingCart,
    IngredientAmount
)
from .filters import IngredientFilter, RecipeFilter
from .mixins import ListRetrieveViewSet, ListViewSet
from .paginations import RecipePagination, SubscriptionPagination
from .permissions import ReadOnly, IsAutherOrAdminOrReadOnly
from .serializers import (
    TagSerializer, IngredientSerializer, RecipeSerializer, FavoriteSerializer,
    SubscriptionSerializer, ShoppingCartSerializer
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
    """CRUD для рецептов, добавление рецепта в избранное и список покупок,
    загрузка списка покупок."""
    queryset = Recipe.objects.all()
    permission_classes = (IsAutherOrAdminOrReadOnly,)
    serializer_class = RecipeSerializer
    pagination_class = RecipePagination
    filterset_class = RecipeFilter

    @action(detail=True, methods=['post'],
            permission_classes=(IsAuthenticated,), name='favorite')
    def favorite(self, request, pk):
        return self.create_obj(FavoriteSerializer, pk, request)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_obj(Favorite, pk, request, 'избранном')

    @action(detail=True, methods=['post'],
            permission_classes=(IsAuthenticated,), name='shopping_cart')
    def shopping_cart(self, request, pk):
        return self.create_obj(ShoppingCartSerializer, pk, request)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_obj(ShoppingCart, pk, request, 'списке покупок')

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,),
            name='download_shopping_cart')
    def download_shopping_cart(self, request, pk=None):
        shopping_cart = {}
        content = 'Выш список покупок \n\n'
        ingredients = IngredientAmount.objects.filter(
            recipe__carts__user=request.user).values_list(
            'ingredient__name', 'amount', 'ingredient__measurement_unit'
        )
        for ingredient in ingredients:
            name = ingredient[0]
            amount = ingredient[1]
            unit = ingredient[2]
            if name in shopping_cart:
                shopping_cart[name]['amount'] += amount
            else:
                shopping_cart[name] = {'unit': unit, 'amount': amount}

        for i, (ingredient, data) in enumerate(shopping_cart.items(), 1):
            content += (f'{i}) {ingredient} ({data["unit"]}) '
                        f'— {data["amount"]}\n')
        response = HttpResponse(content, content_type='text/plain')
        response[
            'Content-Disposition'
        ] = 'attachment; filename="shopping_cart.txt"'

        return response

    @staticmethod
    def create_obj(serializer_class, pk, request):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializer_class(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_obj(obj_class, pk, request, message):
        obj = obj_class.objects.filter(user_id=request.user.id, recipe_id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': f'рецепт не в {message}'},
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
