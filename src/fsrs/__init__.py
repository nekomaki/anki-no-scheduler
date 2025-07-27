from abc import ABC, abstractmethod
from functools import cache
from typing import Optional, Type, TypeVar

from .types import State

T = TypeVar("T", bound="FSRS")


class FSRS(ABC):
    EXPECTED_LENGTH: int
    VERSION: int

    def __init__(self, params: tuple[float, ...]):
        self._params = params

    @property
    def params(self) -> tuple[float, ...]:
        return self._params

    @property
    def version(self) -> int:
        return self.VERSION

    @property
    def decay(self) -> float:
        raise NotImplementedError("Subclasses must implement the decay property.")

    @property
    def factor(self) -> float:
        raise NotImplementedError("Subclasses must implement the factor property.")

    def __getitem__(self, index: int) -> float:
        return self._params[index]

    def __len__(self) -> int:
        return len(self._params)

    def __eq__(self, other) -> bool:
        if not isinstance(other, FSRS):
            return NotImplemented
        return self.VERSION == other.VERSION and self._params == other._params

    def __hash__(self) -> int:
        return hash((self.VERSION, self._params))

    @classmethod
    @cache
    def from_tuple(cls: Type[T], params: tuple[float, ...]) -> T:
        if len(params) != cls.EXPECTED_LENGTH:
            raise ValueError(
                f"{cls.__name__} expects {cls.EXPECTED_LENGTH} parameters, got {len(params)}."
            )

        return cls(params)

    @classmethod
    def from_list(cls: Type[T], params: list[float]) -> T:
        return cls.from_tuple(tuple(params))

    @abstractmethod
    def simulate(
        self, state: State, t_review: float, retention: Optional[float] = None
    ) -> list[tuple[float, State]]:
        pass
