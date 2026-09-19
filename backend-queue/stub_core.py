# Фейковый backend-core для локальной проверки backend-queue.

from fastapi import FastAPI, HTTPException

app = FastAPI(title="Stub backend-core")


SERVICES = {
    1: {"id": 1, "name": "Справки",     "prefix": "A", "avg_minutes": 5,  "is_active": True},
    2: {"id": 2, "name": "Платежи",     "prefix": "B", "avg_minutes": 3,  "is_active": True},
    3: {"id": 3, "name": "Консультация","prefix": "C", "avg_minutes": 10, "is_active": True},
}

WINDOWS = {
    1: {"id": 1, "number": 1, "title": "Окно 1", "is_active": True},
    2: {"id": 2, "number": 2, "title": "Окно 2", "is_active": True},
}


@app.get("/api/v1/services/{service_id}")
def get_service(service_id: int):
    s = SERVICES.get(service_id)
    if not s:
        raise HTTPException(404, "Услуга не найдена")
    return s


@app.get("/api/v1/windows/{window_id}")
def get_window(window_id: int):
    w = WINDOWS.get(window_id)
    if not w:
        raise HTTPException(404, "Окно не найдено")
    return w


@app.get("/health")
def health():
    return {"status": "ok", "stub": True}