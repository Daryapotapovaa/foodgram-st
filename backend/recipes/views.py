import csv
from rest_framework import viewsets
from rest_framework import permissions, status
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.http import HttpResponse
from .serializers import RecipeSerializer, IngredientSerializer, ShortRecipeSerializer
from .models import Recipe, Ingredient, IngredientInRecipe, Favorite, ShoppingCart
from api.permissions import IsAuthorOrReadOnly
from api.pagination import CustomPagination
from django.db.models import Sum



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
    pagination_class = CustomPagination
    permission_classes = [IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

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
                    {'error': 'Невозможно добавить рецепт второй раз'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(
                ShortRecipeSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )
        
        elif request.method == 'DELETE':
            instance = model.objects.filter(
                user=user,
                recipe=recipe
            )
            if instance.exists():
                instance.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

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
    
    def generate_shopping_cart_csv(self, ingredients):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.csv"'
        writer = csv.writer(response)
        writer.writerow(['Ингредиент', 'Единица измерения', 'Количество'])
        for item in ingredients:
            writer.writerow([
                item['ingredient__name'],
                item['ingredient__measurement_unit'],
                item['total_amount']
            ])
        return response
    
    @action(
        methods=['get'],
        detail=False,
        url_path='download_shopping_cart',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        user = request.user
        recipes = Recipe.objects.filter(shopping_cart__user=user)

        if not recipes.exists():
            return Response(
                    {'error': 'В списке покупок не найдены рецепты'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        ingredients = (
            IngredientInRecipe.objects
            .filter(recipe__in=recipes)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient__name')
        )

        return self.generate_shopping_cart_csv(ingredients)