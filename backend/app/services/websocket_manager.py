import logging

from fastapi import WebSocket, WebSocketDisconnect


logger = logging.getLogger(__name__)


class SlideshowConnectionManager:
    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self._connections.discard(websocket)

    async def broadcast(self, event: dict[str, str]) -> None:
        stale_connections: list[WebSocket] = []
        for connection in tuple(self._connections):
            try:
                await connection.send_json(event)
            except (OSError, RuntimeError, WebSocketDisconnect):
                logger.info("Removing disconnected slideshow websocket client")
                stale_connections.append(connection)
        for connection in stale_connections:
            self.disconnect(connection)


slideshow_connections = SlideshowConnectionManager()


async def broadcast_slideshow_update() -> None:
    await slideshow_connections.broadcast({"type": "photos_updated"})
