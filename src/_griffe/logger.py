"""This module contains logging utilities.

We provide the [`patch_loggers`][griffe.patch_loggers]
function so dependant libraries can patch loggers as they see fit.

For example, to fit in the MkDocs logging configuration
and prefix each log message with the module name:

```python
import logging
from _griffe.logger import patch_loggers


class LoggerAdapter(logging.LoggerAdapter):
    def __init__(self, prefix, logger):
        super().__init__(logger, {})
        self.prefix = prefix

    def process(self, msg, kwargs):
        return f"{self.prefix}: {msg}", kwargs


def get_logger(name):
    logger = logging.getLogger(f"mkdocs.plugins.{name}")
    return LoggerAdapter(name, logger)


patch_loggers(get_logger)
```
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any, Callable, ClassVar


class LogLevel(Enum):
    """Enumeration of available log levels."""

    trace: str = "trace"
    """The TRACE log level."""
    debug: str = "debug"
    """The DEBUG log level."""
    info: str = "info"
    """The INFO log level."""
    success: str = "success"
    """The SUCCESS log level."""
    warning: str = "warning"
    """The WARNING log level."""
    error: str = "error"
    """The ERROR log level."""
    critical: str = "critical"
    """The CRITICAL log level."""


class _Logger:
    _default_logger: Any = logging.getLogger
    _instances: ClassVar[dict[str, _Logger]] = {}

    def __init__(self, name: str) -> None:
        # Default logger that can be patched by third-party.
        self._logger = self.__class__._default_logger(name)

    def __getattr__(self, name: str) -> Any:
        # Forward everything to the logger.
        return getattr(self._logger, name)

    @classmethod
    def get(cls, name: str) -> _Logger:
        """Get a logger instance.

        Parameters:
            name: The logger name.

        Returns:
            The logger instance.
        """
        if name not in cls._instances:
            cls._instances[name] = cls(name)
        return cls._instances[name]

    @classmethod
    def _patch_loggers(cls, get_logger_func: Callable) -> None:
        # Patch current instances.
        for name, instance in cls._instances.items():
            instance._logger = get_logger_func(name)
        # Future instances will be patched as well.
        cls._default_logger = get_logger_func


def get_logger(name: str) -> _Logger:
    """Create and return a new logger instance.

    Parameters:
        name: The logger name.

    Returns:
        The logger.
    """
    return _Logger.get(name)


def patch_loggers(get_logger_func: Callable[[str], Any]) -> None:
    """Patch loggers.

    Parameters:
        get_logger_func: A function accepting a name as parameter and returning a logger.
    """
    _Logger._patch_loggers(get_logger_func)
