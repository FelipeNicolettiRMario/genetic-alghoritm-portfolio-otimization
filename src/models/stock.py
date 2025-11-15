from dataclasses import dataclass


@dataclass
class Stock:
    ticker: str
    amount: int
