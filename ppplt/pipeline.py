"""Pipeline primitives used across functional API.

Exposes a simple Step container with >> chaining.
"""

from __future__ import annotations
from typing import Callable, Any


class Step:
    def __init__(self, func: Callable, *args: Any, **kwargs: Any):
        self._func = func
        self._args = args
        self._kwargs = kwargs
        self._executed = False
        self._result = None

    def run(self):
        if not self._executed:
            self._result = self._func(*self._args, **self._kwargs)
            self._executed = True
        return self._result

    def __rshift__(self, other: "Step"):
        self.run()
        return other

    def __repr__(self) -> str:  # pragma: no cover
        name = getattr(self._func, "__name__", str(self._func))
        return f"Step(func={name}, executed={self._executed})"


__all__ = ["Step"]
