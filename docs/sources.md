# Public data source map

What we can get, for which asset class, and on what terms. "Access" is how the data
is delivered; "Terms" is what we may do with it. Rule of thumb: build a connector only
where there is an API or a published bulk download, the terms allow automated
access, and robots.txt does not disallow the path. Where data sits behind a
membership or in PDFs only, it goes in the "manual / licence needed" column.

Terms below are a working summary from each provider's public terms as of
October 2026. Re-read the actual terms page before building a connector or publishing
anything derived from the data.

Status key: **built** = connector in `src/altassets/connectors`, **next** = good
candidate for the next connector, **manual** = no automated route, **licence** = paid
or members-only.

## Central banks and official statistics (the backbone)

| Source | Asset classes | Access | Terms | Status |
|---|---|---|---|---|
| ECB Data Portal (SDMX API) | Rates, FX, bank lending rates and volumes (MIR, BSI), Bank Lending Survey, residential and commercial property indicators | REST API, CSV/JSON, no key | Free reuse with attribution | **built** (`ecb`) |
| Bank of England IADB | Rates, SONIA, lending to commercial real estate, mortgage approvals | CSV download, no key | Free reuse with attribution (BoE terms) | **built** (`boe`) |
| FRED (St. Louis Fed) | US rates, CRE loans and delinquency, credit spreads, BIS property prices re-hosted | REST API, free key | Free; some series owned by third parties (ICE BofA, S&P) with redistribution limits | **built** (`fred`) |
| Federal Reserve Board DDP | Z.1 Financial Accounts (commercial mortgages by holder), H.8 bank balance sheets, SLOOS (CRE and C&I lending standards) | CSV bulk download | Public domain (US government) | **next** |
| FDIC / FFIEC Call Reports | Bank CRE, construction and C&I loan books, non-accruals | Bulk download (FFIEC CDR), FDIC BankFind API | Public domain | **next** |
| BIS Data Portal | Commercial and residential property prices, credit to non-financial sector, debt securities | SDMX API, no key | Free with attribution | **next** |
| ESRB / EBA | EU CRE risk dashboards, bank exposures to CRE and leveraged finance | XLSX/CSV downloads | Free with attribution | manual to next |
| IMF / OECD | Macro, rates, house prices, infrastructure investment | SDMX APIs | Free with attribution (check per dataset) | next |
| World Bank PPI database | Infrastructure debt and equity: private participation in infrastructure projects | Bulk download | CC BY 4.0 | **next** |
| Eurostat | Construction output, building permits, macro | SDMX API | Free reuse with attribution | next |

## Regulatory filings (the best free private-markets data)

| Source | Asset classes | Access | Terms | Status |
|---|---|---|---|---|
| SEC EDGAR XBRL API | Private credit via BDC filings (loan books, fair values, non-accruals); non-traded REIT and infrastructure fund NAVs; listed alt managers (Blackstone, KKR, Apollo, Ares, Brookfield, Blue Owl) | JSON API, no key | Public domain; fair-access policy: named User-Agent with contact, max 10 req/s | **built** (`sec`) |
| SEC EDGAR ABS-EE | Commercial mortgages: loan-level CMBS data (balances, DSCR, LTV, delinquency) | XML exhibits in filings | Public domain; same fair-access policy | **next**, high value |
| SEC Form PF statistics / Form ADV | Private funds aggregate statistics, adviser AUM | CSV/XLSX downloads | Public domain | next |
| UK FCA / Companies House | UK fund and SPV filings | API (Companies House, free key) | Open Government Licence | later |

## Industry bodies and think tanks

| Source | Asset classes | Access | Terms | Status |
|---|---|---|---|---|
| NCREIF (NPI, ODCE) | US private real estate equity | Quarterly index results for members; public snapshots and press releases | Members-only data; public snapshots limited | **licence** |
| INREV | European non-listed real estate funds | Index and reports mostly for members; some public summaries | Members-only | **licence** |
| MSCI Real Assets / RCA | Real estate transactions and indices | Paid | Commercial licence | **licence** (check Bloomberg) |
| Nareit | Listed real estate (FTSE Nareit indices) | Public historical index spreadsheets on reit.com | Check reit.com terms before automating | manual, then next if allowed |
| EDHECinfra / SIPA (infraMetrics) | Infrastructure equity and debt indices | Subscription; research papers public | Commercial licence for index data | **licence** |
| GIIA | Infrastructure investor surveys and reports | PDF reports | Read and cite; no bulk data | manual |
| ILPA | Private equity reporting templates and principles | PDFs and templates | No performance data | manual |
| Cambridge Associates | PE and VC benchmark summaries | Quarterly public PDF summaries | Cite only | manual |
| LSTA | Leveraged and syndicated loans | Members; the main loan index is Morningstar LSTA (PitchBook LCD) | Commercial licence | **licence** (check Bloomberg) |
| MBA (Mortgage Bankers Association) | Commercial and multifamily origination index, CMBS delinquency | Headline numbers in public press releases; full data for members | Members-only for series | manual |
| Kenneth French Data Library | Public equity factors and portfolios | CSV/ZIP downloads | Free for research | **next** |

## Asset managers

Listed alternative managers (Blackstone, KKR, Apollo, Ares, Brookfield, Blue Owl,
Carlyle, TPG) and their public vehicles (BREIT, BCRED, ARCC, OBDC and others) report
through EDGAR, so the `sec` connector covers the structured part. Market-outlook PDFs
and research pages (CBRE, JLL, Cushman, PGIM, Nuveen and others) usually carry terms
that forbid scraping or commercial reuse. Treat them as manual reading. If we want text
from them for NLP features, store links and our own notes, not bulk copies, unless
the terms allow it.

## Bloomberg

There is no cloud connector. The Desktop API (`blpapi`) only talks to a running,
logged-in Terminal on the same machine, and Terminal data is licensed for the user's own
use. See [bloomberg.md](bloomberg.md) for the local adapter plan. Bloomberg is the
practical route to most of the **licence** rows above (loan indices, MSCI/RCA, NCREIF
where carried, CMBS analytics).

## Coverage by asset class

| Asset class | Best free sources | Gaps that need a licence or Bloomberg |
|---|---|---|
| Real estate equity | BIS and ECB property prices, EDGAR (REITs, non-traded REIT NAVs), Nareit | NCREIF, INREV, MSCI |
| Infrastructure equity | EDGAR (listed infra, Brookfield), World Bank PPI | EDHECinfra/SIPA |
| Public equity | Ken French library, EDGAR fundamentals | Daily prices and index levels (Bloomberg) |
| Private equity | EDGAR (listed GPs, Form PF stats), Cambridge Associates public summaries | Preqin, PitchBook, Burgiss/MSCI |
| Infrastructure debt | World Bank PPI, EDGAR | EDHECinfra debt indices, IJGlobal |
| Illiquid term loans | EDGAR BDC schedules, SLOOS, Call Reports | Cliffwater Direct Lending Index |
| Private liquid loans | FRED credit spreads, EDGAR BDCs | Morningstar LSTA loan index, LCD |
| Commercial mortgages | Fed Z.1, FRED, Call Reports, EDGAR ABS-EE (CMBS loan level), ECB/BoE CRE lending | Trepp, MBA series |
