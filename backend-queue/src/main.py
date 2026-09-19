from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1 import algorithm, events
from src.core.ws import manager

app = FastAPI(
    title="Электронная очередь — Queue Feature",
    version="2.0.0",
    description=(
        "Stateless-сервис алгоритма очереди. "
        "Источник истины — backend-core. БД у сервиса нет."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api/v1"
app.include_router(algorithm.router, prefix=API_PREFIX)
app.include_router(events.router, prefix=API_PREFIX)


@app.get("/health", tags=["system"])
def health():
    return {
        "status": "ok",
        "service": "backend-queue",
        "role": "algorithm",
        "db": "none",
        "ws_clients": len(manager.active),
    }


@app.websocket("/ws/queue")
async def queue_ws(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)