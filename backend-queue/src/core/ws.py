from fastapi import WebSocket


class ConnectionManager:

    def __init__(self) -> None:
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket) -> None:
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, message: dict) -> int:
        dead: list[WebSocket] = []
        delivered = 0
        for ws in self.active:
            try:
                await ws.send_json(message)
                delivered += 1
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)
        return delivered


manager = ConnectionManager()