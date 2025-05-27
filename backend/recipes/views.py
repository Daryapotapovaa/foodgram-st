from django.shortcuts import redirect
from django.core.exceptions import ValidationError

from .models import Recipe


def redirect_short_link(request, recipe_id):
    if not Recipe.objects.filter(id=recipe_id).exists():
        raise ValidationError(f"Рецепт c id={recipe_id} не найден")

    return redirect(f"/recipes/{recipe_id}/")