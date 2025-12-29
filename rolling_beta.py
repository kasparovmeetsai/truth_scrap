import pandas as pd
import numpy as np

def rolling_brent_beta_kbbl_diff(
    prices: pd.DataFrame,
    positions: pd.DataFrame,
    brent_col: str = "brent_dubai",
    window: int = 60
):
    """
    Rolling Brent beta of a portfolio using PRICE DIFFERENCES only.
    Output beta is in Brent-equivalent exposure (000s bbls / kbbl).

    Parameters
    ----------
    prices : DataFrame
        Daily prices (indexed by date). Must include brent_col.
    positions : DataFrame
        Daily positions in 000s bbls (kbbl), same columns as prices.
    brent_col : str
        Name of Brent price column.
    window : int
        Rolling window length (e.g. 60).

    Returns
    -------
    DataFrame with:
        - port_pnl
        - brent_dpx
        - brent_beta_kbbl
    """

    # --- Align data
    prices = prices.sort_index().copy()
    positions = positions.sort_index().copy()

    prices.index = pd.to_datetime(prices.index)
    positions.index = pd.to_datetime(positions.index)

    common_cols = prices.columns.intersection(positions.columns)
    if brent_col not in prices.columns:
        raise ValueError(f"Brent column '{brent_col}' not found in prices.")

    prices = prices[common_cols]
    positions = positions[common_cols]

    idx = prices.index.intersection(positions.index)
    prices = prices.loc[idx]
    positions = positions.loc[idx]

    # --- Lag positions (no lookahead)
    pos_lag = positions.shift(1)

    # --- Price differences
    dpx = prices.diff()

    # --- Portfolio daily PnL
    port_pnl = (pos_lag * dpx).sum(axis=1)

    # --- Brent price difference
    brent_dpx = dpx[brent_col]

    # --- Rolling Brent beta in kbbl
    brent_beta_kbbl = (
        port_pnl.rolling(window).cov(brent_dpx)
        / brent_dpx.rolling(window).var()
    )

    result = pd.DataFrame({
        "port_pnl": port_pnl,
        "brent_dpx": brent_dpx,
        "brent_beta_kbbl": brent_beta_kbbl
    })

    return result