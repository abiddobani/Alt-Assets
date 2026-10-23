"""SEC EDGAR XBRL company facts. Free; SEC fair-access policy requires a descriptive
User-Agent with contact details and at most 10 requests/second.

Useful for private credit: BDCs (business development companies) file quarterly
schedules of investments and fair-value metrics for their middle-market loan books,
and non-traded REITs/infra vehicles file NAV and leverage data.

Series ids are "<CIK>:<taxonomy>:<concept>[:<unit>]", e.g.
  1287750:us-gaap:InvestmentOwnedAtFairValue:USD      (Ares Capital)
"""

from __future__ import annotations

import json

import pandas as pd

from altassets.connectors.base import Connector
from altassets.data.schema import SeriesMeta, normalize
from altassets.taxonomy import AssetClass

BASE = "https://data.sec.gov/api/xbrl/companyfacts"


class SECEdgarConnector(Connector):
    source = "sec"
    min_interval = 0.2

    def fetch(self, series_id, start=None, end=None, asset_class=AssetClass.PRIVATE_LIQUID_LOANS):
        parts = series_id.split(":")
        cik, taxonomy, concept = parts[:3]
        unit = parts[3] if len(parts) > 3 else "USD"
        facts = json.loads(self.client.get(f"{BASE}/CIK{int(cik):010d}.json"))
        node = facts["facts"][taxonomy][concept]
        rows = pd.DataFrame(node["units"][unit])
        # One value per period end; prefer the latest filing that reported it.
        rows = rows.sort_values("filed").drop_duplicates("end", keep="last")
        df = rows.rename(columns={"end": "date", "val": "value"})[["date", "value"]]
        frame = normalize(df, self.source, series_id)
        if start:
            frame = frame[frame["date"] >= start]
        if end:
            frame = frame[frame["date"] <= end]
        meta = SeriesMeta(
            source=self.source,
            series_id=series_id,
            title=f"{facts.get('entityName', '')}: {node.get('label', concept)}",
            asset_class=asset_class,
            unit=unit,
            license="US government work (public domain); SEC fair-access rules apply",
            url=f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}",
        )
        return frame.reset_index(drop=True), meta
