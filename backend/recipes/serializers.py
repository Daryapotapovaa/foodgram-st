from rest_framework import serializers
from users.serializers import CustomUserSerializer
from drf_extra_fields.fields import Base64ImageField
from .models import Ingredient, Recipe, IngredientInRecipe


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id', 'name', 'measurement_unit'
        )


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name',
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id', 'name', 'measurement_unit', 'amount'
        )


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(required=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    ingredients = IngredientInRecipeSerializer(
        source='ingredient_in_recipe',
        many=True,
        read_only=True
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
        for ingredient in ingredient_data:
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            )

    def create(self, validated_data):
        ingredient_data = validated_data.pop('ingredient_in_recipe')
        recipe = Recipe.objects.create(**validated_data)
        self.add_ingredients(recipe, ingredient_data)
        return recipe

    def update(self, instance, validated_data):
        ingredient_data = validated_data.pop('ingredient_in_recipe', None)
        
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.image = validated_data.get('image', instance.image) or ""
        if ingredient_data:
            instance.ingredient_in_recipe.all().delete()
            self.add_ingredients(instance, ingredient_data)

        instance.save()
        return instance

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
        
        for ingredient in ingredients:
            amount = int(ingredient.get('amount'))
            if amount <= 0:
                raise serializers.ValidationError({
                    'ingredients': 'Количество ингредиента должно быть больше нуля'
                })
            
        data['ingredient_in_recipe'] = ingredients
        return data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return False #Заглушка

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return False #Заглушка

