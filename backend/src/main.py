from contextlib import asynccontextmanager
import logging
import os
from fastapi import FastAPI

from .world.world_service import WORLD_SERIVCE_NAME, WorldService

from .utils.ws import WS_PS_SERIVCE_NAME, WsPubSubService
from .routes import routers
from .models import create_all_tables

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "WARNING").upper())

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    create_all_tables()

    with WsPubSubService() as ws_ps:

        yield {WS_PS_SERIVCE_NAME: ws_ps, WORLD_SERIVCE_NAME: WorldService()}


app = FastAPI(lifespan=lifespan, root_path=os.environ["API_BASE_URI"])

for router in routers:
    app.include_router(router)


@app.get("/")
def version():
    return {"version": "1.0.0"}
