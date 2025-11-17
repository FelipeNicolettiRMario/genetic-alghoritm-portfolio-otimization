import yfinance
import random
import numpy as np

from cachetools.func import lru_cache

from src.models.stock import FundamentalData, Stock
from src.market.base import IMarketEngine


class YahooFinanceMarketEngine(IMarketEngine):

    def __init__(
        self,
        stocks: list[str],
        start_date: str,
        end_date: str,
        period: str = "1d",
        risk_free_rate: float = 0.0,
    ) -> None:
        self.stock_history = yfinance.download(
            " ".join(stocks),
            start=start_date,
            end=end_date,
            interval=period,
            auto_adjust=False,
        )
        self.risk_free_rate = risk_free_rate

    def get_portfolio_series(self, wallet: list[Stock] = None):

        if wallet:
            tickers = [s.ticker for s in wallet]
            amounts = np.array([s.amount for s in wallet])
            adj_close = self.stock_history["Adj Close"][tickers]
        else:
            tickers = list(self.stock_history["Adj Close"].columns)
            adj_close = self.stock_history["Adj Close"]
            amounts = np.ones(len(tickers))

        weights = amounts / amounts.sum()

        returns = adj_close.pct_change().dropna()

        portfolio_returns = (returns * weights).sum(axis=1)

        portfolio_equity = (1 + portfolio_returns).cumprod()

        return portfolio_returns, portfolio_equity, weights

    def get_sharpe_ratio(self, wallet: list[Stock] = None):
        portfolio_returns, _, _ = self.get_portfolio_series(wallet)
        excess_returns = portfolio_returns - self.risk_free_rate / 252

        vol = portfolio_returns.std()
        vol = max(vol, 1e-8)

        sharpe = (excess_returns.mean() / vol) * np.sqrt(252)
        return sharpe

    def get_sortino_ratio(self, wallet: list[Stock] = None):
        portfolio_returns, _, _ = self.get_portfolio_series(wallet)
        excess_returns = portfolio_returns - self.risk_free_rate / 252
        negative_returns = np.minimum(excess_returns, 0)

        downside = np.sqrt((negative_returns**2).mean()) * np.sqrt(252)
        downside = max(downside, 1e-8)

        annualized_ret = (1 + portfolio_returns.mean()) ** 252 - 1

        return (annualized_ret - self.risk_free_rate) / downside

    def get_calmar_ratio(self, wallet: list[Stock] = None):
        _, equity, _ = self.get_portfolio_series(wallet)

        n_days = len(equity)
        annualized_ret = (equity.iloc[-1] / equity.iloc[0]) ** (252 / n_days) - 1

        dd = (equity / equity.cummax()) - 1
        max_dd = dd.min()

        if abs(max_dd) < 1e-6:
            return 0

        return annualized_ret / abs(max_dd)

    def get_wallet_volatiliy(self, quantities) -> float:
        weighted_returns = np.dot(self.returns, quantities)
        volatility = weighted_returns.std() * np.sqrt(252)

        return volatility.sum()

    def get_wallet_mean_return(self, quantities) -> float:
        weighted_returns = np.dot(self.returns, quantities)
        excess_return = weighted_returns.mean() - self.risk_free_rate

        return excess_return.sum()

    @staticmethod
    def get_random_distribuited_wallet(
        wallet: list[str], total_number_of_stocks: int = 100
    ) -> list[Stock]:

        def split_into_random_numbers(total_sum, parts):
            cuts = sorted(random.sample(range(1, total_sum), parts - 1))
            final_parts = []

            prev = 0
            for cut in cuts:
                final_parts.append(cut - prev)
                prev = cut
            final_parts.append(total_sum - prev)

            return final_parts

        distribuition_of_wallet = split_into_random_numbers(
            total_number_of_stocks, len(wallet)
        )

        distribuited_wallet = []
        for ticker, distribuition in zip(wallet, distribuition_of_wallet):
            distribuited_wallet.append(Stock(ticker=ticker, amount=distribuition))

        return distribuited_wallet

    @staticmethod
    def get_random_assets_wallet(
        tickers: list[str], min_assets: int = 3, max_assets: int = 10
    ) -> list[str]:
        number_of_assets = random.randint(min_assets, max_assets)
        selected_tickers = random.sample(tickers, number_of_assets)

        return selected_tickers

    @lru_cache(maxsize=128)
    def get_fundamentalist_data(self, ticker: str) -> FundamentalData:
        t = yfinance.Ticker(ticker)

        bs = t.balance_sheet
        if bs is None or bs.empty:
            raise ValueError(f"Sem balance sheet disponível para {ticker}")

        bs_latest = bs.iloc[:, 0]

        invested_capital = float(bs_latest.get("Invested Capital", 0))
        total_debt = float(bs_latest.get("Total Debt", 0))
        equity = float(bs_latest.get("Common Stock Equity", 0))

        if invested_capital == 0:
            invested_capital = 1e-6

        fs = t.financials
        if fs is None or fs.empty:
            raise ValueError(f"Sem income statement disponível para {ticker}")

        fs_latest = fs.iloc[:, 0]

        net_income = float(fs_latest.get("Net Income", 0))
        ebit = float(fs_latest.get("EBIT", 0))
        ebitda = float(fs_latest.get("EBITDA", 0))
        tax_rate = float(fs_latest.get("Tax Rate For Calcs", 0.25))

        nopat = ebit * (1 - tax_rate)
        roic = nopat / invested_capital

        roe = net_income / equity if equity != 0 else 0

        if ebitda == 0:
            debt_ebitda = float("inf")
        else:
            debt_ebitda = total_debt / ebitda

        net_incomes = fs.loc["Net Income"].dropna()

        if len(net_incomes) >= 2:
            ni_t0 = float(net_incomes.iloc[0])
            ni_t1 = float(net_incomes.iloc[1])
            growth_rate = (ni_t0 - ni_t1) / abs(ni_t1) if ni_t1 != 0 else 0
        else:
            growth_rate = 0

        return FundamentalData(
            ticker=ticker,
            roic=roic,
            roe=roe,
            debt_ebitda=debt_ebitda,
            growth_rate=growth_rate,
        )

    def get_multiple_fundamentalist_data(
        self, tickers: list[str]
    ) -> dict[str, FundamentalData]:
        fundamental_data = {}
        for ticker in tickers:
            try:
                data = self.get_fundamentalist_data(ticker)
                fundamental_data[ticker] = data
            except ValueError as e:
                print(f"Erro ao obter dados fundamentais para {ticker}: {e}")
        return fundamental_data
