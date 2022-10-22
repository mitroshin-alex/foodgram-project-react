from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    TagViewSet, IngredientViewSet, RecipeViewSet, SubscriptionListViewSet,
    SubscribeView
)

router_v1 = DefaultRouter()

router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('recipes', RecipeViewSet, basename='titles')
router_v1.register(
    'users/subscriptions', SubscriptionListViewSet, basename='subscriptions'
)

urlpatterns = [
    path(
        'users/<int:user_id>/subscribe/',
        SubscribeView.as_view(),
        name='subscribe'
    ),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
]
