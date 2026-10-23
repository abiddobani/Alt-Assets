import json

import pandas as pd
import pytest

from altassets.connectors.base import RobotsDisallowed
from altassets.connectors.boe import BoEConnector
from altassets.connectors.ecb import ECBConnector
from altassets.connectors.fred import FREDConnector
from altassets.connectors.sec_edgar import SECEdgarConnector
from altassets.data.store import Store
from altassets.taxonomy import AssetClass

ECB_CSV = """KEY,FREQ,CURRENCY,CURRENCY_DENOM,EXR_TYPE,EXR_SUFFIX,TIME_PERIOD,OBS_VALUE,OBS_STATUS,TITLE,UNIT
EXR.D.USD.EUR.SP00.A,D,USD,EUR,SP00,A,2024-01-02,1.1,A,US dollar/Euro,USD
EXR.D.USD.EUR.SP00.A,D,USD,EUR,SP00,A,2024-01-03,1.2,A,US dollar/Euro,USD
"""

BOE_CSV = """DATE,IUDBEDR
02 Jan 2024,5.25
03 Jan 2024,5.00
"""


def test_ecb_parses_sdmx_csv(make_client):
    c = make_client({"https://data-api.ecb.europa.eu/service/data/EXR/": (200, ECB_CSV)})
    df, meta = ECBConnector(c).fetch("EXR.D.USD.EUR.SP00.A", start="2024-01-01")
    assert list(df.columns) == ["source", "series_id", "date", "value"]
    assert df["value"].tolist() == [1.1, 1.2]
    assert meta.frequency == "D" and meta.title == "US dollar/Euro"
    req = c.seen[-1]
    assert req.url.path == "/service/data/EXR/D.USD.EUR.SP00.A"
    assert req.url.params["startPeriod"] == "2024-01-01"


def test_boe_parses_iadb_csv(make_client):
    c = make_client({"https://www.bankofengland.co.uk/boeapps/": (200, BOE_CSV)})
    df, _ = BoEConnector(c).fetch("IUDBEDR", start="2024-01-01")
    assert df["date"].tolist() == [pd.Timestamp("2024-01-02"), pd.Timestamp("2024-01-03")]
    assert c.seen[-1].url.params["Datefrom"] == "01/Jan/2024"


def test_fred_handles_missing_marker(make_client):
    obs = {"observations": [{"date": "2024-01-01", "value": "4.1"},
                            {"date": "2024-01-02", "value": "."},
                            {"date": "2024-01-03", "value": "4.0"}]}
    info = {"seriess": [{"title": "10y", "frequency_short": "D", "units_short": "%"}]}
    c = make_client({
        "https://api.stlouisfed.org/fred/series/observations": (200, json.dumps(obs)),
        "https://api.stlouisfed.org/fred/series?": (200, json.dumps(info)),
    })
    df, meta = FREDConnector(c, api_key="k").fetch("DGS10")
    assert df["value"].tolist() == [4.1, 4.0]
    assert meta.unit == "%"


def test_fred_requires_key(make_client, monkeypatch):
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="FRED_API_KEY"):
        FREDConnector(make_client({})).fetch("DGS10")


def test_sec_keeps_latest_filing_per_period(make_client):
    facts = {"entityName": "Example BDC", "facts": {"us-gaap": {"InvestmentOwnedAtFairValue": {
        "label": "Investments at fair value", "units": {"USD": [
            {"end": "2023-12-31", "val": 100, "filed": "2024-02-01"},
            {"end": "2023-12-31", "val": 101, "filed": "2025-02-01"},  # restated
            {"end": "2024-03-31", "val": 110, "filed": "2024-05-01"},
        ]}}}}}
    c = make_client({"https://data.sec.gov/api/xbrl/companyfacts/CIK0000000042.json": (200, json.dumps(facts))})
    df, meta = SECEdgarConnector(c).fetch("42:us-gaap:InvestmentOwnedAtFairValue")
    assert df["value"].tolist() == [101, 110]
    assert meta.asset_class is AssetClass.PRIVATE_LIQUID_LOANS


def test_robots_disallow_is_enforced(make_client):
    c = make_client({"https://data-api.ecb.europa.eu/": (200, ECB_CSV)},
                    robots="User-agent: *\nDisallow: /service/\n")
    with pytest.raises(RobotsDisallowed):
        ECBConnector(c).fetch("EXR.D.USD.EUR.SP00.A")


def test_cache_avoids_second_request(make_client):
    c = make_client({"https://data-api.ecb.europa.eu/service/data/EXR/": (200, ECB_CSV)})
    ECBConnector(c).fetch("EXR.D.USD.EUR.SP00.A")
    n = len(c.seen)
    ECBConnector(c).fetch("EXR.D.USD.EUR.SP00.A")
    assert len(c.seen) == n


def test_user_agent_carries_contact(make_client, monkeypatch):
    monkeypatch.setenv("ALTASSETS_CONTACT", "research@example.org")
    c = make_client({"https://data-api.ecb.europa.eu/service/data/EXR/": (200, ECB_CSV)})
    ECBConnector(c).fetch("EXR.D.USD.EUR.SP00.A")
    assert "research@example.org" in c.seen[-1].headers["user-agent"]


def test_store_roundtrip_and_panel(make_client, tmp_path):
    c = make_client({"https://data-api.ecb.europa.eu/service/data/EXR/": (200, ECB_CSV)})
    df, meta = ECBConnector(c).fetch("EXR.D.USD.EUR.SP00.A")
    store = Store(tmp_path / "curated")
    store.write(df, meta)
    pd.testing.assert_frame_equal(store.read("ecb", "EXR.D.USD.EUR.SP00.A"), df)
    panel = store.panel([("ecb", "EXR.D.USD.EUR.SP00.A")])
    assert panel.iloc[-1, 0] == 1.2
