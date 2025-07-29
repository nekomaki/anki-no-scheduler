from typing import Optional, Protocol, Type, TypeVar

from .types import State

T = TypeVar("T", bound="FSRSProtocol")


class FSRSProtocol(Protocol):
    decay: float
    factor: float

    @classmethod
    def from_tuple(cls: Type[T], params: tuple[float, ...]) -> T: ...

    @classmethod
    def from_list(cls: Type[T], params: list[float]) -> T: ...

    def simulate(
        self,
        state: State,
        t_review: float,
        retention: Optional[float] = None,
    ) -> list[tuple[float, State]]: ...

    def power_forgetting_curve(self, t: float, s: float) -> float: ...
