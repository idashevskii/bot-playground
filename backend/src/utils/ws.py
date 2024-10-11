from asyncio import Event
import asyncio
from contextlib import contextmanager
import logging
from typing import Any, Callable, ContextManager, Dict, List, Optional
from fastapi import Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from ..utils.async_utils import event_wait_timeout

WS_PS_SERIVCE_NAME = "ws_ps_service"

logger = logging.getLogger(__name__)


async def is_passive_ws_alive(websocket: WebSocket):
    try:
        await asyncio.wait_for(websocket.receive_bytes(), timeout=0.001)
    except asyncio.TimeoutError:
        return True
    except:
        return False
    return False


class WsPubSub:
    def __init__(self, on_last_disconnected: Callable[[], None]):
        self.__connections: list[WebSocket] = []
        self.__async_evt = Event()
        self.__event: Optional[BaseModel] = None
        self.__stopped = False
        self.__on_last_disconnected = on_last_disconnected
        self.__last_event_id: int = 0

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.__connections.append(websocket)
        last_sent_event_id: Optional[int] = None
        try:
            while not self.__stopped and await is_passive_ws_alive(websocket):
                # wait with timeout to avoid dead locks, e.g. when app is hot-reloaded
                await event_wait_timeout(self.__async_evt, 3.0)
                if self.__event != None and last_sent_event_id != self.__last_event_id:
                    # logger.info("Sending data")
                    last_sent_event_id = self.__last_event_id
                    await websocket.send_text(self.__event.model_dump_json())
        except WebSocketDisconnect:
            logger.info("WS self disconnected")
        finally:
            await self.disconnect(websocket)

    async def disconnect(self, websocket: WebSocket):
        try:
            await websocket.close()
        except:
            ...
        self.__connections.remove(websocket)
        if not self.__connections:
            self.__on_last_disconnected()

    def notify(self, event: BaseModel):
        self.__last_event_id += 1
        # logger.info(f"Attempt to notify {self.get_count()} clients")
        self.__event = event
        if self.__async_evt.is_set():
            raise RuntimeError("Event not yet handled")
        self.__async_evt.set()
        self.__async_evt.clear()

    def get_count(self):
        return len(self.__connections)

    def close(self):
        if self.__stopped:
            return
        self.__stopped = True
        self.__event = None
        if not self.__async_evt.is_set():
            self.__async_evt.set()


class WsPubSubService(ContextManager):
    def __init__(self):
        self.__topics: Dict[str, WsPubSub] = {}

    async def subscribe(self, topic: str, websocket: WebSocket):
        def unsubscribe():
            if topic in self.__topics:
                logger.info(f"All clients unsubscribed from {topic}")
                self.__topics[topic].close()
                del self.__topics[topic]

        if topic not in self.__topics:
            self.__topics[topic] = WsPubSub(unsubscribe)

        logger.info(
            f"Subscribed to {topic}. Total {self.__topics[topic].get_count()} clients"
        )

        await self.__topics[topic].connect(websocket)

    def publish(self, topic: str, event: BaseModel):
        if topic not in self.__topics:
            return

        self.__topics[topic].notify(event)

    def __exit__(self, exc_type, exc_value, traceback):
        logger.info("WsPubSubService: exiting")
        for ws in self.__topics.values():
            ws.close()


# Dependency
def get_ws_ps(state: Any) -> WsPubSubService:
    return getattr(state, WS_PS_SERIVCE_NAME)
