from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1 import admin, operator, tickets
from src.core.database import Base, SessionLocal, engine
from src.core.ws import manager

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Электронная очередь — backend-queue",
    version="1.0.0",
    description="Микросервис очереди (талоны, вызовы, табло).",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api/v1"

app.include_router(tickets.router, prefix=API_PREFIX)
app.include_router(operator.router, prefix=API_PREFIX)
app.include_router(admin.router, prefix=API_PREFIX)


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok", "service": "backend-queue"}


@app.websocket("/ws/queue")
async def queue_ws(websocket: WebSocket):
    from src.api.v1.tickets import queue_snapshot
    await manager.connect(websocket)
    db = SessionLocal()
    try:
        await websocket.send_json(
            {"type": "queue_update", "data": queue_snapshot(db)}
        )
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    finally:
        db.close()