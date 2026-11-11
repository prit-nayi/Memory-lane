from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.websocket_manager import slideshow_connections


router = APIRouter(tags=["slideshow"])


@router.websocket("/api/v1/slideshow/ws")
async def slideshow_websocket(websocket: WebSocket) -> None:
    await slideshow_connections.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        slideshow_connections.disconnect(websocket)
