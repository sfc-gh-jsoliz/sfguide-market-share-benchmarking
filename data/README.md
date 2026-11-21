# Synthetic data

Everything here is synthetic. `data/generate.py` (standard library only, fixed seed `20240731`) writes:

| File | Rows | What |
|---|---|---|
| `categories.csv` | 6 | MCC-aligned merchant categories mapped to US Census retail-sales variable codes |
| `book_monthly.csv` | 144 | The processor's processed volume, transactions and active merchants by category and month-end |
| `market_monthly.csv` | 144 | Market retail sales by category and month-end |

The same rows go into the generated block in `sql/setup.sql` and into `app/sample/` (Sample mode), so Sample and Live show identical numbers. Re-running the generator gives byte-identical files.

## How it is built

The drivers and formulas are the original pack's: 24 month-ends (Jul 2024 to Jun 2026), market sales growing linearly from a base level, and the processor's book growing linearly from a base share of that market. The v2 generator adds:

- a month-of-year seasonal factor (holiday lift in November and December, a January dip) applied to the book and the market alike, so share in basis points is unaffected;
- small fixed-seed noise on the book (plus or minus 0.6%) and on active merchants, replacing `RANDOM()` so the data is reproducible outside Snowflake.

Share is `processed_volume / market_sales x 10,000` (basis points; 100 bps = 1%). The growth gap is the book's year-over-year growth minus the market's, in percentage points. Status in `MARKET_SHARE_VERTICAL_SUMMARY` compares the 3-month average share at the start and end of the window: Gaining at +3% or more, Losing at -3% or less, Holding otherwise.

## Planted stories (on this synthetic data set)

| Vertical | Share, start to now (3-mo avg) | Latest growth gap | Status | Story |
|---|---|---|---|---|
| Restaurants & Food Service | 220.6 to 243.0 bps (+22.4) | +6.5 pp | Gaining | The book grows more than twice as fast as the restaurant market: the headline win. |
| Health & Personal Care | 139.7 to 145.8 bps (+6.0) | +2.8 pp | Gaining | Steady outgrowth. |
| Food & Beverage Stores | 119.9 to 124.8 bps (+4.9) | +1.6 pp | Gaining | Grows on a large market base, so a small bps gain is a lot of volume. |
| Furniture & Home Furnishings | 160.4 to 163.6 bps (+3.3) | +0.8 pp | Holding | Flat market; the book edges up but stays under the Gaining threshold. |
| Clothing & Accessories | 149.6 to 146.6 bps (-3.0) | -1.5 pp | Holding | Slipping slowly: growing, but slower than the market. A watch item. |
| Electronics & Appliances | 179.4 to 157.5 bps (-21.9) | -7.7 pp | Losing | The book shrinks while the market grows: the clear share loss. |

The numbers above are the Live output of `MARKET_SHARE_VERTICAL_SUMMARY` after `sql/setup.sql`.
