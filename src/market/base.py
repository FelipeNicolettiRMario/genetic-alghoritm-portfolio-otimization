from abc import ABC, abstractmethod

from src.models.stock import Stock


class IMarketEngine(ABC):

    @abstractmethod
    def get_wallet_volatiliy(self, quantities: int) -> float:
        pass

    @abstractmethod
    def get_wallet_mean_return(self, quantities: int) -> float:
        pass

    @abstractmethod
    def get_sharpe_ratio(self, wallet: list[Stock] = None):
        pass

    @abstractmethod
    def get_sortino_ratio(self, wallet: list[Stock] = None) -> float:
        pass

    @abstractmethod
    def get_calmar_ratio(self, wallet: list[Stock] = None) -> float:
        pass

    @abstractmethod
    def get_random_distribuited_wallet(
        wallet: list[str], total_number_of_stocks: int = 100
    ) -> list[Stock]:
        pass

    @abstractmethod
    def get_random_assets_wallet(
        self, tickers: list[str], max_assets: int
    ) -> list[str]:
        pass

    @abstractmethod
    def get_fundamentalist_data(self, ticker: str) -> "FundamentalData":
        pass

    @abstractmethod
    def get_multiple_fundamentalist_data(
        self, tickers: list[str]
    ) -> dict[str, "FundamentalData"]:
        pass
