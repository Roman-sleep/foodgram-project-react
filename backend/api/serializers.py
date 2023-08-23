from recipes.models import (Tag, Ingredient, Recipe,
                            Favorites, ShoppingList)
from users.models import User
from rest_framework.serializers import SerializerMethodField
from rest_framework.exceptions import ValidationError


class UserSerializer(UserSerializer):
    '''Сериализатор модели User.'''
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', )


class TagSerializer(serializers.ModelSerializer):
    '''Сериализатор модели Tag.'''
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color_code', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    '''Сериализатор модели Ingredient.'''
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'quantity')


class RecipeReadSerializer(serializers.ModelSerializer):
    '''Сериализатор модели Recipe.'''
    class Meta:
        model = Recipe
        fields = ('id', 'title', 'image', 'cooking_time')


class FavoritesSerializer(serializers.ModelSerializer):
    '''Сериализатор модели Favorites.'''
    class Meta:
        model = Favorites
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        if user.favorites.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное.'
            )
        return data

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class ShoppingListSerializer(serializers.ModelSerializer):
    '''Сериализатор модели ShoppingList.'''
    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        if user.shopping_list.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в корзину'
            )
        return data

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
