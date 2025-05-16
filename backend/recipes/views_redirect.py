from django.shortcuts import redirect
from django.http import Http404
from .models import Recipe


def redirect_short_link(request, recipe_id):
    if not Recipe.objects.filter(id=recipe_id).exists():
        raise Http404("Рецепт не найден")

    return redirect(f"/api/recipes/{recipe_id}/")
