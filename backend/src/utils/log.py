from typing import Callable

import logging


class CallbackLoggingHandler(logging.Handler):
    def __init__(self, handler: Callable[[str, str], None]) -> None:
        super().__init__()
        self.__handler = handler

    def emit(self, record: logging.LogRecord):
        self.__handler(record.levelname, record.getMessage())


def recreate_callback_logger(
    name: str, handler: Callable[[str, str], None]
) -> logging.Logger:
    return recreate_logger(name=name, handler=CallbackLoggingHandler(handler))


def recreate_logger(name: str, handler: logging.Handler) -> logging.Logger:
    ret = logging.getLogger(name)
    ret.handlers.clear()
    ret.setLevel(logging.DEBUG)
    ret.addHandler(handler)
    return ret
