from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from recipes.models import (Favorites, Recipe, RecipeIngredient,
                            ShoppingList,)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,)
from rest_framework.response import Response

from .serializers import (FavoritesSerializer, ShoppingListSerializer,)


class RecipeViewSet(viewsets.ModelViewSet):
    ...

    @staticmethod
    def send_message(ingredients):
        '''Fормирует текстовый файл с покупками/'''
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
        '''Zагрузкa списка покупок/'''
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
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        '''Dобавляет рецепт в список покупок.'''
        recipe = get_object_or_404(Recipe, id=pk)
        return self.add_to_list(request, recipe, ShoppingListSerializer)

    @shopping_cart.mapping.delete
    def destroy_shopping_cart(self, request, pk):
        '''удаляет рецепт из списка покупок.'''
        get_object_or_404(
            ShoppingList,
            user=request.user.id,
            recipe=get_object_or_404(Recipe, id=pk)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('POST',),
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        '''Добавляет рецепт в избранное.'''
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