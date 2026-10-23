"""Bank of England Interactive Statistical Database (IADB). Free CSV, no key.

Series ids are IADB codes, e.g. IUDBEDR (Bank Rate), IUDSOIA (SONIA).
"""

from __future__ import annotations

import io
from datetime import date

import pandas as pd

from altassets.connectors.base import Connector
from altassets.data.schema import SeriesMeta, normalize
from altassets.taxonomy import AssetClass

BASE = "https://www.bankofengland.co.uk/boeapps/database/_iadb-fromshowcolumns.asp"


def _iadb_date(d: str | None, default: str) -> str:
    if not d:
        return default
    return date.fromisoformat(d).strftime("%d/%b/%Y")


class BoEConnector(Connector):
    source = "boe"
    min_interval = 2.0

    def fetch(self, series_id, start=None, end=None, asset_class=AssetClass.MACRO):
        params = {
            "csv.x": "yes",
            "Datefrom": _iadb_date(start, "01/Jan/1963"),
            "Dateto": _iadb_date(end, "now"),
            "SeriesCodes": series_id,
            "CSVF": "TN",  # tabular, no titles
            "UsingCodes": "Y",
            "VPD": "Y",
            "VFD": "N",
        }
        raw = self.client.get(BASE, params=params)
        df = pd.read_csv(io.BytesIO(raw))
        df.columns = [c.strip() for c in df.columns]
        df = df.rename(columns={"DATE": "date", series_id: "value"})
        df["date"] = pd.to_datetime(df["date"], format="%d %b %Y")
        frame = normalize(df, self.source, series_id)
        meta = SeriesMeta(
            source=self.source,
            series_id=series_id,
            asset_class=asset_class,
            license="Bank of England: reuse permitted with attribution (see BoE terms)",
            url=f"https://www.bankofengland.co.uk/boeapps/database/fromshowcolumns.asp?SeriesCodes={series_id}",
        )
        return frame, meta
