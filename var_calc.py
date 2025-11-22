import numpy as np
import pandas as pd

def compute_contracts_from_var(
    prices: pd.DataFrame,
    signal_df: pd.DataFrame,      # +1 / -1 / 0 per asset
    weights_df: pd.DataFrame,     # % of total VaR per asset (row-wise)
    contract_multipliers: dict,
    var_target: float = 250_000,  # total 20d 95% VaR in $
    window: int = 20,
    H: int = 20,
    z: float = 1.65
) -> pd.DataFrame:
    """
    Walk-forward contract sizing using:
    - prices (levels),
    - per-asset VAR allocation (% of total VAR),
    - long/short signals,
    - and a total VAR target.

    Returns:
        contracts_df: DataFrame with number of contracts per asset per date.
    """

    assets = prices.columns
    mult = pd.Series(contract_multipliers).reindex(assets)

    # 1) Build 1-contract daily PnL in $ from prices
    #    ΔP * multiplier (aligned by date index)
    price_diff = prices.diff()
    pnl_1c = price_diff.mul(mult, axis=1)

    contracts_list = []
    dates_list = []

    # start after we have a full window
    start_idx = window + 1

    for t in range(start_idx, len(prices)):
        date = prices.index[t]

        # ------------- window data up to t-1 -------------
        window_pnl = pnl_1c.iloc[t-window:t]       # (window x N)
        if window_pnl.isnull().all().all():
            continue

        # covariance of 1-contract daily PnL
        Sigma = window_pnl.cov()                  # N x N, $^2
        Sigma_vals = Sigma.values

        # per-asset daily std of 1-contract PnL
        sigma_i = window_pnl.std()                # Series, in $

        # ------------- VAR allocation & signals ----------
        alpha = weights_df.loc[date].reindex(assets).fillna(0.0)
        # ensure non-negative and normalized
        alpha = alpha.clip(lower=0)
        if alpha.sum() > 0:
            alpha = alpha / alpha.sum()
        else:
            # if all zero, no risk that day
            contracts_list.append(pd.Series(0.0, index=assets, name=date))
            dates_list.append(date)
            continue

        signal = signal_df.loc[date].reindex(assets).fillna(0.0)

        # ------------- unscaled contract "shape" ----------
        # avoid div by zero
        sigma_safe = sigma_i.replace(0, np.nan)
        n0 = (alpha / sigma_safe).fillna(0.0).values  # vector (N,)

        # if everything zero (e.g. flat vols), skip
        if np.allclose(n0, 0):
            contracts_list.append(pd.Series(0.0, index=assets, name=date))
            dates_list.append(date)
            continue

        # ------------- current portfolio VAR for this shape ----------
        sigma_port_daily = np.sqrt(n0 @ Sigma_vals @ n0)   # $ daily
        var_current = z * np.sqrt(H) * sigma_port_daily

        if var_current == 0 or np.isnan(var_current):
            k = 0.0
        else:
            k = var_target / var_current

        # final unsigned contracts
        n_unsigned = k * n0

        # apply long/short signal
        n_signed = n_unsigned * signal.values

        contracts_series = pd.Series(n_signed, index=assets, name=date)
        contracts_list.append(contracts_series)
        dates_list.append(date)

    contracts_df = pd.DataFrame(contracts_list, index=dates_list)
    return contracts_df