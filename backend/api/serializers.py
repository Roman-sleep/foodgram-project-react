from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import SerializerMethodField

from recipes.models import (
    Favorites,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    Tag
)

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    '''Сериализатор модели User.'''
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'password')

    def get_is_subscribed(self, obj):
        '''Проверка подписки.'''

        user = self.context.get("request").user

        return user.is_authenticated and \
            user.subscriptions.filter(author=obj).exists()

    def create(self, validated_data):
        '''Создание нового User.'''

        user = User(
            email=validated_data["email"],
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


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


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ''' Сериализатор связи ингредиентов и рецепта. '''
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    unit = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'unit',)


class RecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор модели Recipe.'''

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(max_length=None)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'autor', 'ingredients', 'title', 'image',
                  'cooking_time', 'is_favorited', 'is_in_shopping_cart',
                  'description')

    def get_ingredients(self, obj):
        '''Cписок ингридиентов для рецепта.'''
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def validate_cooking_time(self, cooking_time):
        if cooking_time < 1:
            raise serializers.ValidationError(
                'Время готовки должно быть не меньше одной минуты')
        return cooking_time

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.favorites.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.shopping_list.filter(user=request.user).exists()

    def create(self, validated_data):
        '''Создание рецепта.'''
        request = self.context.get('request', None)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        '''Редактирование рецепта.'''
        instance.tags.clear()
        RecipeIngredient.objects.filter(recipe=instance).delete()
        instance.tags.set(validated_data.pop('tags'))
        ingredients = validated_data.pop('ingredients')
        self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)


class FavoritesSerializer(serializers.ModelSerializer):
    '''Сериализатор модели Favorites.'''
    class Meta:
        model = Favorites
        fields = ('user', 'recipe')

    def validate(self, data):
        self.check_duplicate(data['user'], data['recipe'])
        return data

    def to_representation(self, instance):
        return RecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data

    @staticmethod
    def check_duplicate(user, recipe):
        if user.favorites.filter(recipe=recipe).exists():
            raise ValidationError(
                'Рецепт уже добавлен в избранное.'
            )


class ShoppingListSerializer(serializers.ModelSerializer):
    '''Сериализатор модели ShoppingList.'''
    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')

    def validate(self, data):
        self.check_duplicate(data['user'], data['recipe'])
        return data

    def to_representation(self, instance):
        return RecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data

    @staticmethod
    def check_duplicate(user, recipe):
        if user.shopping_list.filter(recipe=recipe).exists():
            raise ValidationError(
                'Рецепт уже добавлен в корзину'
            )
