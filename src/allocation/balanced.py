from src.allocation.base import Allocation
from src.models.stock import Stock
from src.models.allocation import AllocationStrategy


class BalancedAllocation(Allocation):

    def __init__(self, stocks_initial_wallet: list[Stock], recurrent_funds: float):
        super().__init__()

        self._proportions = self._configure_proportions(stocks_initial_wallet)
        self._recurrent_funds = recurrent_funds

    def _configure_proportions(self, stocks_initial_wallet: list[Stock]):
        total = sum(stock.amount for stock in stocks_initial_wallet)
        return {s.ticker: s.amount / total for s in stocks_initial_wallet}

    def get_allocation_strategy(self) -> AllocationStrategy:
        return [
            AllocationStrategy(
                ticker=t,
                contribuition_value=self._recurrent_funds * p
            )
            for t, p in self._proportions.items()
        ]

    def allocate_funds_on_stock(
        self,
        stock: Stock,
        stock_actual_price: float,
        remaining_funds: float,
        allocation_strategy: AllocationStrategy,
    ):

        max_buy = allocation_strategy.contribuition_value // stock_actual_price
        if max_buy < 1:
            return stock, remaining_funds

        total_spent = max_buy * stock_actual_price

        if total_spent > remaining_funds:
            return stock, remaining_funds

        stock.amount += max_buy
        remaining_funds -= total_spent

        return stock, remaining_funds
