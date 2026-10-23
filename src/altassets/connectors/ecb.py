"""ECB Data Portal (SDMX 2.1 REST). Free, no key; reuse permitted with attribution.

Series ids are "<FLOW>.<KEY>", e.g.
  EXR.D.USD.EUR.SP00.A                       EUR/USD reference rate
  FM.M.U2.EUR.RT.MM.EURIBOR3MD_.HSTA         3m Euribor
  YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_10Y        euro area 10y AAA spot yield
"""

from __future__ import annotations

import io

import pandas as pd

from altassets.connectors.base import Connector
from altassets.data.schema import SeriesMeta, normalize
from altassets.taxonomy import AssetClass

BASE = "https://data-api.ecb.europa.eu/service/data"


class ECBConnector(Connector):
    source = "ecb"

    def fetch(self, series_id, start=None, end=None, asset_class=AssetClass.MACRO):
        flow, _, key = series_id.partition(".")
        params = {"format": "csvdata"}
        if start:
            params["startPeriod"] = start
        if end:
            params["endPeriod"] = end
        raw = self.client.get(f"{BASE}/{flow}/{key}", params=params)
        df = pd.read_csv(io.BytesIO(raw))
        title = df["TITLE"].iloc[0] if "TITLE" in df and len(df) else ""
        freq = df["FREQ"].iloc[0] if "FREQ" in df and len(df) else ""
        unit = df["UNIT"].iloc[0] if "UNIT" in df and len(df) else ""
        frame = normalize(
            df.rename(columns={"TIME_PERIOD": "date", "OBS_VALUE": "value"}),
            self.source,
            series_id,
        )
        meta = SeriesMeta(
            source=self.source,
            series_id=series_id,
            title=str(title),
            asset_class=asset_class,
            frequency=str(freq),
            unit=str(unit),
            license="ECB: reuse permitted with source attribution",
            url=f"https://data.ecb.europa.eu/data/datasets/{flow}/{series_id}",
        )
        return frame, meta
