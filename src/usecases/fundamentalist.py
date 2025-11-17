import numpy as np
from random import choice, randint

from src.genetic_alghoritm.chromosome import Chromosome

from src.models.stock import FundamentalData


class FundamentalistChromosome(Chromosome):

    def __init__(
        self, tickers: list[str], fundamental_scores: dict[str, FundamentalData]
    ) -> None:
        self._fundamental_scores = fundamental_scores
        self.tickers = tickers

    def _get_fundamentalist_score(self, ticker: str) -> float:
        data = self._fundamental_scores[ticker]

        roic_val = max(data.roic, -0.99)
        roic_score = roic_val / (abs(roic_val) + 1)

        roe_val = max(data.roe, -0.99)
        roe_score = roe_val / (abs(roe_val) + 1)

        if data.debt_ebitda <= 0 or np.isnan(data.debt_ebitda):
            debt_score = 1.0
        else:
            debt_score = 1 / (1 + data.debt_ebitda)

        growth_score = (np.tanh(data.growth_rate) + 1) / 2

        score = (
            0.35 * roic_score + 0.35 * roe_score + 0.2 * growth_score + 0.1 * debt_score
        )

        return score

    def genetic_information(self) -> str:
        return hash(tuple(self.tickers))

    def fitness(self) -> float:
        score_for_tickers = [
            self._get_fundamentalist_score(ticker) for ticker in self.tickers
        ]

        average_score = sum(score_for_tickers) / len(score_for_tickers)

        return average_score

    def crossover(self, other):
        number_of_sons = 2
        sons = []

        max_son_size = max(len(self.tickers), len(other.tickers))
        min_son_size = min(len(self.tickers), len(other.tickers))
        
        for _ in range(number_of_sons):
            son_size = np.random.randint(min_son_size, max_son_size + 1)
            combined_tickers = list(set(self.tickers + other.tickers))
            np.random.shuffle(combined_tickers)
            son_tickers = combined_tickers[:son_size]

            son = FundamentalistChromosome(
                tickers=son_tickers,
                fundamental_scores=self._fundamental_scores,
            )
            sons.append(son)

        return tuple(sons)

    def mutate(self) -> None:
        if not self.tickers:
            return

        mutation_type = np.random.choice(["add", "remove", "swap"])
        all_tickers = list(self._fundamental_scores.keys())
        available_tickers = list(set(all_tickers) - set(self.tickers))

        if mutation_type == "add":
            max_new_tickers = len(all_tickers) - len(self.tickers)
            if max_new_tickers > 0:
                new_ticker = str(np.random.choice(available_tickers))
                self.tickers.append(new_ticker)

        elif mutation_type == "remove":
            if len(self.tickers) > 1:
                ticker_to_remove = str(np.random.choice(self.tickers))
                self.tickers.remove(ticker_to_remove)

        elif mutation_type == "swap":
            if available_tickers:
                ticker_to_remove = str(np.random.choice(self.tickers))
                ticker_to_add = str(np.random.choice(available_tickers))
                self.tickers.remove(ticker_to_remove)
                self.tickers.append(ticker_to_add)
