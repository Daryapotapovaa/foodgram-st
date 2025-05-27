import json
from django.core.management.base import BaseCommand
from recipes.models import Ingredient
from django.db.utils import IntegrityError


class Command(BaseCommand):
    help = 'Загрузка ингредиентов из ingredients.json'

    def handle(self, *args, **kwargs):
        file_path = 'api/preload_data/ingredients.json'
        try:
            with open(file_path, encoding='utf-8') as file:
                created_ingredients = Ingredient.objects.bulk_create(
                    (Ingredient(**item) for item in json.load(file)),
                    ignore_conflicts=True
                )

            self.stdout.write(self.style.SUCCESS(
                f'Загружено {len(created_ingredients)} новых ингредиентов.'
            ))

        except Exception as e:
            self.stderr.write(self.style.ERROR(
                f'Непредвиденная ошибка: {file_path}: {e}'
            ))
