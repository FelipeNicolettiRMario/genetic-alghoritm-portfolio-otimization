from dataclasses import dataclass


@dataclass
class Stock:
    ticker: str
    amount: int


@dataclass
class FundamentalData:
    ticker: str
    roic: float
    roe: float
    debt_ebitda: float
    growth_rate: float
