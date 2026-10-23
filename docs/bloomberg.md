# Bloomberg: optional local adapter

## Why it cannot run in the cloud

Bloomberg Terminal ("Bloomberg Pro") access comes through the Desktop API. `blpapi`
connects to `localhost:8194`, which only exists while a Terminal is running and logged
in on that machine. Cloud servers need B-PIPE or Data License, which are separate
enterprise products. So Bloomberg pulls run on your own computer.

## Licence boundary

Terminal data is for the licensed user's own use. The adapter writes to a local
`data/bloomberg/` store that is git-ignored and never synced to shared storage. Models
trained on it are fine to keep locally; do not publish the raw data or redistribute it.

## How it fits

`src/altassets/connectors/bloomberg.py` implements the same `Connector.fetch` interface
as the public connectors, using `HistoricalDataRequest` on `//blp/refdata`. Series ids
are `"<security>|<field>"`, e.g. `"SPX Index|PX_LAST"`.

On the Terminal machine:

```bash
pip install -e ".[bloomberg]"   # blpapi may need Bloomberg's own package index
altassets --store data/bloomberg fetch bloomberg "SPX Index|PX_LAST" --start 2010-01-01
```

First live run: 2026-10-23 on Abid's Terminal machine (blpapi 3.26.9.1). All series in
`sources/bloomberg.yaml` returned data; refresh them with

```bash
altassets --store data/bloomberg fetch-all sources/bloomberg.yaml
```

## Known quirks

- The Morningstar LSTA indices (SPBDAL family) have no spread or discount-margin field,
  so loan spreads come from the Bloomberg US Leveraged Loan Index (I38932US) and the
  S&P UBS Leveraged Loan Index (CSLLLTOB).
- The Cliffwater Direct Lending Index (CDLI) stops at 2023-06-30 on this entitlement;
  the Cliffwater BDC index (CWBDC) is the current listed proxy.
- CSLLLTOB is monthly until 2008-07, and I38932US discount margin is monthly until
  2024-09; both are daily after that. Resample before mixing them.
- JLSMLLI Index (J.P. Morgan leveraged loans) is not available on this entitlement.
