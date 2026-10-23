"""Sliding-window datasets over a wide panel (rows = dates, columns = series)."""

from __future__ import annotations

import numpy as np
import pandas as pd


def make_windows(
    panel: pd.DataFrame, target: str, lookback: int, horizon: int = 1
) -> tuple[np.ndarray, np.ndarray]:
    """X: (n, lookback, n_features), y: (n,) = target value `horizon` steps ahead.

    Uses only past rows for each window, so there is no look-ahead leakage.
    """
    panel = panel.ffill().dropna()
    values = panel.to_numpy(dtype=np.float32)
    t = panel.columns.get_loc(target)
    xs, ys = [], []
    for i in range(lookback, len(values) - horizon + 1):
        xs.append(values[i - lookback : i])
        ys.append(values[i + horizon - 1, t])
    if not xs:
        return np.empty((0, lookback, values.shape[1]), np.float32), np.empty(0, np.float32)
    return np.stack(xs), np.asarray(ys, dtype=np.float32)


def time_split(n: int, val_frac: float = 0.2) -> tuple[slice, slice]:
    cut = int(n * (1 - val_frac))
    return slice(0, cut), slice(cut, n)
