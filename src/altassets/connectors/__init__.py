from altassets.connectors.boe import BoEConnector
from altassets.connectors.ecb import ECBConnector
from altassets.connectors.fred import FREDConnector
from altassets.connectors.sec_edgar import SECEdgarConnector

REGISTRY = {
    "ecb": ECBConnector,
    "boe": BoEConnector,
    "fred": FREDConnector,
    "sec": SECEdgarConnector,
}


def get(name: str):
    if name == "bloomberg":
        from altassets.connectors.bloomberg import BloombergDesktopConnector

        return BloombergDesktopConnector()
    return REGISTRY[name]()
