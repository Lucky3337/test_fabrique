# Тестовое задание для fabrique

API - система опросов пользователей. Написанная на django 2.2.10 и Django Rest framework.

## Управление сервисом

Для запуска сервиса необходимо сбилдить и запустить докер контейнеры.

* Билд и запуск сервиса

```bash
docker-compose up --build
```

* Создание нового администратора сервиса

```bash
docker container exec -it fabrique-django python manage.py createsuperuser
```

* Остановка сервиса

```bash
docker-compose down
```

## Документация API сервиса

После успешного запуска сервиса можно посмотреть документацию к API. [Ссылка](http://localhost:8010/openapi/) на документацию. 