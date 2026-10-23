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

The adapter has not been run against a real Terminal yet. The first run should be done
together, on your machine.

## What to pull first (once we test it)

- Leveraged loan index levels and spreads (Morningstar LSTA, if your Terminal carries it)
- CMBS spreads and delinquency
- Listed REIT and infrastructure index levels
- MSCI/RCA property indices, if entitled
