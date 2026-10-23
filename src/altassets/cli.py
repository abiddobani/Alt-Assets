"""Command line entry point.

    altassets fetch ecb FM.M.U2.EUR.RT.MM.EURIBOR3MD_.HSTA --asset-class macro
    altassets fetch-all sources/series.yaml
    altassets train experiments/configs/baseline_cre.yaml
"""

from __future__ import annotations

import argparse

import yaml

from altassets import connectors
from altassets.data.store import Store
from altassets.taxonomy import AssetClass


def _fetch(name, series_id, start, end, asset_class, store):
    df, meta = connectors.get(name).fetch(
        series_id, start=start, end=end, asset_class=AssetClass(asset_class)
    )
    path = store.write(df, meta)
    print(f"{name}:{series_id}  {len(df)} rows -> {path}")


def main(argv=None):
    p = argparse.ArgumentParser(prog="altassets")
    p.add_argument("--store", default="data/curated")
    sub = p.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("fetch", help="fetch one series")
    f.add_argument("source")
    f.add_argument("series_id")
    f.add_argument("--start")
    f.add_argument("--end")
    f.add_argument("--asset-class", default="macro", choices=[a.value for a in AssetClass])

    fa = sub.add_parser("fetch-all", help="fetch every series listed in a YAML file")
    fa.add_argument("path")

    t = sub.add_parser("train", help="run an experiment config")
    t.add_argument("config")

    a = p.parse_args(argv)
    store = Store(a.store)
    if a.cmd == "fetch":
        _fetch(a.source, a.series_id, a.start, a.end, a.asset_class, store)
    elif a.cmd == "fetch-all":
        for s in yaml.safe_load(open(a.path))["series"]:
            try:
                _fetch(s["source"], s["id"], s.get("start"), s.get("end"),
                       s.get("asset_class", "macro"), store)
            except Exception as e:  # keep going; one dead series should not stop a refresh
                print(f"FAILED {s['source']}:{s['id']}: {e}")
    elif a.cmd == "train":
        from altassets.experiments.run import run

        r = run(a.config)
        print(f"val_mse={r['val_mse']:.4f}  n_train={r['n_train']}  n_val={r['n_val']}")


if __name__ == "__main__":
    main()
