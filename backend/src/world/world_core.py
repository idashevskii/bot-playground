from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

import logging

from pydantic import BaseModel

from ..utils.log import recreate_callback_logger

logger = logging.getLogger(__name__)


class ClientInteration(BaseModel):
    request: Any
    response: Any


class WorldLogEntry(BaseModel):
    level: str
    message: str


class WorldStage(BaseModel):
    code: str
    title: str


plugin_instance_id = 0


class WorldActionDef(BaseModel):
    name: str
    title: str
    shortcut: Optional[str] = None


class WorldAction(BaseModel):
    name: str


class ExternalInput(BaseModel):
    actions: List[WorldAction]


@dataclass
class TickResult[S: BaseModel]:
    state: S
    stage: WorldStage
    interations: List[ClientInteration]
    logs: List[WorldLogEntry]
    actions: List[WorldAction]


class AbstractPlugin[S: BaseModel]:
    def __init__(self) -> None:
        global plugin_instance_id
        plugin_instance_id += 1
        self.__id = plugin_instance_id
        # begin: loadable data
        self.__state: Optional[S] = None
        self.__stage: WorldStage = WorldStage(code="initial", title="Initial")
        self.__interations: List[ClientInteration] = []
        self.__logs: List[WorldLogEntry] = []
        # end: loadable data
        self.actions: List[WorldAction] = []
        self.logger = recreate_callback_logger(
            f"{__name__}.plugin[{self.__id}]",
            lambda level, message: self.__logs.append(
                WorldLogEntry(level=level, message=message)
            ),
        )
        logger.info(f"Plugin Created")

    async def do_tick(self) -> TickResult:
        # take actions before step
        external_input = ExternalInput(actions=self.actions)
        self.actions = []
        if self.__state == None:
            self.__state = await self.initialize()

        self.__state = await self.step(
            prev_state=self.__state, external_input=external_input
        )
        # take interactions and logs after step
        interations = self.__interations
        logs = self.__logs
        self.__interations = []
        self.__logs = []
        return TickResult(
            state=self.__state,
            stage=self.__stage,
            actions=external_input.actions,
            interations=interations,
            logs=logs,
        )

    def load(self, state: S, stage_code: str, stage_title: str):
        self.__state = state
        self.__stage: WorldStage = WorldStage(code=stage_code, title=stage_title)
        self.__interations = []
        self.__logs = []

    def add_interation(self, request: Any, response: Any):
        self.__interations.append(ClientInteration(request=request, response=response))

    def add_action(self, action: WorldAction):
        logger.info(f"Added action: {action}")
        self.actions.append(action)

    def set_stage(self, code: str, title: str):
        self.__stage = WorldStage(code=code, title=title)

    @classmethod
    def define_actions(cls) -> List[WorldActionDef]:
        return []

    @abstractmethod
    def parse_state(self, state_dump: str) -> S: ...

    @abstractmethod
    def describe_state(self, state: S) -> Dict[str, str]: ...

    @abstractmethod
    def render_state(self, state: S) -> bytes: ...

    @abstractmethod
    async def initialize(self) -> S:
        """
        Creates initial state
        """

    @abstractmethod
    async def step(
        self,
        prev_state: S,
        external_input: ExternalInput,
    ) -> S:
        """
        Creates new state based on previous state
        """
