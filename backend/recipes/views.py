from django.shortcuts import redirect
from django.http import Http404

from .models import Recipe


def redirect_short_link(request, recipe_id):
    if not Recipe.objects.filter(id=recipe_id).exists():
        raise Http404(f"Рецепт c id={recipe_id} не найден")

    return redirect(f"/recipes/{recipe_id}/")