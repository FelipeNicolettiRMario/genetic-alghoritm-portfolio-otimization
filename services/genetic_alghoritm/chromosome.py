from __future__ import annotations
from typing import TypeVar, Tuple, Type
from abc import ABC, abstractmethod

T = TypeVar("T", bound="Chromosome")


class Chromosome(ABC):

    @abstractmethod
    def fitness(self) -> float: ...

    @abstractmethod
    def crossover(self: T, other: T) -> Tuple[T, T]: ...

    @abstractmethod
    def mutate(self) -> None: ...
