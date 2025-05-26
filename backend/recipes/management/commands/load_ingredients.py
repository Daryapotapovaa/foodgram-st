import json
from django.core.management.base import BaseCommand
from recipes.models import Ingredient
from django.db.utils import IntegrityError


class Command(BaseCommand):
    help = 'Загрузка ингредиентов из ingredients.json'

    def handle(self, *args, **kwargs):
        try:
            with open('api/preload_data/ingredients.json', encoding='utf-8') as file:
                ingredients = [
                    Ingredient(**item) for item in json.load(file)
                ]

            created = Ingredient.objects.bulk_create(
                ingredients, ignore_conflicts=True
            )

            self.stdout.write(self.style.SUCCESS(
                f'Загружено {len(created)} новых ингредиентов.'
            ))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(
                'Файл ingredients.json не найден.'
            ))
        except json.JSONDecodeError:
            self.stderr.write(self.style.ERROR(
                'Ошибка при чтении JSON-файла.'
            ))
        except IntegrityError as e:
            self.stderr.write(self.style.ERROR(
                f'Ошибка базы данных: {e}'
            ))
        except Exception as e:
            self.stderr.write(self.style.ERROR(
                f'Непредвиденная ошибка: {e}'
            ))
