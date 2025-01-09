import yfinance
import random
import numpy as np

from models.stock import Stock


class GetWalletDataTools:

    def __init__(
        self, stocks: list[str], start_date: str, end_date: str, period: str = "1mo"
    ) -> None:
        self.stock_history = yfinance.download(
            " ".join(stocks), start=start_date, end=end_date, interval=period
        )

        adj_close = self.stock_history["Adj Close"]
        self.returns = np.log(adj_close) - np.log(adj_close.shift(1))
        self.returns = self.returns.dropna()

    def get_wallet_volatiliy(self, quantities) -> float:
        weighted_returns = np.dot(self.returns, quantities)
        volatility = weighted_returns.std() * np.sqrt(252)

        return volatility.sum()

    def get_wallet_mean_return(self, risk_free_rate, quantities) -> float:
        weighted_returns = np.dot(self.returns, quantities)
        excess_return = weighted_returns.mean() - risk_free_rate

        return excess_return.sum()

    def get_sharpe_ratio_for_symbol(
        self, symbol: str, risk_free_rate: float, weight: int
    ) -> float:
        closing_data_for_symbol = self.stock_history["Adj Close"][symbol]
        returns = closing_data_for_symbol.pct_change()
        weighted_returns = returns * weight

        excess_return = weighted_returns.mean() - risk_free_rate
        volatility = weighted_returns.std() * np.sqrt(252)

        return excess_return / volatility

    @staticmethod
    def get_random_distribuited_wallet(
        wallet: list[str], total_number_of_stocks: int = 100
    ) -> list[Stock]:

        def split_into_random_numbers(total_sum, parts):
            intermediate_numbers = sorted(
                [random.randint(0, total_sum) for _ in range(parts - 1)]
            )

            intermediate_numbers = [0] + intermediate_numbers + [total_sum]

            final_parts = [
                intermediate_numbers[i + 1] - intermediate_numbers[i]
                for i in range(len(intermediate_numbers) - 1)
            ]

            return final_parts

        distribuition_of_wallet = split_into_random_numbers(
            total_number_of_stocks, len(wallet)
        )

        distribuited_wallet = []
        for ticker, distribuition in zip(wallet, distribuition_of_wallet):
            distribuited_wallet.append(Stock(ticker=ticker, amount=distribuition))

        return distribuited_wallet
