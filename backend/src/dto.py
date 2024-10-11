from typing import List, Optional, Tuple
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseDtoModel(BaseModel):
    model_config = ConfigDict(
        strict=True,
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel,
    )


class WorldBaseDto(BaseDtoModel):
    title: str


class WorldCreateDto(WorldBaseDto):
    plugin: str


class WorldUpdateDto(WorldBaseDto):
    config: str


class WorldDto(WorldBaseDto):
    id: int
    plugin: str
    config: Optional[str]


class ExtendedWorldDto(WorldDto):
    initialized: bool
    running: bool


class StageDto(BaseDtoModel):
    id: int
    title: str
    world_id: int


class WorldStatusStepDto(BaseDtoModel):
    id: int
    stage_id: int


class WorldStatusDto(BaseDtoModel):
    is_running: bool
    steps: List[WorldStatusStepDto]


class StepDto(BaseDtoModel):
    stage_id: int
    state: str
    actions: str
    logs: str
    interactions: str


class NoopEventWsDto(BaseModel):
    status: str = "OK"
