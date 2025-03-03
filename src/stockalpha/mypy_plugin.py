from typing import Callable, Optional

from mypy.plugin import FunctionContext, MethodContext, Plugin
from mypy.types import Type


# This is a custom plugin to tell mypy about logging module attributes
class LoggingPlugin(Plugin):
    def get_function_hook(
        self, fullname: str
    ) -> Optional[Callable[[FunctionContext], Type]]:
        # Handles functions from the logging module
        return None


def plugin(version: str):
    # Entry point for mypy
    return LoggingPlugin
