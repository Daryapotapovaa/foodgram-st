from datetime import datetime

from rest_framework import viewsets
from rest_framework import permissions, status
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.http import Http404, FileResponse
from rest_framework.response import Response
from django.http import HttpResponse
from django.db.models import Sum
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend

from api.serializers.recipes import (RecipeSerializer, IngredientSerializer,
                          ShortRecipeSerializer)
from recipes.models import (Recipe, Ingredient, IngredientInRecipe,
                     Favorite, ShoppingCart)
from api.permissions import IsAuthorOrReadOnly
from api.pagination import LimitPageNumberPagination
from api.filters import RecipeFilter


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = None

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__startswith=name)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitPageNumberPagination
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['GET'],
        detail=True,
        url_path='get-link'
    )
    def get_short_link(self, request, pk=None):
        if not Recipe.objects.filter(pk=pk).exists():
            raise Http404
        
        short_url = request.build_absolute_uri(
            reverse("short-link", args=[pk])
        )
        return Response({"short-link": short_url})

    def _handle_recipe_action(self, request, recipe_id, model):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=recipe_id)

        if request.method == 'POST':
            obj, created = model.objects.get_or_create(
                user=user,
                recipe=recipe
            )

            if not created:
                return Response(
                    {'error': f'Невозможно добавить рецепт с id={recipe_id} второй раз'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response(
                ShortRecipeSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )
        
        get_object_or_404(
            model,
            user=user,
            recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
        url_path='favorite'
    )
    def favorite(self, request, pk=None):
        return self._handle_recipe_action(request, pk, Favorite)

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
        url_path='shopping_cart'
    )
    def shopping_cart(self, request, pk=None):
        return self._handle_recipe_action(request, pk, ShoppingCart)

    def generate_shopping_cart_csv(self, ingredients, recipes, user):
        current_date = datetime.now().strftime("%d.%m.%Y %H:%M")
    
        content = [
            f"Фудграм - Список покупок | {current_date}",
            f"Пользователь: {user.username}\n",
            "Ингредиенты:"
        ]
        
        for i, item in enumerate(ingredients, 1):
            content.append(
                f"{i}. {item['ingredient__name'].title()} - "
                f"{item['total_amount']} "
                f"{item['ingredient__measurement_unit']}"
            )
        
        content.extend([
            "\nРецепты:",
            *[f"- {recipe.name} (автор: {recipe.author.get_full_name()})" 
            for recipe in recipes.distinct()],
            f"\n© Foodgram {datetime.now().year}"
        ])
        
        return FileResponse(
            ("\n".join(content)),
            as_attachment=True,
            filename="shopping_list.txt",
            content_type="text/plain; charset=utf-8",
        )

    @action(
        methods=['GET'],
        detail=False,
        url_path='download_shopping_cart',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        user = request.user
        recipes = Recipe.objects.filter(shoppingcarts__user=user)

        # if not recipes.exists():
        #     return Response(
        #         {'error': 'В списке покупок не найдены рецепты'},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )

        ingredients = (
            IngredientInRecipe.objects
            .filter(recipe__in=recipes)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient__name')
        )

        return self.generate_shopping_cart_csv(ingredients, recipes, user)
