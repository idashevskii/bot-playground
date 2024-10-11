import logging
from typing import Any, Callable, Dict, List, Optional, Set
from sqlalchemy import func, select, delete
from sqlalchemy.orm import Session

from ..utils.serde import json_pydantic_dump

from ..plugins import PLUGINS

from ..utils.collections import set_attrs_from_dict
from .. import models, dto
from .world_core import AbstractPlugin, WorldAction

logger = logging.getLogger(__name__)

WORLD_SERIVCE_NAME = "world_service"

type StepChangedHandler = Callable[[], None]


class WorldService:
    def __init__(self) -> None:
        self.__pluguns: Dict[int, AbstractPlugin] = {}
        self.__running_worlds: Set[int] = set()

    def get_world_plugin(self, world: models.World) -> AbstractPlugin:
        world_id = world.id
        if world_id not in self.__pluguns:
            plugin = str(world.plugin)
            if not plugin in PLUGINS:
                raise RuntimeError(f"Plugin {plugin} not defined")
            clazz = PLUGINS[plugin]()
            self.__pluguns[world_id] = clazz()

        return self.__pluguns[world_id]

    def is_world_initialized(self, entity_id: int):
        return entity_id in self.__pluguns

    def is_world_running(self, entity_id: int):
        return entity_id in self.__running_worlds

    def render_step_state(self, db: Session, entity_id: int):
        step = get_step(db, entity_id)
        world = step.stage.world
        plugin = self.get_world_plugin(world)
        state = plugin.parse_state(step.state)
        return plugin.render_state(state)

    def describe_step_state(self, db: Session, entity_id: int):
        step = get_step(db, entity_id)
        world = step.stage.world
        plugin = self.get_world_plugin(world)
        state = plugin.parse_state(step.state)
        return plugin.describe_state(state)

    def get_world_actions(self, db: Session, world_id: int):
        world = get_world(db, world_id)
        plugin = self.get_world_plugin(world)
        return plugin.define_actions()

    def add_world_action(self, db: Session, world_id: int, action: WorldAction):
        world = get_world(db, world_id)
        plugin = self.get_world_plugin(world)
        plugin.add_action(action)

    def get_world_status(self, db: Session, world_id: int):
        stmt = (
            select(models.Step.id, models.Step.stage_id)
            .select_from(models.Step)
            .join(models.Stage)
            .where(models.Stage.world_id == world_id)
            .order_by(models.Step.id)
        )
        res = db.execute(stmt).all()
        steps: List[dto.WorldStatusStepDto] = []
        for row in res:
            step_id, stage_id = row.tuple()
            steps.append(dto.WorldStatusStepDto(id=step_id, stage_id=stage_id))

        return dto.WorldStatusDto(
            steps=steps,
            is_running=self.is_world_running(world_id),
        )

    async def world_control_start(
        self,
        db: Session,
        world_id: int,
        on_step_change: StepChangedHandler,
        from_step_id: Optional[int] = None,
        max_steps: Optional[int] = None,
    ):
        if self.is_world_running(world_id):
            logger.warning("World already running")
            return

        world = get_world(db, world_id)
        plugin = self.get_world_plugin(world)

        # if step not specified, find last step
        stage: Optional[models.Stage] = None
        if not from_step_id:
            from_step_id = self.__get_last_step_id(db=db, world_id=world_id)
        if from_step_id:
            step = get_step(db, from_step_id)
            stage = step.stage
            plugin.load(
                state=plugin.parse_state(step.state),
                stage_code=stage.code,
                stage_title=stage.title,
            )
            logger.info("Plugin loaded from history")
        else:
            logger.info("Plugin started from scratch")

        n = 0
        logger.info(f"World started {max_steps = }")
        try:
            self.__set_running(world_id, True)
            while self.is_world_running(world_id) and (
                max_steps == None or n < max_steps
            ):
                n += 1
                stage = await self.do_tick(
                    db=db, world=world, plugin=plugin, stage=stage
                )
                on_step_change()
                # logger.info(f"World tick {n}")
        finally:
            self.__set_running(world_id, False)

    async def do_tick(
        self,
        db: Session,
        world: models.World,
        stage: Optional[models.Stage],
        plugin: AbstractPlugin,
    ) -> models.Stage:
        tick_result = await plugin.do_tick()

        if not stage or stage.code != tick_result.stage.code:
            stage = models.Stage(
                world_id=world.id,
                title=tick_result.stage.title,
                code=tick_result.stage.code,
            )
            db.add(stage)
            db.commit()
            db.refresh(stage)

        step = models.Step(
            stage_id=stage.id,
            state=json_pydantic_dump(tick_result.state),
            actions=json_pydantic_dump(tick_result.actions),
            logs=json_pydantic_dump(tick_result.logs),
            interactions=json_pydantic_dump(tick_result.interations),
        )
        db.add(step)
        db.commit()

        return stage

    def world_control_stop(self, db: Session, world_id: int):
        self.__set_running(world_id, False)

    def __get_last_step_id(self, db: Session, world_id: int) -> Optional[int]:
        # looking for step with highest id
        stmt = (
            select(func.max(models.Step.id))
            .select_from(models.Step)
            .join(models.Stage)
            .where(models.Stage.world_id == world_id)
        )
        res = db.execute(stmt).first()
        if res and res[0]:
            return res[0]
        return None

    def __set_running(self, world_id: int, running: bool):
        if running:
            self.__running_worlds.add(world_id)
        elif world_id in self.__running_worlds:
            self.__running_worlds.remove(world_id)


def get_world(db: Session, entity_id: int):
    ret = db.query(models.World).filter(models.World.id == entity_id).first()
    if not ret:
        raise RuntimeError(f"World #{entity_id} not found")
    return ret


def get_worlds(db: Session, offset: int = 0, limit: int = 100):
    return db.query(models.World).offset(offset).limit(limit).all()


def get_world_stages(db: Session, entity_id: int):
    # world = get_world(db, entity_id)
    # return get_world(db, entity_id).stages
    return (
        db.query(models.Stage)
        .where(models.Stage.world_id == entity_id)
        .order_by(models.Stage.id.desc())
        .all()
    )


def create_world(db: Session, world: dto.WorldCreateDto):
    entity = models.World(**world.model_dump(by_alias=False))
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


def update_world(db: Session, entity_id: int, world: dto.WorldUpdateDto):
    entity = get_world(db, entity_id)
    set_attrs_from_dict(world.model_dump(by_alias=False), entity)
    db.commit()
    db.refresh(entity)
    return entity


def delete_world(db: Session, entity_id: int):
    entity = get_world(db, entity_id)
    db.delete(entity)
    db.commit()
    return entity


def clear_world(db: Session, entity_id: int):
    entity = get_world(db, entity_id)

    stages = db.query(models.Stage).where(models.Stage.world_id == entity_id).all()
    for stage in stages:
        db.execute(delete(models.Step).where(models.Step.stage_id == stage.id))
        db.delete(stage)
    db.commit()
    return entity


def get_step(db: Session, entity_id: int):
    ret = db.query(models.Step).filter(models.Step.id == entity_id).first()
    if not ret:
        raise RuntimeError(f"Step #{entity_id} not found")
    return ret


def get_world_service(state: Any) -> WorldService:
    return getattr(state, WORLD_SERIVCE_NAME)
