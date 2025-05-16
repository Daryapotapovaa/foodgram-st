from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator


User = get_user_model()

class Ingredient(models.Model):
    name = models.CharField(
        max_length=128,
        unique=True,
        verbose_name="Название ингредиента"
    )
    measurement_unit = models.CharField(
        max_length=64,
        verbose_name="Единица измерения"
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name="Название"
    )
    text = models.TextField(
        verbose_name="Описание"
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name="Фото"
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name="Ингредиенты"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name="Автор"
    )
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Время приготовления"
    )
    is_favorited = models.BooleanField(
        default=False,
        verbose_name="В избранном"
    )
    is_in_shopping_cart = models.BooleanField(
        default=False,
        verbose_name="В корзине"
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_in_recipe',
        verbose_name="Рецепт"
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиенты рецепта"
    )
    amount = models.PositiveIntegerField(
        verbose_name="Колчиество",
        validators=[MinValueValidator(1)]
    )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name="Рецепт"
    )

    class Meta:
        verbose_name = 'Избранное',
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique user recipe in Favorite'
            )
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name="Рецепт"
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique user recipe in ShoppingCart'
            )
        ]