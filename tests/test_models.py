import numpy as np
import pandas as pd
import pytest

from altassets.models.datasets import make_windows, time_split


def test_windows_have_no_lookahead():
    panel = pd.DataFrame({"a": np.arange(10.0), "b": np.arange(10.0) * 2},
                         index=pd.date_range("2020", periods=10, freq="ME"))
    X, y = make_windows(panel, "a", lookback=3, horizon=1)
    assert X.shape == (7, 3, 2)
    # First window covers rows 0..2 and predicts row 3.
    assert X[0, -1, 0] == 2.0 and y[0] == 3.0
    tr, va = time_split(len(X), 0.3)
    assert tr.stop == va.start


def test_lstm_trains_on_cpu():
    torch = pytest.importorskip("torch")
    from altassets.models.forecaster import LSTMForecaster, train

    X = np.random.default_rng(0).normal(size=(40, 5, 3)).astype(np.float32)
    y = X[:, -1, 0]
    hist = train(LSTMForecaster(3, hidden=8, layers=1), X[:30], y[:30], X[30:], y[30:],
                 epochs=3, device=torch.device("cpu"))
    assert len(hist) == 3


def test_experiment_runs_end_to_end(tmp_path):
    pytest.importorskip("torch")
    import yaml

    from altassets.data.schema import SeriesMeta, normalize
    from altassets.data.store import Store
    from altassets.experiments.run import run

    store = Store(tmp_path / "curated")
    dates = pd.date_range("2000-01-31", periods=80, freq="QE")
    rng = np.random.default_rng(0)
    for sid in ("x", "y"):
        df = normalize(pd.DataFrame({"date": dates, "value": rng.normal(size=80).cumsum()}), "t", sid)
        store.write(df, SeriesMeta(source="t", series_id=sid))
    cfg = {"store": str(store.root), "out": str(tmp_path / "runs"), "freq": "QE",
           "series": ["t:x", "t:y"], "target": "t:x", "lookback": 4,
           "model": {"hidden": 8, "layers": 1}, "train": {"epochs": 2}}
    path = tmp_path / "smoke.yaml"
    path.write_text(yaml.safe_dump(cfg))
    result = run(path)
    assert result["n_train"] > 0 and (tmp_path / "runs" / "smoke" / "model.pt").exists()
