"""FRED (St. Louis Fed) API. Free key required: set FRED_API_KEY.

Some FRED series are owned by third parties (e.g. ICE BofA, S&P) with their own
redistribution limits; check the series notes before publishing derived data.
"""

from __future__ import annotations

import json
import os

import pandas as pd

from altassets.connectors.base import Connector
from altassets.data.schema import SeriesMeta, normalize
from altassets.taxonomy import AssetClass

BASE = "https://api.stlouisfed.org/fred"


class FREDConnector(Connector):
    source = "fred"
    min_interval = 0.6  # FRED allows ~120 requests/minute

    def __init__(self, client=None, api_key: str | None = None):
        super().__init__(client)
        self.api_key = api_key or os.environ.get("FRED_API_KEY")

    def _get(self, path: str, **params) -> dict:
        if not self.api_key:
            raise RuntimeError("FRED_API_KEY is not set (free key: fredaccount.stlouisfed.org)")
        params |= {"api_key": self.api_key, "file_type": "json"}
        return json.loads(self.client.get(f"{BASE}/{path}", params=params))

    def fetch(self, series_id, start=None, end=None, asset_class=AssetClass.MACRO):
        params = {"series_id": series_id}
        if start:
            params["observation_start"] = start
        if end:
            params["observation_end"] = end
        obs = self._get("series/observations", **params)["observations"]
        df = pd.DataFrame(obs)[["date", "value"]].replace(".", None)
        info = self._get("series", series_id=series_id)["seriess"][0]
        meta = SeriesMeta(
            source=self.source,
            series_id=series_id,
            title=info.get("title", ""),
            asset_class=asset_class,
            frequency=info.get("frequency_short", ""),
            unit=info.get("units_short", ""),
            license="FRED terms of use; check series notes for third-party copyright",
            url=f"https://fred.stlouisfed.org/series/{series_id}",
        )
        return normalize(df, self.source, series_id), meta
