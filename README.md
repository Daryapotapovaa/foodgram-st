# Foodgram — Продуктовый помощник

**Foodgram** — это веб-приложение для публикации рецептов, добавления их в избранное и список покупок, а также подписки на авторов.

## Автор

**Потапова Дарья Максимовна**

🔗 [GitHub: Daryapotapovaa](https://github.com/Daryapotapovaa)

## 🛠️ Стек технологий

* Python 3.9
* Django 3.2
* Django REST Framework
* PostgreSQL
* Docker
* Docker Compose
* Nginx
* Gunicorn
* GitHub Actions

## Инструкция по запуску
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

Для загрузки предварительно созданных ингредиентов используйте команду:
```
docker-compose exec backend python manage.py load_ingredients
```
## Доступ к приложению

* Frontend: [http://localhost/](http://localhost/)
* Админка: [http://localhost/admin/](http://localhost/admin/)
* API: [http://localhost/api/docs/](http://localhost/api/docs/)
