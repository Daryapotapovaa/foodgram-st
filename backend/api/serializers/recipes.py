from rest_framework import serializers
from api.serializers.users import UserSerializer
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (Ingredient, Recipe, IngredientInRecipe,
                     Favorite, ShoppingCart)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id', 'name', 'measurement_unit'
        )


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name',
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )
    amount = serializers.IntegerField(
        required=True,
        min_value=1
    )

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id', 'name', 'measurement_unit', 'amount'
        )
        read_only_fields = fields


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    image = Base64ImageField(required=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    ingredients = IngredientInRecipeSerializer(
        source='ingredients_in_recipe',
        many=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )
        read_only_fields = (
            'id', 'author', 'is_favorited', 'is_in_shopping_cart'
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['image'] = instance.image.url
        return representation

    def add_ingredients(self, recipe, ingredient_data):
        IngredientInRecipe.objects.bulk_create(
            [
                IngredientInRecipe(
                    recipe=recipe,
                    ingredient=ingredient['ingredient'],
                    amount=ingredient['amount']
                )
                for ingredient in ingredient_data
            ]
        )

    def create(self, validated_data):
        ingredient_data = validated_data.pop('ingredients_in_recipe')
        recipe = super().create(validated_data)
        self.add_ingredients(recipe, ingredient_data)
        return recipe

    def update(self, instance, validated_data):
        ingredient_data = validated_data.pop('ingredients_in_recipe')
        instance.ingredients_in_recipe.all().delete()
        self.add_ingredients(instance, ingredient_data)
        return super().update(instance, validated_data)

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Обязательное поле (минимум 1)'
            })

        image = self.initial_data.get('image')
        if not image:
            raise serializers.ValidationError({
                'image': 'Обязательное поле'
            })

        ingredient_ids = [ingredient.get('id') for ingredient in ingredients]

        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError({
                'ingredients': 'Ингредиенты не должны повторяться'
            })

        return data

    def get_is_favorited(self, recipe):
        request = self.context.get('request')
        return Favorite.objects.filter(
            user=request.user.id,
            recipe=recipe
        ).exists()

    def get_is_in_shopping_cart(self, recipe):
        request = self.context.get('request')
        return ShoppingCart.objects.filter(
            user=request.user.id,
            recipe=recipe
        ).exists()


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time'
        )
        read_only_fields = fields
