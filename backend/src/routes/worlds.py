import logging
from typing import Annotated, List, Optional
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Path,
    Query,
    Request,
    WebSocket,
)
from sqlalchemy.orm import Session

from ..world.world_core import WorldAction

from ..utils.ws import get_ws_ps

from ..dto import (
    ExtendedWorldDto,
    NoopEventWsDto,
    StageDto,
    WorldCreateDto,
    WorldDto,
    WorldStatusDto,
    WorldUpdateDto,
)
from ..database import get_db
from ..world import world_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/worlds")


def make_world_watch_status_topic(world_id: int):
    return f"world/{world_id}/status-watch"


@router.get("", response_model=List[WorldDto])
async def read(db: Session = Depends(get_db)):
    return world_service.get_worlds(db)


@router.get("/extended", response_model=List[ExtendedWorldDto])
async def read_extended(request: Request, db: Session = Depends(get_db)):
    w_service = world_service.get_world_service(request.state)
    return [
        ExtendedWorldDto(
            initialized=w_service.is_world_initialized(world.id),
            running=w_service.is_world_running(world.id),
            **WorldDto.model_validate(world).model_dump(),
        )
        for world in world_service.get_worlds(db)
    ]


@router.get("/{entityId}", response_model=WorldDto)
async def read_one(
    entity_id: Annotated[int, Path(alias="entityId")], db: Session = Depends(get_db)
):
    return world_service.get_world(db, entity_id)


@router.post("", response_model=WorldDto)
async def create(item: WorldCreateDto, db: Session = Depends(get_db)):
    return world_service.create_world(db, item)


@router.patch("/{entityId}", response_model=WorldDto)
async def update(
    entity_id: Annotated[int, Path(alias="entityId")],
    item: WorldUpdateDto,
    db: Session = Depends(get_db),
):
    return world_service.update_world(db, entity_id, item)


@router.get("/{entityId}/stages", response_model=List[StageDto])
async def read_stages(
    entity_id: Annotated[int, Path(alias="entityId")], db: Session = Depends(get_db)
):
    return world_service.get_world_stages(db, entity_id)


@router.get("/{entityId}/status", response_model=WorldStatusDto)
async def read_status(
    request: Request,
    entity_id: Annotated[int, Path(alias="entityId")],
    db: Session = Depends(get_db),
):
    w_service = world_service.get_world_service(request.state)
    return w_service.get_world_status(db, entity_id)


@router.post("/{entityId}/stop")
async def stop_world(
    request: Request,
    entity_id: Annotated[int, Path(alias="entityId")],
    db: Session = Depends(get_db),
):
    w_service = world_service.get_world_service(request.state)
    w_service.world_control_stop(db, entity_id)


@router.post("/{entityId}/start")
async def do_world_start(
    request: Request,
    background_tasks: BackgroundTasks,
    entity_id: Annotated[int, Path(alias="entityId")],
    db: Session = Depends(get_db),
    max_steps: Annotated[Optional[int], Query(alias="maxSteps")] = None,
):
    w_service = world_service.get_world_service(request.state)

    async def task():
        await w_service.world_control_start(
            db,
            entity_id,
            on_step_change=lambda: notify_world_status_change(request, entity_id),
            max_steps=max_steps,
        )

    background_tasks.add_task(task)


@router.get("/{entityId}/actions/schema")
async def read_actions_schema(
    request: Request,
    entity_id: Annotated[int, Path(alias="entityId")],
    db: Session = Depends(get_db),
):
    w_service = world_service.get_world_service(request.state)
    return w_service.get_world_actions(db, entity_id)


@router.post("/{entityId}/actions/add")
async def add_action(
    request: Request,
    action: WorldAction,
    entity_id: Annotated[int, Path(alias="entityId")],
    db: Session = Depends(get_db),
):
    w_service = world_service.get_world_service(request.state)
    w_service.add_world_action(db, entity_id, action)


@router.delete("/{entityId}", response_model=WorldDto)
async def delete(
    entity_id: Annotated[int, Path(alias="entityId")], db: Session = Depends(get_db)
):
    # raise HTTPException(417, detail="Unsafe API Disabled")
    world_service.clear_world(db, entity_id)
    return world_service.delete_world(db, entity_id)


@router.post("/{entityId}/clear", response_model=WorldDto)
async def clear(
    entity_id: Annotated[int, Path(alias="entityId")], db: Session = Depends(get_db)
):
    # raise HTTPException(417, detail="Unsafe API Disabled")
    return world_service.clear_world(db, entity_id)


@router.websocket("/ws/{entityId}/watch-status")
async def websocket_endpoint(
    websocket: WebSocket,
    entity_id: Annotated[int, Path(alias="entityId")],
    db: Session = Depends(get_db),
):
    ws_ps = get_ws_ps(websocket.state)

    if not world_service.get_world(db, entity_id):
        raise HTTPException(404, detail="World not found")

    await ws_ps.subscribe(make_world_watch_status_topic(entity_id), websocket)


def notify_world_status_change(request: Request, entity_id: int):
    ws_ps = get_ws_ps(request.state)
    ws_ps.publish(make_world_watch_status_topic(entity_id), NoopEventWsDto())


@router.get("/{entityId}/test-trigger-status")
async def test_trigger_status(
    entity_id: Annotated[int, Path(alias="entityId")],
    request: Request,
):
    notify_world_status_change(request, entity_id)


# @router.get("/{id}/test-ws")
# async def ws_test(id: int):
#     return HTMLResponse(
#         f"""
# <!DOCTYPE html>
# <html>
#     <body>
#         <h1>See console</h1>
#         <script>
#             var ws = new WebSocket(`/api/worlds/ws/{id}/watch-status`);
#             ws.onmessage = function(event) {{
#                 console.log(event.data)
#             }};
#         </script>
#     </body>
# </html>
# """
#     )
