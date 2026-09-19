# backend-queue

Микросервис очереди: выдача талонов, вызовы оператором, табло реального времени, статистика.

## Что делает
- Хранит **только талоны** в собственной БД.
- За услугами/окнами ходит в `backend-core` по HTTP (с TTL-кэшем).
- **Денормализует** название услуги, префикс и номер окна в талон.
- Раздаёт WebSocket `/ws/queue` для табло.
- Проверяет JWT, подписанные общим `SECRET_KEY` с `backend-core`.

## Переменные окружения
| Переменная | Смысл |
|---|---|
| `SECRET_KEY` | Должен совпадать с backend-core |
| `DATABASE_URL` | По умолчанию `sqlite:///./queue.db` |
| `CORE_API_URL` | Адрес backend-core, напр. `http://backend-core:8000` |
| `CORE_TIMEOUT` | Таймаут HTTP-запросов, сек |
| `CORE_CACHE_TTL` | TTL кэша справочников, сек |

## Запуск
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

alembic revision --autogenerate -m "initial tickets"
alembic upgrade head
python -m seed

uvicorn src.main:app --reload --port 8001
```

Swagger: http://127.0.0.1:8001/docs

## Запуск обоих сервисов
```bash
docker compose up --build
```

## Эндпоинты
| Метод | URL | Назначение |
|---|---|---|
| POST | `/api/v1/tickets` | Взять талон |
| GET  | `/api/v1/tickets/{id}` | Статус + позиция + ETA |
| POST | `/api/v1/tickets/{id}/cancel` | Отменить |
| POST | `/api/v1/tickets/{id}/feedback` | Оценка 1–5 |
| POST | `/api/v1/operator/call-next?window_id=1` | Вызвать следующего |
| POST | `/api/v1/operator/tickets/{id}/start` | Начать |
| POST | `/api/v1/operator/tickets/{id}/finish` | Завершить |
| POST | `/api/v1/operator/tickets/{id}/no-show` | Не явился |
| GET  | `/api/v1/operator/queue` | Снимок очереди |
| GET  | `/api/v1/admin/stats?day=YYYY-MM-DD` | Статистика |
| WS   | `/ws/queue` | Табло реального времени |