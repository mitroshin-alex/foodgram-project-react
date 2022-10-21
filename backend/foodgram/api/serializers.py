from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer

from .fields import Base64ImageField
from recipes.models import (
    Tag, Subscription, Ingredient, Recipe, IngredientAmount, Favorite, User
)


class UserRegistrationSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя."""
    id = serializers.ReadOnlyField()

    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')


class CustomUserSerializer(UserSerializer):
    """Сериализатор отображения пользователя."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        return is_subscribed(self, obj)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор отображения тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор отображения ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор отображения ингредиентов в рецепте."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для короткого представления рецептов."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранных рецептов."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeShortSerializer(
            instance.recipe, context=context).data


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(read_only=True)

    # is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    # def get_is_in_shopping_cart(self, obj):
    #     request = self.context.get('request')
    #     if not request or request.user.is_anonymous:
    #         return False
    #     return ShoppingCart.objects.filter(
    #         user=request.user, recipe=obj).exists()

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients', None)
        tags = self.initial_data.get('tags', None)
        ingredients_set = set()
        tags_obj = list()

        if ingredients is None:
            raise serializers.ValidationError({
                'ingredients': ["Обязательное поле."]
            })
        if tags is None:
            raise serializers.ValidationError({
                'tags': ["Обязательное поле."]
            })

        for ingredient in ingredients:
            if int(ingredient.get('amount')) <= 0:
                raise serializers.ValidationError({
                    'ingredients_amount': [
                        'Количество ингредиента должно быть больше нуля'
                    ]
                })
            ingredient_id = ingredient.get('id')
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError({
                    'ingredients_id': ['Ингредиент не существует']
                })
            if ingredient_id in ingredients_set:
                raise serializers.ValidationError({
                    'ingredients_id': [
                        'Ингредиент в рецепте не должен повторяться'
                    ]
                })
            ingredients_set.add(ingredient_id)

        for tag in tags:
            if not Tag.objects.filter(id=tag).exists():
                raise serializers.ValidationError({
                    'tags': ['Тег не существует']
                })
            tags_obj.append(Tag.objects.get(id=tag))

        data['ingredients'] = ingredients
        data['tags'] = tags_obj

        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            **validated_data
        )
        recipe.tags.add(*tags)
        self.create_ingredient_amount(recipe, ingredients)

        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        tags = self.initial_data.get('tags')
        instance.tags.add(*tags)

        IngredientAmount.objects.filter(recipe=instance).delete()
        self.create_ingredient_amount(
            instance,
            validated_data.get('ingredients')
        )

        instance.image = validated_data.get('image')
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.get('cooking_time')
        instance.save()

        return instance

    @staticmethod
    def get_ingredients(obj):
        queryset = IngredientAmount.objects.filter(recipe=obj)
        return IngredientAmountSerializer(queryset, many=True).data

    @staticmethod
    def create_ingredient_amount(instance, data):
        for ingredient in data:
            IngredientAmount.objects.create(
                recipe=instance,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок на пользователей."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return is_subscribed(self, obj)

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit', None)
        recipes = obj.recipes.all()
        context = {'request': request}
        if recipes_limit is not None:
            recipes = recipes[:int(recipes_limit)]
        return RecipeShortSerializer(
            instance=recipes, many=True, context=context
        ).data

    @staticmethod
    def get_recipes_count(obj):
        return obj.recipes.count()


def is_subscribed(self, obj):
    request = self.context.get('request')
    if not request or request.user.is_anonymous:
        return False
    return Subscription.objects.filter(
        user=self.context.get('request').user,
        author=obj
    ).exists()
