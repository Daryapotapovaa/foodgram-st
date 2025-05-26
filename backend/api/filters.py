from django_filters import rest_framework as filters
from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    author = filters.NumberFilter(
        field_name='author__id'
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ["author", "is_favorited", "is_in_shopping_cart"]

    def filter_is_favorited(self, recipes, name, value):
        if value and self.request.user.is_authenticated:
            return recipes.filter(
                favorites__user=self.request.user
            )
        return recipes

    def filter_is_in_shopping_cart(self, recipes, name, value):
        if value and self.request.user.is_authenticated:
            return recipes.filter(
                shoppingcarts__user=self.request.user
            )
        return recipes
