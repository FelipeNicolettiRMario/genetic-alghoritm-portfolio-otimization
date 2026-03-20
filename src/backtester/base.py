from abc import ABC, abstractmethod


class Backtester(ABC):
    @abstractmethod
    def run_backtest(self) -> dict:
        """Run the backtest and return the results as a dictionary."""
        pass

    @abstractmethod
    def get_performance_metrics(self) -> dict:
        """Retrieve performance metrics from the backtest results."""
        pass
