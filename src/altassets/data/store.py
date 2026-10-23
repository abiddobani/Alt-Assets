"""Parquet store: data/curated/<source>/<series_id>.parquet plus a JSON sidecar of metadata."""

from __future__ import annotations

import json
import re
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from altassets.data.schema import SeriesMeta


def _slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s)


class Store:
    def __init__(self, root: str | Path = "data/curated"):
        self.root = Path(root)

    def path(self, source: str, series_id: str) -> Path:
        return self.root / _slug(source) / f"{_slug(series_id)}.parquet"

    def write(self, df: pd.DataFrame, meta: SeriesMeta) -> Path:
        p = self.path(meta.source, meta.series_id)
        p.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(p, index=False)
        meta_dict = asdict(meta)
        meta_dict["asset_class"] = meta.asset_class.value
        p.with_suffix(".json").write_text(json.dumps(meta_dict, indent=2))
        return p

    def read(self, source: str, series_id: str) -> pd.DataFrame:
        return pd.read_parquet(self.path(source, series_id))

    def panel(self, keys: list[tuple[str, str]], freq: str = "ME") -> pd.DataFrame:
        """Wide frame of several series resampled to a common frequency (last value)."""
        cols = {}
        for source, sid in keys:
            s = self.read(source, sid).set_index("date")["value"]
            cols[f"{source}:{sid}"] = s.resample(freq).last()
        return pd.DataFrame(cols)
