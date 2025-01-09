from __future__ import annotations

from models.stock import Stock
from services.wallet.get import GetWalletDataTools
from .chromosome import Chromosome

from random import choice, choices, randint
from copy import deepcopy
import numpy as np


class WalletChromosome(Chromosome):

    def __init__(
        self,
        stocks: list[Stock],
        wallet_tools: GetWalletDataTools,
        free_risk_tax: float,
    ) -> None:
        self.stocks = stocks
        self.repo = wallet_tools
        self.free_risk_tax = free_risk_tax
        self._index_for_stock = {}

        stock_index_counter = 0
        for stock in self.stocks:
            self._index_for_stock[stock.ticker] = stock_index_counter
            stock_index_counter += 1

        super().__init__()

    @property
    def weights(self):
        return [s.amount for s in self.stocks]

    def fitness(self) -> float:
        return self.repo.get_wallet_mean_return(
            self.free_risk_tax, self.weights
        ) / self.repo.get_wallet_volatiliy(self.weights)

    def crawl_stocks_and_replace_for_picked_genes(
        self, picked_genes: list[Stock]
    ) -> list[Stock]:
        for picked_gene in picked_genes:
            index_of_stock_in_child = self._index_for_stock[picked_gene.ticker]
            self.stocks[index_of_stock_in_child] = picked_gene

    def crossover(
        self, other: WalletChromosome
    ) -> tuple[WalletChromosome, WalletChromosome]:

        max_choices_of_stocks = int(len(self.stocks) / 2)
        replace_inf_value = lambda x: 0.001 if x == -np.inf else x
        sharp_for_each_stock = [
            self.repo.get_sharpe_ratio_for_symbol(
                s.ticker, self.free_risk_tax, s.amount
            )
            for s in self.stocks
        ]
        sharp_for_each_stock = [replace_inf_value(s) for s in sharp_for_each_stock]

        genes_choosed_from_self = choices(
            self.stocks,
            weights=sharp_for_each_stock,
            k=randint(1, max_choices_of_stocks),
        )
        genes_choosed_from_partner = choices(
            other.stocks,
            weights=sharp_for_each_stock,
            k=randint(1, max_choices_of_stocks),
        )

        child_1 = deepcopy(self)
        child_2 = deepcopy(other)

        child_1.crawl_stocks_and_replace_for_picked_genes(genes_choosed_from_partner)
        child_2.crawl_stocks_and_replace_for_picked_genes(genes_choosed_from_self)

        return child_1, child_2

    def mutate(self) -> None:
        #TODO: Encontrar melhor mutação
        sharpe_ratio_by_ticker = [
            (
                s.ticker,
                self.repo.get_sharpe_ratio_for_symbol(
                    s.ticker, self.free_risk_tax, s.amount
                ),
            )
            for s in self.stocks
        ]
        sharpe_ratio_by_ticker_sorted_asc = sorted(
            sharpe_ratio_by_ticker, key=lambda sharpe: sharpe[1]
        )
        stock_picked_to_remove_amount = self.stocks[
            self._index_for_stock[sharpe_ratio_by_ticker_sorted_asc[0][0]]
        ]
        stock_picked_to_increase_amount = None

        while (
            stock_picked_to_increase_amount == None
            or stock_picked_to_increase_amount == stock_picked_to_remove_amount
        ):
            stock_picked_to_increase_amount = self.stocks[
                self._index_for_stock[sharpe_ratio_by_ticker_sorted_asc[-1][0]]
            ]

        max_amount_to_remove = (
            int(stock_picked_to_remove_amount.amount / 2) + 2
            if stock_picked_to_remove_amount.amount > 1
            else 2
        )
        amount_to_remove = randint(1, max_amount_to_remove)

        if (stock_picked_to_remove_amount.amount - amount_to_remove) >=1:
            stock_picked_to_remove_amount.amount -= amount_to_remove
            stock_picked_to_increase_amount.amount += amount_to_remove

        self.crawl_stocks_and_replace_for_picked_genes(
            [stock_picked_to_remove_amount, stock_picked_to_increase_amount]
        )

    def __str__(self) -> str:
        return f"Wallet: {self.stocks} | Sharp Ratio: {self.fitness()}"
