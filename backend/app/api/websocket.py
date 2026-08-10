"""WebSocket API endpoints."""

import json
from typing import Dict, Any, Optional
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from fastapi.websockets import WebSocketState

from app.core.event_bus import event_bus
from app.core.errors import AuthenticationError
from app.security.auth import jwt_manager

router = APIRouter()


class WebSocketManager:
    """WebSocket connection manager."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[UUID, list[str]] = {}
        self.job_subscribers: Dict[str, list[str]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: UUID) -> str:
        """Accept and store connection."""
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        
        self.active_connections[connection_id] = websocket
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(connection_id)
        
        return connection_id
    
    def disconnect(self, connection_id: str):
        """Remove connection."""
        websocket = self.active_connections.pop(connection_id, None)
        if websocket:
            # Remove from user connections
            for user_id, connections in self.user_connections.items():
                if connection_id in connections:
                    connections.remove(connection_id)
                    if not connections:
                        del self.user_connections[user_id]
                    break
            
            # Remove from job subscribers
            for job_id, subscribers in self.job_subscribers.items():
                if connection_id in subscribers:
                    subscribers.remove(connection_id)
                    if not subscribers:
                        del self.job_subscribers[job_id]
                    break
    
    async def send_message(self, connection_id: str, message: Dict[str, Any]):
        """Send message to a specific connection."""
        websocket = self.active_connections.get(connection_id)
        if websocket and websocket.client_state == WebSocketState.CONNECTED:
            try:
                await websocket.send_json(message)
            except Exception:
                self.disconnect(connection_id)
    
    async def send_to_user(self, user_id: UUID, message: Dict[str, Any]):
        """Send message to all connections for a user."""
        connections = self.user_connections.get(user_id, [])
        for connection_id in connections:
            await self.send_message(connection_id, message)
    
    async def send_to_job_subscribers(self, job_id: str, message: Dict[str, Any]):
        """Send message to all subscribers of a job."""
        subscribers = self.job_subscribers.get(job_id, [])
        for connection_id in subscribers:
            await self.send_message(connection_id, message)
    
    def subscribe_to_job(self, connection_id: str, job_id: str):
        """Subscribe a connection to job updates."""
        if job_id not in self.job_subscribers:
            self.job_subscribers[job_id] = []
        if connection_id not in self.job_subscribers[job_id]:
            self.job_subscribers[job_id].append(connection_id)
    
    def unsubscribe_from_job(self, connection_id: str, job_id: str):
        """Unsubscribe a connection from job updates."""
        if job_id in self.job_subscribers:
            if connection_id in self.job_subscribers[job_id]:
                self.job_subscribers[job_id].remove(connection_id)
                if not self.job_subscribers[job_id]:
                    del self.job_subscribers[job_id]


# Global WebSocket manager
ws_manager = WebSocketManager()


@router.websocket("/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time updates."""
    user_id = None
    connection_id = None
    
    try:
        # Authenticate via token in query params
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=1008, reason="Missing authentication token")
            return
        
        try:
            payload = jwt_manager.decode_token(token)
            user_id = UUID(payload.get("sub"))
        except Exception:
            await websocket.close(code=1008, reason="Invalid authentication token")
            return
        
        # Accept connection
        connection_id = await ws_manager.connect(websocket, user_id)
        
        # Send initial connection confirmation
        await ws_manager.send_message(connection_id, {
            "type": "connection_established",
            "client_id": client_id,
            "user_id": str(user_id),
            "connection_id": connection_id,
        })
        
        # Listen for messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                message_type = message.get("type")
                
                if message_type == "subscribe_job":
                    job_id = message.get("job_id")
                    if job_id:
                        ws_manager.subscribe_to_job(connection_id, job_id)
                        await ws_manager.send_message(connection_id, {
                            "type": "subscribed",
                            "job_id": job_id,
                        })
                
                elif message_type == "unsubscribe_job":
                    job_id = message.get("job_id")
                    if job_id:
                        ws_manager.unsubscribe_from_job(connection_id, job_id)
                        await ws_manager.send_message(connection_id, {
                            "type": "unsubscribed",
                            "job_id": job_id,
                        })
                
                elif message_type == "ping":
                    await ws_manager.send_message(connection_id, {
                        "type": "pong",
                        "timestamp": message.get("timestamp"),
                    })
                
                else:
                    await ws_manager.send_message(connection_id, {
                        "type": "error",
                        "message": f"Unknown message type: {message_type}",
                    })
            
            except json.JSONDecodeError:
                await ws_manager.send_message(connection_id, {
                    "type": "error",
                    "message": "Invalid JSON message",
                })
            
            except WebSocketDisconnect:
                break
    
    except WebSocketDisconnect:
        pass
    finally:
        if connection_id:
            ws_manager.disconnect(connection_id)


# Event bus subscriber - forwards events to WebSocket clients
@event_bus.on("job_progress")
async def handle_job_progress(event: Dict[str, Any]):
    """Handle job progress events and forward to WebSocket."""
    job_id = event.get("job_id")
    if job_id:
        await ws_manager.send_to_job_subscribers(str(job_id), {
            "type": "job_progress",
            "job_id": str(job_id),
            "progress": event.get("progress", 0),
            "status": event.get("status"),
            "message": event.get("message"),
        })


@event_bus.on("job_completed")
async def handle_job_completed(event: Dict[str, Any]):
    """Handle job completion events."""
    job_id = event.get("job_id")
    if job_id:
        await ws_manager.send_to_job_subscribers(str(job_id), {
            "type": "job_completed",
            "job_id": str(job_id),
            "result": event.get("result"),
        })


@event_bus.on("job_failed")
async def handle_job_failed(event: Dict[str, Any]):
    """Handle job failure events."""
    job_id = event.get("job_id")
    if job_id:
        await ws_manager.send_to_job_subscribers(str(job_id), {
            "type": "job_failed",
            "job_id": str(job_id),
            "error": event.get("error"),
        })


@event_bus.on("video_ready")
async def handle_video_ready(event: Dict[str, Any]):
    """Handle video ready events."""
    user_id = event.get("user_id")
    if user_id:
        await ws_manager.send_to_user(UUID(user_id), {
            "type": "video_ready",
            "video_id": str(event.get("video_id")),
            "url": event.get("url"),
        })