"""Hit the real endpoints. Run with: pytest -m live"""

import os

import pytest

from altassets.connectors.base import PoliteClient

pytestmark = pytest.mark.live


@pytest.fixture
def client(tmp_path):
    return PoliteClient(cache_dir=None)


def test_ecb_live(client):
    from altassets.connectors.ecb import ECBConnector

    df, _ = ECBConnector(client).fetch("EXR.D.USD.EUR.SP00.A", start="2024-01-01", end="2024-01-31")
    assert len(df) > 15


def test_boe_live(client):
    from altassets.connectors.boe import BoEConnector

    df, _ = BoEConnector(client).fetch("IUDBEDR", start="2024-01-01", end="2024-03-31")
    assert len(df) > 30


@pytest.mark.skipif(not os.environ.get("FRED_API_KEY"), reason="FRED_API_KEY not set")
def test_fred_live(client):
    from altassets.connectors.fred import FREDConnector

    df, _ = FREDConnector(client).fetch("DGS10", start="2024-01-01", end="2024-01-31")
    assert len(df) > 15


@pytest.mark.skipif(not os.environ.get("ALTASSETS_CONTACT"), reason="SEC requires a contact User-Agent")
def test_sec_live(client):
    from altassets.connectors.sec_edgar import SECEdgarConnector

    df, _ = SECEdgarConnector(client).fetch("1287750:us-gaap:InvestmentOwnedAtFairValue:USD")
    assert len(df) > 10
