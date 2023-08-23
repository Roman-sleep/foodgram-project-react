from djoser.views import UserViewSet
from rest_framework import viewsets
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        )

from recipes.models import (Tag, Ingredient, Recipe,)

from users.models import User

from .pagination import CustomPagination
from .permissions import AuthorPermission
from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeSerializer, UserSerializer,)


class TagViewSet(viewsets.ModelViewSet):
    '''Работа с Tag.'''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''Работа с Ingredient.'''
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, )
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    '''Работа с Recipe.'''
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AuthorPermission, )
    pagination_class = CustomPagination


class UserViewSet(UserViewSet):
    '''Работа с User.'''
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination
