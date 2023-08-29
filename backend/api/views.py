from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated)

from recipes.models import (Tag, Ingredient, Recipe,)

from users.models import User, Follow

from .pagination import CustomPagination
from .permissions import AuthorPermission
from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeSerializer, UserSerializer,
                          ShoppingListSerializer,)


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

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id):
        '''Для подписок.'''
        user = request.user
        author = get_object_or_404(User, pk=id)

        if request.method == 'POST':
            serializer = ShoppingListSerializer(
                author, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(
                Follow, user=user, author=author
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        '''Для списка покупок.'''
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = ShoppingListSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
