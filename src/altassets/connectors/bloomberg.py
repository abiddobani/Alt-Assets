"""Optional Bloomberg Desktop API adapter (not used in the cloud).

blpapi's Desktop API only talks to a Terminal that is running and logged in on the
same machine (localhost:8194). It therefore has to run on Abid's own computer. Data
pulled this way is licensed for that user's own use under the Bloomberg Terminal
agreement, so it stays local: write it to the local store and do not upload it to
shared storage or redistribute it.

Usage on the Terminal machine:
    pip install "altassets[bloomberg]"   # blpapi from Bloomberg's index if needed
    altassets fetch bloomberg "SPX Index|PX_LAST" --start 2015-01-01
"""

from __future__ import annotations

import pandas as pd

from altassets.connectors.base import Connector
from altassets.data.schema import SeriesMeta, normalize
from altassets.taxonomy import AssetClass

MAX_TIMEOUTS = 12  # consecutive 5 s waits with no event before giving up


class BloombergError(RuntimeError):
    pass


def _error_text(err) -> str:
    """Format an errorInfo element as "CATEGORY/SUBCATEGORY: message"."""
    parts = [err.getElementAsString(n) for n in ("category", "subcategory") if err.hasElement(n)]
    msg = err.getElementAsString("message") if err.hasElement("message") else str(err)
    return f"{'/'.join(parts)}: {msg}" if parts else msg


class BloombergDesktopConnector(Connector):
    source = "bloomberg"

    def __init__(self, host: str = "localhost", port: int = 8194):
        try:
            import blpapi  # noqa: F401
        except ImportError as e:  # pragma: no cover - only on a Terminal machine
            raise RuntimeError(
                "blpapi is not installed. This adapter only works on a machine with a "
                "running Bloomberg Terminal."
            ) from e
        self.host, self.port = host, port

    def fetch(self, series_id, start=None, end=None, asset_class=AssetClass.PUBLIC_EQUITY):
        """series_id is "<security>|<field>", e.g. "SPX Index|PX_LAST"."""
        import blpapi

        security, _, field = series_id.partition("|")
        field = field or "PX_LAST"
        opts = blpapi.SessionOptions()
        opts.setServerHost(self.host)
        opts.setServerPort(self.port)
        session = blpapi.Session(opts)
        if not session.start() or not session.openService("//blp/refdata"):
            raise RuntimeError("Could not connect to the Bloomberg Terminal on localhost")
        try:
            req = session.getService("//blp/refdata").createRequest("HistoricalDataRequest")
            req.getElement("securities").appendValue(security)
            req.getElement("fields").appendValue(field)
            req.set("startDate", (start or "1990-01-01").replace("-", ""))
            if end:
                req.set("endDate", end.replace("-", ""))
            session.sendRequest(req)
            rows = []
            timeouts = 0
            while True:
                ev = session.nextEvent(5000)
                if ev.eventType() == blpapi.Event.TIMEOUT:
                    timeouts += 1
                    if timeouts >= MAX_TIMEOUTS:
                        raise BloombergError(f"{security}: no response from the Terminal")
                    continue
                timeouts = 0
                for msg in ev:
                    if msg.hasElement("responseError"):
                        raise BloombergError(f"{security}: {_error_text(msg.getElement('responseError'))}")
                    if not msg.hasElement("securityData"):
                        continue
                    sd = msg.getElement("securityData")
                    if sd.hasElement("securityError"):
                        raise BloombergError(f"{security}: {_error_text(sd.getElement('securityError'))}")
                    fx = sd.getElement("fieldExceptions") if sd.hasElement("fieldExceptions") else None
                    if fx is not None and fx.numValues():
                        err = fx.getValueAsElement(0).getElement("errorInfo")
                        raise BloombergError(f"{security}|{field}: {_error_text(err)}")
                    fd = sd.getElement("fieldData")
                    for i in range(fd.numValues()):
                        pt = fd.getValueAsElement(i)
                        if pt.hasElement(field):  # a date can come back without the field
                            rows.append(
                                {
                                    "date": pt.getElementAsDatetime("date"),
                                    "value": pt.getElementAsFloat(field),
                                }
                            )
                if ev.eventType() == blpapi.Event.RESPONSE:
                    break
            if not rows:
                raise BloombergError(f"{series_id}: no observations returned")
        finally:
            session.stop()
        meta = SeriesMeta(
            source=self.source,
            series_id=series_id,
            asset_class=asset_class,
            license="Bloomberg Terminal licence: personal use, do not redistribute",
        )
        return normalize(pd.DataFrame(rows), self.source, series_id), meta
