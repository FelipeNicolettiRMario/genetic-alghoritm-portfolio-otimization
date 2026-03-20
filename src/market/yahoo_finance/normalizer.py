import pandas as pd


def normalize_market_frame(market_frame: pd.DataFrame) -> pd.DataFrame:
    market_frame = market_frame.ffill().bfill()

    return market_frame
