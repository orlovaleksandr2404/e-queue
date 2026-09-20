# Сервис электронной очереди (E-Queue)

## Быстрый запуск

### 1. Подготовка окружения
Скопируйте пример файла переменных окружения в корень проекта:
```bash
cp .env.example .env
```
### 2. Сборка и запуск контейнеров
Запустите все 5 микросервисов (backend-core, backend-queue, frontend, postgres, redis):

```bash
docker compose up -d --build
```
остановка контейнеров:
```bash
docker compose down
```
Полная остановка с удалением базы данных и сбросом томов (Volume):
```bash
docker compose down -v
```
### 3. Применение миграций и наполнение демо-данными
Дождитесь запуска базы данных и выполните:

```bash
# Применение миграций базы данных
docker compose exec backend-core alembic upgrade head

# Загрузка тестовых данных (организации, услуги, окна, пользователи)
docker compose exec backend-core python seed.py
```
## Интерфейсы и ссылки
После запуска все интерфейсы доступны в браузере:

- Терминал выбора услуг - http://localhost:5173/terminal
- Информационное табло - http://localhost:5173/board
- Рабочее место оператора - http://localhost:5173/operator
- Панель администратора - http://localhost:5173/admin
- Swagger UI (Core API) - http://localhost:8000/docs
- Swagger UI (Queue API) - http://localhost:8001/docs

## Тестовые учетные записи
Администратор

- Логин: admin
- Пароль: adminpassword

Оператор

- Логин: operator1
- Пароль: secretpassword

## Запуск автотестов
```bash
# Тесты ядра (авторизация, RBAC, жизненный цикл талонов, окна, услуги):
docker compose exec backend-core pytest

# Тесты сервиса очередей (алгоритм подбора талонов, валидация событий):
docker compose exec backend-queue pytest
```

