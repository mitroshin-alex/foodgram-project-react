from django.contrib import admin

from .models import (
    Ingredient, Tag, Subscription, Recipe, IngredientAmount, Favorite,
    ShoppingCart
)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name', )


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('name', 'slug')


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    search_fields = ('user',)


class RecipeInlineAdmin(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1

    def get_queryset(self, request):
        return super(RecipeInlineAdmin, self).get_queryset(request)


class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeInlineAdmin, ]
    list_display = ('pk', 'name', 'text', 'cooking_time',
                    'image', 'author', 'pub_date')
    filter_horizontal = ('tags', 'ingredients')
    search_fields = ('user',)


class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = ('pk', 'ingredient', 'recipe', 'amount')


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')


admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(IngredientAmount, IngredientAmountAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
