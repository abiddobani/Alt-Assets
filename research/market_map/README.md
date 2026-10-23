# Alternative assets market map

A working table of the eight asset classes, their main subgroups, market size, duration,
long-run return and fees. It is meant to be revised over several rounds.

- [`market_map.md`](market_map.md): the readable table (generated; do not edit by hand)
- [`market_map.csv`](market_map.csv): the source of truth, one row per subgroup
- [`sources.csv`](sources.csv): every source cited, by ID
- [`build.py`](build.py): rebuilds the view, and optionally an Excel copy

## How to revise

1. Edit `market_map.csv` (any spreadsheet tool works). Change `g20_size_usd_bn`, not
   `share_of_group_pct`: the share is recomputed from the sizes on every build.
2. Add any new source to `sources.csv` and cite its ID in the row's `sources` column.
3. Remove a field's name from `estimated_fields` once it is backed by a hard source.
4. Run `python research/market_map/build.py` (add `--xlsx out.xlsx` for an Excel copy).

## What each column means

| Column | Definition used in this draft |
|---|---|
| Equity / Debt | Abid's top-level split |
| Asset class | The eight classes in `src/altassets/taxonomy.py` |
| Subgroup | The main way the market is cut for that class: sector for real estate, infrastructure and public equity; strategy for private equity and private credit; rating for liquid loans; lender type for commercial mortgages |
| % of asset class | Subgroup's share of the asset class's G20 size |
| G20 size | USD bn, assets located in G20 countries (19 members plus the EU). Where only a global figure exists it is scaled by a G20 share: real estate 95%, public equity 93%, infrastructure 93%, private equity 95%, private credit 97% |
| Canada size | USD bn, assets located in Canada (not Canadian investors' holdings abroad). CAD converted at ~1.37 per USD (approx. end-2025) |
| Duration | How long cash flows are locked in: lease length (WALE) for real estate, contract or concession life for infrastructure equity, holding period for private equity, weighted-average life for debt. Public equity is perpetual, so it shows implied duration ≈ forward P/E |
| 20-yr return | Annualised total return over roughly 2006-2025. Each row says whether it is gross or net of fees: private-fund IRRs (PE, VC, infra equity, distressed) are net; indices are gross |
| Fees | Typical management fee / performance fee for fund access. "Commitments" means charged on committed capital, "invested" on deployed capital, "NAV" on net asset value |

Extra columns in the CSV: current or long-run cash yield, the basis for each figure, a
confidence rating for the size, the sources, and notes. `duration_check` and
`duration_evidence` record how each duration was checked against a published source
(Confirmed, Changed, Partly verified, Not verified); the view lists them under
"Duration check". Where MBA maturity data is used, a share f of balances maturing in one
year is read as an average loan term of roughly 1/f years.

## Known gaps (first draft, 23 Oct 2026)

- **Estimates.** Most subgroup splits, all Canada sizes except public equity, all
  durations and fees, and most 20-yr returns are estimates. Hard figures so far: the
  asset-class totals for real estate, public equity, private equity, US commercial
  mortgages and leveraged loans; office and industrial shares; ACWI sector weights;
  Cambridge Associates PE and VC returns; Cliffwater's 20-yr direct lending return;
  NCREIF income yields.
- **Infrastructure equity** counts unlisted fund AUM only (USD 1.6tn incl. debt funds).
  Listed infrastructure and direct holdings by pension and sovereign funds are excluded,
  so this understates the investable market.
- **Infrastructure debt** total (~USD 4.5tn global) is derived from annual issuance and
  average loan life. It needs a stock figure (IJGlobal, BIS or EDHECinfra).
- **Commercial mortgages** outside the US are estimated country by country. China
  developer loans (~USD 1.9tn) are left out.
- **Canada private markets** sizes are rough. Candidate sources: Bank of Canada and OSFI
  (commercial real estate debt), CVCA (PE and venture AUM), Canadian P3 project lists.

## Next round

The 20-yr returns can be replaced with computed figures from the local Bloomberg
series on Abid's machine (Morningstar LSTA loans, CMBS, FTSE Nareit, NCREIF NPI and
ODCE, RCA CPPI, S&P Global Infrastructure, LPX50, Cliffwater). The raw Bloomberg data
stays on that machine under the Terminal licence; only summary averages would come back
into this table, and only if the licence allows it.
