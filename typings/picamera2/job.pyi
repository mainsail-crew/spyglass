from collections.abc import Callable as Callable
from typing import Any, Generic, Literal, TypeVar

from _typeshed import Incomplete

T = TypeVar("T")

class Job(Generic[T]):
    _functions: Incomplete
    _future: Incomplete
    _signal_function: Incomplete
    _result: Incomplete
    calls: int
    def __init__(
        self,
        functions: list[Callable[..., tuple[bool, Any] | tuple[Literal[True], T]]],
        signal_function=None,
    ) -> None: ...
    def execute(self) -> bool: ...
    def signal(self) -> None: ...
    def get_result(self, timeout: float | None = None) -> T: ...
    def cancel(self) -> None: ...
