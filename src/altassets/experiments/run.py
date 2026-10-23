"""Run an experiment from a YAML config: build a panel from the store, window it, train."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from altassets.data.store import Store


def run(config_path: str | Path) -> dict:
    import numpy as np
    import torch

    from altassets.models.datasets import make_windows, time_split
    from altassets.models.forecaster import LSTMForecaster, train

    cfg = yaml.safe_load(Path(config_path).read_text())
    torch.manual_seed(cfg.get("seed", 0))
    store = Store(cfg.get("store", "data/curated"))
    keys = [tuple(k.split(":", 1)) for k in cfg["series"]]
    panel = store.panel(keys, freq=cfg.get("freq", "ME"))
    # Standardise on the training window only.
    X, y = make_windows(panel, cfg["target"], cfg["lookback"], cfg.get("horizon", 1))
    tr, va = time_split(len(X), cfg.get("val_frac", 0.2))
    mu, sd = X[tr].mean(axis=(0, 1)), X[tr].std(axis=(0, 1)) + 1e-8
    t = list(panel.columns).index(cfg["target"])
    X = (X - mu) / sd
    y = (y - mu[t]) / sd[t]
    model = LSTMForecaster(X.shape[-1], **cfg.get("model", {}))
    hist = train(model, X[tr], y[tr], X[va], y[va], **cfg.get("train", {}))
    result = {"config": cfg, "val_mse": hist[-1], "history": hist,
              "n_train": int(tr.stop), "n_val": int(len(X) - tr.stop)}
    out = Path(cfg.get("out", "experiments/runs")) / Path(config_path).stem
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(result, indent=2, default=float))
    torch.save(model.state_dict(), out / "model.pt")
    np.save(out / "norm.npy", np.stack([mu, sd]))
    return result
