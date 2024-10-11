from enum import StrEnum
from typing import Dict, Tuple
import asyncio
import io

from pydantic import BaseModel
from ...world.world_core import AbstractPlugin, ExternalInput, WorldActionDef

from PIL import Image, ImageDraw


class ActionName(StrEnum):
    TURN_UP = "TURN_UP"
    TURN_DOWN = "TURN_DOWN"
    TURN_LEFT = "TURN_LEFT"
    TURN_RIGHT = "TURN_RIGHT"


class DemoGameState(BaseModel):
    field_size: Tuple[int, int]
    pos: Tuple[int, int]
    velocity: Tuple[int, int]
    score: int


class DemoGamePlugin(AbstractPlugin[DemoGameState]):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def define_actions(cls):
        return [
            WorldActionDef(
                name=ActionName.TURN_UP, title="Turn Up", shortcut="ArrowUp"
            ),
            WorldActionDef(
                name=ActionName.TURN_DOWN, title="Turn Down", shortcut="ArrowDown"
            ),
            WorldActionDef(
                name=ActionName.TURN_LEFT, title="Turn Left", shortcut="ArrowLeft"
            ),
            WorldActionDef(
                name=ActionName.TURN_RIGHT, title="Turn Right", shortcut="ArrowRight"
            ),
        ]

    def render_state(self, state: DemoGameState):
        im_width = 640
        im_height = 480
        im = Image.new("RGB", (im_width, im_height))
        draw = ImageDraw.Draw(im)
        draw.line((0, 0) + im.size, fill=128)
        draw.line((0, im.size[1], im.size[0], 0), fill=128)
        cols, rows = state.field_size
        field_size_px = (im_width / cols, im_height / rows)
        current_col, current_row = state.pos

        for col in range(cols):
            for row in range(rows):
                is_current = current_col == col and current_row == row
                fill_color = (64, 0, 64)
                if is_current:
                    fill_color = (255, 255, 0)
                draw.rectangle(
                    (
                        col * field_size_px[0],
                        row * field_size_px[1],
                        (col + 1) * field_size_px[0],
                        (row + 1) * field_size_px[1],
                    ),
                    outline=255,
                    fill=fill_color,
                )

        ret = io.BytesIO()
        im.save(ret, format="PNG")
        ret = ret.getvalue()

        return ret

    def describe_state(self, state: DemoGameState) -> Dict[str, str]:
        return {
            "score": str(state.score),
            "s_score": str(state.score**2),
            "chances": str(state.score % 61 + 7),
        }

    def parse_state(self, state_dump: str) -> DemoGameState:
        return DemoGameState.model_validate_json(state_dump)

    async def initialize(self):

        return DemoGameState(field_size=(24, 16), pos=(0, 0), velocity=(1, 1), score=0)

    async def step(
        self,
        prev_state: DemoGameState,
        external_input: ExternalInput,
    ):
        state = prev_state

        state.score += 1

        stage_number = state.score // 5
        self.set_stage(f"stage_{stage_number}", f"Stage {stage_number}")

        vel_x, vel_y = 0, 0

        for action in external_input.actions:
            # self.logger.info(f"{action.name = }")
            if action.name == ActionName.TURN_UP:
                vel_y = -1
            elif action.name == ActionName.TURN_DOWN:
                vel_y = 1
            elif action.name == ActionName.TURN_LEFT:
                vel_x = -1
            elif action.name == ActionName.TURN_RIGHT:
                vel_x = 1

        # keep velocity, if was not changed
        if vel_x == 0 and vel_y == 0:
            vel_x, vel_y = state.velocity

        state.pos = (
            (state.pos[0] + vel_x) % state.field_size[0],
            (state.pos[1] + vel_y) % state.field_size[1],
        )
        self.logger.debug(f"{vel_x=} {vel_y=}")
        # self.logger.info("It is long info. " * 10)
        # self.logger.warning("It is long warning. " * 10)
        # self.logger.error("It is long error. " * 10)
        # self.logger.critical("It is long critical. " * 10)
        state.velocity = (vel_x, vel_y)

        # self.logger.info(f"Current speed: {vel_x=} {vel_y=}")
        await asyncio.sleep(0.2)

        return state
