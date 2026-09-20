import logging

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self.active.append(ws)
        logger.info("ws connected: total=%d", len(self.active))

    def disconnect(self, ws: WebSocket) -> None:
        if ws in self.active:
            self.active.remove(ws)
            logger.info("ws disconnected: total=%d", len(self.active))

    async def broadcast(self, message: dict) -> int:
        dead: list[WebSocket] = []
        delivered = 0
        for ws in self.active:
            try:
                await ws.send_json(message)
                delivered += 1
            except Exception as e:
                logger.warning("ws send failed: %s", e)
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)
        return delivered


manager = ConnectionManager()