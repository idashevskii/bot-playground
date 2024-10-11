import logging
from typing import Annotated, List
from fastapi import APIRouter, Depends, Path, Request, Response
from sqlalchemy.orm import Session

from ..dto import StepDto
from ..database import get_db
from ..world import world_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/steps")


# @router.get("", response_model=List[StepDto])
# async def read(db: Session = Depends(get_db)):
#     return world_service.get_steps(db)


@router.get("/{entityId}", response_model=StepDto)
async def read_one(
    entity_id: Annotated[int, Path(alias="entityId")], db: Session = Depends(get_db)
):
    return world_service.get_step(db, entity_id)


@router.get(
    "/{entityId}/render",
    responses={200: {"content": {"image/png": {}}}},
    response_class=Response,
)
def render_step_state(
    request: Request,
    entity_id: Annotated[int, Path(alias="entityId")],
    db: Session = Depends(get_db),
):

    w_service = world_service.get_world_service(request.state)
    image_bytes: bytes = w_service.render_step_state(db, entity_id)
    # media_type here sets the media type of the actual response sent to the client.
    return Response(content=image_bytes, media_type="image/png")


@router.get("/{entityId}/describe")
def describe_step_state(
    request: Request,
    entity_id: Annotated[int, Path(alias="entityId")],
    db: Session = Depends(get_db),
):
    w_service = world_service.get_world_service(request.state)
    return w_service.describe_step_state(db, entity_id)
