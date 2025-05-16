import json
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


User = get_user_model()


class Command(BaseCommand):
    help = 'Загрузка пользователей из users.json'

    def handle(self, *args, **kwargs):
        with open('api/preload_data/users.json', encoding='utf-8') as file:
            data = json.load(file)
            count = 0
            for item in data:
                obj, created = User.objects.get_or_create(
                    username=item['username'],
                    email=item['email'],
                    first_name=item['first_name'],
                    last_name=item['last_name'],
                    password=item['password']
                )
                if created:
                    count += 1
            self.stdout.write(self.style.SUCCESS(
                f'{count} пользователей загружено'))
