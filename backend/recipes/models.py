from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.core.validators import MinValueValidator


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='Почта',
        max_length=254,
        unique=True
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=(r"^[\w.@+-]+$"),
                message=(
                    "Имя пользователя может содержать только буквы, "
                    "цифры и знаки @/./+/-/_"
                ),
                code="invalid_username",
            )
        ],
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=False
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=False
    )
    avatar = models.ImageField(
        verbose_name='Аватарка',
        upload_to='users/images/',
        default=None,
        null=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name="Подписчик"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authors',
        verbose_name="Подписан на"
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('follower',)
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'author'],
                name='unique follower author in subscription'
            )
        ]

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
        ordering = ('name',)
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="unique ingredient",
            )
        ]


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
        related_name='recipes',
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

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_in_recipe',
        verbose_name="Рецепт"
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients_in_recipe',
        verbose_name="Ингредиенты рецепта"
    )
    amount = models.PositiveIntegerField(
        verbose_name="Колчиество",
        validators=[MinValueValidator(1)]
    )


class UserRecipeRelation(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="%(class)ss",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="%(class)ss",
    )

    class Meta:
        abstract = True
        ordering = ("user", "recipe")
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_%(class)s"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.recipe}"


class Favorite(UserRecipeRelation):

    class Meta(UserRecipeRelation.Meta):
        verbose_name = 'Избранное',
        verbose_name_plural = 'Избранные'


class ShoppingCart(UserRecipeRelation):

    class Meta(UserRecipeRelation.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
