import pandas as pd
import numpy as np

def rolling_brent_beta_kbbl_diff(prices, positions, brent_col="brent", window=60):
    prices = prices.sort_index().copy()
    positions = positions.sort_index().copy()
    prices.index = pd.to_datetime(prices.index)
    positions.index = pd.to_datetime(positions.index)

    if brent_col not in prices.columns:
        raise ValueError(f"'{brent_col}' not found in prices columns: {prices.columns.tolist()}")

    # keep only tradable instruments in positions; keep brent in prices for beta driver
    trade_cols = prices.columns.intersection(positions.columns)
    price_cols = trade_cols.union([brent_col])

    prices = prices.loc[prices.index.intersection(positions.index), price_cols]
    positions = positions.loc[prices.index, trade_cols]

    pos_lag = positions.shift(1)
    dpx = prices.diff()

    port_pnl = (pos_lag * dpx[trade_cols]).sum(axis=1)
    brent_dpx = dpx[brent_col]

    brent_beta_kbbl = port_pnl.rolling(window).cov(brent_dpx) / brent_dpx.rolling(window).var()

    return pd.DataFrame({
        "port_pnl": port_pnl,
        "brent_dpx": brent_dpx,
        "brent_beta_kbbl": brent_beta_kbbl
    })