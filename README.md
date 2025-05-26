# Инструкция по запуску
### Склонируйте репозиторий
```
git clone https://github.com/Daryapotapovaa/foodgram-st.git
cd foodgram-st
```

### В корне проекта создать .env файл. В нем должны быть:
```
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_NAME=foodgram
DB_HOST=db
DB_PORT=5432
SECRET_KEY = 'django-insecure-example-key'
DEBUG = False
ALLOWED_HOSTS=127.0.0.1,localhost
```
### Запуск
В папке infra:
```
docker-compose up
```
Выполните миграции и создайте суперпользователя
```
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --no-input
docker-compose exec backend python manage.py createsuperuser
```
### Загрузка подготовленных данных

Для загрузки предварительно созданных пользователей, ингредиентов и рецептов используйте команды:
```
docker-compose exec backend python manage.py load_ingredients
docker-compose exec backend python manage.py load_users
docker-compose exec backend python manage.py load_recipes
```

