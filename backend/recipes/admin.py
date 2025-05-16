from django.contrib import admin
from .models import (Recipe, Ingredient, IngredientInRecipe,
                     Favorite, ShoppingCart)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name', )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'count_favorites')
    search_fields = ('name', 'author__username')
    list_filter = ('author', 'name')

    def count_favorites(self, obj):
        return obj.favorites.count()


admin.site.register(IngredientInRecipe)
admin.site.register(ShoppingCart)
admin.site.register(Favorite)
