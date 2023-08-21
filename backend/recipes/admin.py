from django.contrib import admin
from .models import (Tag, Ingredient, Recipe,
                     )


class TagAdmin(admin.ModelAdmin):
    """Управление тегами в админ панели."""
    list_display = ('name', 'color_code', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name', )


class IngredientAdmin(admin.ModelAdmin):
    """Управление ингридиентами в админ панели."""
    list_display = ('name', 'quantity')
    search_fields = ('name', )
    list_filter = ('name', )


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'cooking_time')
    search_fields = ('name', 'author', 'tags')
    list_filter = ('author', 'name', 'tags')


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
