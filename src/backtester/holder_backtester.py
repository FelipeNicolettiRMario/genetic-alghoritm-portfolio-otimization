import pandas as pd
from typing import Callable
from math import sqrt
from src.backtester.base import Backtester
from src.models.stock import Stock
from src.models.allocation import AllocationStrategy
from src.allocation.base import Allocation


class HolderBacktester(Backtester):

    def __init__(
        self,
        market_frame: pd.DataFrame,
        market_frame_normalizer: Callable[[pd.DataFrame], pd.DataFrame],
        initial_investment: float,
        wallet: list[Stock],
        allocation_strategy_engine: Allocation = None
    ):
        self.market_frame = market_frame_normalizer(market_frame)
        self.wallet = wallet
        self._allocation_strategy_engine = allocation_strategy_engine

        self._check_initial_investment_availability(
            self.market_frame, initial_investment
        )
        self.initial_investment = initial_investment

        self._wallet_positions, self._remaning_amount = self._setup_initial_positions()
        self._portfolio_values = [
            sum(self._wallet_positions[0].values()) + self._remaning_amount
        ]

        contribuition_strategy = self._allocation_strategy_engine.get_allocation_strategy()

        self._ticker_to_contribuition_strategy = {
            c.ticker: c for c in contribuition_strategy
        }

    def _check_initial_investment_availability(
        self, market_frame: pd.DataFrame, initial_investment: float
    ) -> None:

        if initial_investment <= 0:
            raise ValueError("Initial investment must be greater than zero.")

        first_row = market_frame.iloc[0]

        required_initial_investment = sum(
            first_row["Open"][stock.ticker] * stock.amount for stock in self.wallet
        )

        if initial_investment < required_initial_investment:
            raise ValueError(
                f"O investimento inicial {initial_investment} é insuficiente. "
                f"Valor mínimo necessário: {required_initial_investment}."
            )

    def _setup_initial_positions(self) -> tuple[list[dict[str, float]], float]:
        positions = {}
        first_row = self.market_frame.iloc[0]

        allocated_amount = 0.0

        for stock in self.wallet:
            price = first_row["Open"][stock.ticker]
            invested_value = stock.amount * price
            positions[stock.ticker] = invested_value
            allocated_amount += invested_value

        remaining_amount = self.initial_investment - allocated_amount

        return [positions], remaining_amount

    def run_backtest(self):

        periods = 0

        for idx, market_state in list(self.market_frame.iterrows())[1:]:

            current_positions = {}

            for stock in self.wallet:
                stock_price = market_state["Open"][stock.ticker]
                rule = self._ticker_to_contribuition_strategy.get(stock.ticker)
                if rule:
                    if (
                        periods > 0
                        and periods % rule.period == 0
                        and self._remaning_amount >= rule.contribuition_value
                    ):
                        _, self._remaning_amount = self._allocation_strategy_engine.allocate_funds_on_stock(
                            stock,stock_price, self._remaning_amount, rule
                        )

                price = market_state["Open"][stock.ticker]
                current_positions[stock.ticker] = stock.amount * price

            self._wallet_positions.append(current_positions)

            portfolio_value = sum(current_positions.values()) + self._remaning_amount
            self._portfolio_values.append(portfolio_value)

            periods += 1

        return self._wallet_positions

    def get_performance_metrics(self) -> dict:

        values = self._portfolio_values

        returns = [(values[i] / values[i - 1]) - 1 for i in range(1, len(values))]

        mean_return = sum(returns) / len(returns) if returns else 0.0

        if len(returns) > 1:
            variance = sum((r - mean_return) ** 2 for r in returns) / (len(returns) - 1)
            volatility = sqrt(variance)
        else:
            volatility = 0.0

        total_return = (values[-1] - values[0]) / values[0]

        return {
            "initial_value": values[0],
            "final_value": values[-1],
            "total_return": total_return,
            "mean_return": mean_return,
            "volatility": volatility,
        }
