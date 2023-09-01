from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.models import (Favorites, Ingredient, Recipe,
                            RecipeIngredient, ShoppingList, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from users.models import Follow, User
from .pagination import CustomPagination
from .permissions import AuthorPermission
from .serializers import (FavoritesSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingListSerializer,
                          TagSerializer, UserSerializer)


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

    @staticmethod
    def send_message(ingredients):
        '''Fормирует текстовый файл с покупками.'''
        shopping_list = 'Купить в магазине:'
        for ingredient in ingredients:
            shopping_list += (
                f"\n{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) - "
                f"{ingredient['amount']}")
        file = 'shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{file}.txt"'
        return response

    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request):
        '''Zагрузкa списка покупок.'''
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_list__user=request.user
        ).order_by('ingredient__name').values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        return self.send_message(ingredients)

    @staticmethod
    def add_to_list(request, recipe, serializer_class):
        context = {'request': request}
        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        serializer = serializer_class(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=('POST',),
        permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        '''Dобавляет рецепт в список покупок.'''
        recipe = get_object_or_404(Recipe, id=pk)
        return self.add_to_list(request, recipe, ShoppingListSerializer)

    @shopping_cart.mapping.delete
    def destroy_shopping_cart(self, request, pk):
        '''Yдаляет рецепт из списка покупок.'''
        get_object_or_404(
            ShoppingList,
            user=request.user.id,
            recipe=get_object_or_404(Recipe, id=pk)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('POST',),
        permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        '''Dобавляет рецепт в избранное.'''
        recipe = get_object_or_404(Recipe, id=pk)
        return self.add_to_list(request, recipe, FavoritesSerializer)

    @favorite.mapping.delete
    def destroy_favorite(self, request, pk):
        '''Yдаляет рецепт из избранного.'''
        get_object_or_404(
            Favorites,
            user=request.user,
            recipe=get_object_or_404(Recipe, id=pk)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
            if Follow.objects.filter(user=user, author=author).exists():
                raise PermissionDenied('Вы уже подписаны на этого автора')

            serializer = UserSerializer(author, context={'request': request})
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        get_object_or_404(
            Follow, user=user, author=author
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        '''Для списка подписок.'''
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = UserSerializer(
            pages, many=True, context={'request': request}
        )

        return self.get_paginated_response(serializer.data)
