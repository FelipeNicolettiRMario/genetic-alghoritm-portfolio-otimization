from dataclasses import dataclass


@dataclass
class AllocationStrategy:
    ticker: str
    contribuition_value: float
    period: int = 30  # in days
