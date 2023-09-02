from django.contrib import admin
from .models import (Tag, Ingredient, Recipe,
                     Favorites, ShoppingList)


class TagAdmin(admin.ModelAdmin):
    """Управление тегами в админ панели."""
    list_display = ('name', 'color_code', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name', )


class IngredientAdmin(admin.ModelAdmin):
    """Управление ингридиентами в админ панели."""
    list_display = ('name', 'quantity')
    search_fields = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'title', 'cooking_time',
                    'favorites_count', 'ingredients_count')
    search_fields = ('author', 'title', 'tags__name',
                     'favorites_count', 'ingredients_count')
    list_filter = ('tags', 'favorites_count', 'ingredients_count')


class FavoritesAdmin(admin.ModelAdmin):
    """Управление подписками в админ панели."""
    list_display = ('recipe', 'user')
    list_filter = ('recipe', 'user')
    search_fields = ('recipe', 'user')


class ShoppingListAdmin(admin.ModelAdmin):
    """Управление списком покупок в админ панели."""
    list_display = ('recipe', 'user')
    list_filter = ('recipe', 'user')
    search_fields = ('user', )


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorites, FavoritesAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
