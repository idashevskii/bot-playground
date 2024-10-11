import importlib
from typing import Callable, Dict, Type

from ..world.world_core import AbstractPlugin

PLUGINS: Dict[str, Callable[[], Type[AbstractPlugin]]] = {
    "DEMO_GAME": lambda: importlib.import_module(
        ".demo_game.demo_game", __package__
    ).DemoGamePlugin
}
