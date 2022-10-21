from rest_framework.pagination import PageNumberPagination


class RecipePagination(PageNumberPagination):
    """Пагинатор для рецептов."""
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 1000


class SubscriptionPagination(PageNumberPagination):
    """Пагинатор для подписок."""
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 1000
