"""Canonical long-format observation schema shared by every connector."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

import pandas as pd

from altassets.taxonomy import AssetClass

OBS_COLUMNS = ["source", "series_id", "date", "value"]


@dataclass(frozen=True)
class SeriesMeta:
    source: str
    series_id: str
    title: str = ""
    asset_class: AssetClass = AssetClass.MACRO
    frequency: str = ""  # D, W, M, Q, A
    unit: str = ""
    license: str = ""
    url: str = ""
    retrieved_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )


def normalize(df: pd.DataFrame, source: str, series_id: str) -> pd.DataFrame:
    """Coerce a two-column (date, value) frame into the canonical schema."""
    out = pd.DataFrame(
        {
            "source": source,
            "series_id": series_id,
            "date": pd.to_datetime(df["date"]),
            "value": pd.to_numeric(df["value"], errors="coerce"),
        }
    )
    return out.dropna(subset=["value"]).sort_values("date").reset_index(drop=True)
