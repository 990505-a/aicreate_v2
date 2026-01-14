"""WebSocket handlers for real-time workflow updates."""

import json
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

router = APIRouter()


class ConnectionManager:
    """Manager for WebSocket connections."""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, execution_id: str, websocket: WebSocket):
        """Connect a WebSocket for execution updates."""
        await websocket.accept()

        if execution_id not in self.active_connections:
            self.active_connections[execution_id] = set()

        self.active_connections[execution_id].add(websocket)
        logger.info(f"WebSocket connected for execution {execution_id}")

    def disconnect(self, execution_id: str, websocket: WebSocket):
        """Disconnect a WebSocket."""
        if execution_id in self.active_connections:
            self.active_connections[execution_id].discard(websocket)

            if not self.active_connections[execution_id]:
                del self.active_connections[execution_id]

        logger.info(f"WebSocket disconnected for execution {execution_id}")

    async def broadcast_to_execution(self, execution_id: str, message: dict):
        """Broadcast message to all connections for an execution."""
        if execution_id not in self.active_connections:
            return

        message_json = json.dumps(message)

        for connection in self.active_connections[execution_id]:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error sending WebSocket message: {e}")
                self.disconnect(execution_id, connection)

    async def broadcast_to_all(self, message: dict):
        """Broadcast message to all active connections."""
        message_json = json.dumps(message)

        for execution_id, connections in self.active_connections.items():
            for connection in list(connections):
                try:
                    await connection.send_text(message_json)
                except Exception as e:
                    logger.error(f"Error sending WebSocket message: {e}")
                    self.disconnect(execution_id, connection)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/executions/{execution_id}/updates")
async def workflow_execution_updates(websocket: WebSocket, execution_id: str):
    """WebSocket endpoint for workflow execution updates."""
    await manager.connect(execution_id, websocket)

    try:
        # Keep connection alive
        while True:
            data = await websocket.receive_text()
            # Echo back or handle client messages if needed
            logger.debug(f"Received message for execution {execution_id}: {data}")

    except WebSocketDisconnect:
        manager.disconnect(execution_id, websocket)
        logger.info(f"WebSocket disconnected for execution {execution_id}")
    except Exception as e:
        logger.error(f"WebSocket error for execution {execution_id}: {e}")
        manager.disconnect(execution_id, websocket)
