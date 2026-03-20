from abc import ABC, abstractmethod

from src.models.stock import Stock
from src.models.allocation import AllocationStrategy


class Allocation(ABC):

    @abstractmethod
    def get_allocation_strategy(self) -> list[AllocationStrategy]:
        pass

    @abstractmethod
    def allocate_funds_on_stock(
        self,
        stock: Stock,
        stock_actual_price: float,
        remaining_funds: float,
        allocation_strategy: AllocationStrategy,
    ) -> tuple[Stock, float]:
        pass
