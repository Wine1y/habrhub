# HabrHub
Небольшое Django-приложение, позволяющее периодически обходить выбранные хабы на [Хабре](https://habr.com/) и сохранять последние статьи.

## Настройки проекта (ENV)
- **DJANGO_SECRET_KEY** - Секретный ключ Django
- **CELERY_BROKER_URL** - URL брокера сообщений Celery (RabbitMQ/Redis)
- **DEBUG** - true/false для управления режимом отладки

## Инструкции по развёртыванию
1. Создать переменную среду Python (`python -m venv venv`)
2. Активировать переменную среду (`venv\scripts\activate` для Windows или (`source venv/bin/activate`) для Linux
3. Установить зависимости проекта (`pip install -r requirements.txt`)
4. Перейти в директорию src (`cd src`)
5. Применить миграции (`python manage.py migrate`)
6. Собрать static-файлы (`python manage.py collectstatic`)
7. Установить [ENV-настройки](#настройки-проекта-env) проекта (`SET NAME=VALUE` для Windows и `export NAME="VALUE"` для Linux)
8. Создать аккаунт администратора (`python manage.py createsuperuser`)
9. Запустить waitress-сервер проекта (`waitress-serve --host 127.0.0.1 habrhub.wsgi:application`)
10. Запустить Celery (`celery -A habrhub beat -l INFO`)
11. Запустить Celery-worker (`celery -A habrhub worker -l INFO`)

> Docker-образы доступны в разделе [Packages](https://github.com/Wine1y/habrhub/pkgs/container/habrhub)

## Использование
- На главной странице можно найти краткую статистику по добавленным хабам
- Хабами можно управлять через админ-панель Django (`/admin`)
- Список сохранённых статей также можно найти в админ панели