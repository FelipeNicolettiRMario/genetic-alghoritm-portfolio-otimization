from __future__ import annotations

from src.models.stock import Stock
from src.market.base import IMarketEngine
from src.genetic_alghoritm.chromosome import Chromosome

from random import choice, choices, randint


class TripleRiskEfficiencyChromosome(Chromosome):

    def __init__(
        self,
        stocks: list[Stock],
        market_engine: IMarketEngine,
        free_risk_tax: float,
    ) -> None:
        self._stocks = stocks
        self._market_engine = market_engine

    def genetic_information(self):
        return hash(tuple((s.ticker, s.amount) for s in self._stocks))

    def fitness(self):
        sharpe = self._market_engine.get_sharpe_ratio(tuple(self._stocks))
        sortino = self._market_engine.get_sortino_ratio(tuple(self._stocks))
        calmar = self._market_engine.get_calmar_ratio(tuple(self._stocks))

        sharpe_norm = sharpe / 3
        sortino_norm = sortino / 4
        calmar_norm = calmar / 5

        score = 0.4 * sharpe_norm + 0.3 * sortino_norm + 0.3 * calmar_norm

        return score

    def _create_son_wallet_from_cuts(
        self,
        ticker_list: list[str],
        self_quantities: dict[str, int],
        other_quantities: dict[str, int],
    ) -> TripleRiskEfficiencyChromosome:
        stocks_for_son = []
        for ticker in ticker_list:
            ticker_quantity_in_self = self_quantities[ticker]
            ticker_quantity_in_other = other_quantities[ticker]

            if ticker_quantity_in_self == ticker_quantity_in_other:
                stocks_for_son.append(Stock(ticker, ticker_quantity_in_self))
            else:
                stocks_for_son.append(
                    Stock(
                        ticker,
                        choice([ticker_quantity_in_self, ticker_quantity_in_other]),
                    )
                )

        return TripleRiskEfficiencyChromosome(
            stocks_for_son,
            self._market_engine,
            self._market_engine.risk_free_rate,
        )

    def crossover(
        self, other: TripleRiskEfficiencyChromosome
    ) -> tuple[TripleRiskEfficiencyChromosome, TripleRiskEfficiencyChromosome]:
        sons: list[TripleRiskEfficiencyChromosome] = []

        self_quantities = {s.ticker: s.amount for s in self._stocks}
        other_quantities = {s.ticker: s.amount for s in other._stocks}
        tickers = list(self_quantities.keys())

        parent_gen_infos = [
            self.genetic_information(),
            other.genetic_information(),
        ]
        genetic_information_for_sons: set = set()

        MAX_TRIES_FOR_GENETIC_DIVERSITY = 10

        for _ in range(2):
            tries_for_genetic_diversity = 0
            while True:
                son = self._create_son_wallet_from_cuts(
                    tickers,
                    self_quantities,
                    other_quantities,
                )
                son_genetic_info = son.genetic_information()

                if (
                    son_genetic_info not in parent_gen_infos
                    and son_genetic_info not in genetic_information_for_sons
                ):
                    genetic_information_for_sons.add(son_genetic_info)
                    sons.append(son)
                    break

                if tries_for_genetic_diversity >= MAX_TRIES_FOR_GENETIC_DIVERSITY:
                    son.mutate()
                    sons.append(son)
                    break

                tries_for_genetic_diversity += 1

        return tuple(sons)

    def mutate(self):
        stock_to_increase, stock_to_decrease = choices(self._stocks, k=2)
        while stock_to_increase is stock_to_decrease or stock_to_decrease.amount < 2:
            stock_to_increase, stock_to_decrease = choices(self._stocks, k=2)

        max_transfer = stock_to_decrease.amount // 2
        value_to_transfer = randint(1, max_transfer)

        stock_to_increase.amount += value_to_transfer
        stock_to_decrease.amount -= value_to_transfer

    def __str__(self) -> str:
        return f"Wallet: {self._stocks} | Efficiency: {self.fitness()}"
