# Alt-Assets

Data connectors and a deep learning research platform for alternative assets.

**Equity:** real estate, infrastructure, public, private.
**Debt:** infrastructure debt, illiquid term loans, private liquid loans, commercial mortgages.

## Layout

```
src/altassets/
  connectors/   one module per source; all share PoliteClient (robots.txt, rate limit, cache, UA)
    ecb.py        ECB Data Portal (SDMX)
    boe.py        Bank of England IADB
    fred.py       FRED (needs FRED_API_KEY)
    sec_edgar.py  SEC EDGAR XBRL company facts (BDCs, REITs, listed alt managers)
    bloomberg.py  optional, local only: Bloomberg Desktop API
  data/         canonical schema (source, series_id, date, value) and Parquet store
  models/       windowed datasets, LSTM baseline, CPU/GPU device selection
  experiments/  YAML-driven training runs
  taxonomy.py   asset class enum used to tag every series
sources/series.yaml           starter series list
experiments/configs/          experiment configs
docs/sources.md               public source map per asset class, with access terms
docs/bloomberg.md             Bloomberg local adapter plan
```

## Quick start (CPU)

```bash
python -m venv .venv && source .venv/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -e ".[ml,dev]"

export ALTASSETS_CONTACT="you@example.com"   # sent in the User-Agent; SEC requires it
export FRED_API_KEY="..."                    # free at fredaccount.stlouisfed.org

altassets fetch-all sources/series.yaml
altassets train experiments/configs/baseline_cre.yaml
pytest            # offline tests
pytest -m live    # hits the real endpoints
```

## Moving to a GPU later

Install the CUDA build of torch on the GPU machine (`pip install torch --index-url
https://download.pytorch.org/whl/cu124`). `models/device.py` picks CUDA automatically;
override with `ALTASSETS_DEVICE=cpu|cuda|mps`. Nothing else changes.

## Data rules

- Connectors only for sources with an API or bulk download whose terms allow automated
  access. `PoliteClient` refuses robots.txt-disallowed paths and throttles per host.
- Every series keeps its licence and URL in the metadata sidecar next to the Parquet file.
- Bloomberg data stays on the Terminal machine (`data/bloomberg/`, git-ignored).
