# Market Share & Vertical Benchmarking

Benchmark a payments processor's processed volume by merchant category against the real US retail market, expressed as market share in basis points with a growth gap.

Owner: Javier Soliz · Last reviewed: November 2026

## What it shows

A payments processor strategy / benchmarking team wants to know where it is gaining or losing share by merchant vertical — not just whether its own volume is growing. This pack benchmarks a (synthetic) processor book against real market retail sales by category and surfaces:

- A latest-month table of processed volume, market sales, and **share in basis points** per merchant category (restaurants, apparel, electronics, grocery, furniture, health).
- A card gallery of generated share notes, each badged **Verified** or **Needs review**.
- A Streamlit sidebar that runs the full workflow and writes a new share note grounded only in the governed benchmark data.

## How it works

- A benchmark view joins the processor's monthly processed volume to market retail sales by category and month, computing `share_bps = processed_volume / market_sales × 10,000` and a growth gap.
- In **DEPLOY** mode the market side is the **real, free US Census Advance Retail Sales** data from the Snowflake Marketplace "Financial Data Package". In **sample mode** the market side is fully synthetic, so no listing is required. The processor's own book is synthetic in both modes (a specific acquirer's volume has no public source).
- The Streamlit app calls Snowflake Cortex `AI_COMPLETE` to draft a one-page share note under strict data rules (copy figures exactly, no estimates, no outside benchmarks), then a second `AI_COMPLETE` pass verifies each claim against the benchmark facts and flags the note Verified or Needs review.
- Setup also creates a **Cortex Analyst semantic view** and a **Cortex Agent** over the benchmark data. These are explorable in Snowsight (Agents / Analyst) for natural-language questions — they are **not** called by the Streamlit app.

## Prerequisites

- A Snowflake account.
- Snowflake Enterprise Edition or higher, in a region where Cortex AISQL and Cortex Agents are available.
- A role that can `CREATE DATABASE` and `CREATE WAREHOUSE` (setup builds its own dedicated database and warehouse).
- Snowflake Cortex available in your region (the app uses `AI_COMPLETE`; the Cortex Agent and Analyst objects also require Cortex).
- Streamlit in Snowflake to run the app.
- Sample mode is fully synthetic and needs no external data. DEPLOY mode uses the free, public US Census retail-sales data from the Marketplace "Financial Data Package" listing.

## Setup

1. **Sample (synthetic) mode:** run [`app/setup_synthetic.sql`](app/setup_synthetic.sql). Builds every object on synthetic category data — no Marketplace listing required.
2. **Deploy (real market) mode:** in Snowsight → Marketplace, get the free **Financial Data Package** (`SNOWFLAKE_PUBLIC_DATA_FINANCIAL_PACKAGE`), then run [`app/setup.sql`](app/setup.sql).
3. **Deploy the app:** create the stage and the Streamlit in Snowflake **inside `SNOWPACK_MARKET_SHARE.CORE`** (upload [`app/streamlit_app.py`](app/streamlit_app.py) to a stage in that schema and `CREATE STREAMLIT` there, or create a new Streamlit in Snowsight with `SNOWPACK_MARKET_SHARE.CORE` as its location). Keeping both in this schema means [`app/teardown.sql`](app/teardown.sql) removes them with the database.
4. **Explore the agent (optional):** Snowsight → AI & ML → Agents → **Market Share Agent**.

Both scripts create the identical objects in `SNOWPACK_MARKET_SHARE.CORE`, so the app, semantic view, and agent behave the same between modes.

## Objects created

| Object | Type | Purpose |
|---|---|---|
| `SNOWPACK_MARKET_SHARE` | Database | Dedicated, isolated home for this pack |
| `SNOWPACK_MARKET_SHARE.CORE` | Schema | Holds all tables, views, and AI objects |
| `SNOWPACK_MARKET_SHARE_WH` | Warehouse (XSMALL) | Dedicated compute; auto-suspend 60s |
| `MARKET_SHARE_MERCHANT_CATEGORY` | Table | Merchant-category dimension (MCC-aligned, mapped to Census variable codes) |
| `MARKET_SHARE_PORTFOLIO_MONTHLY` | Table | Synthetic processor processed volume by category and month |
| `MARKET_SHARE_RETAIL_SALES` | Table (sample) / View (deploy) | Market retail sales by category — synthetic in sample mode, real US Census in deploy mode |
| `MARKET_SHARE_BENCHMARK` | View | Processor volume vs market sales: share in bps and growth gap |
| `MARKET_SHARE_DATA_SOURCE_INFO` | View | Marker indicating synthetic vs real market mode |
| `MARKET_SHARE_SV` | Semantic view | Governed business meaning for Cortex Analyst |
| `MARKET_SHARE_REPORTS` | Table | Persisted generated share notes and verifier status |
| `MARKET_SHARE_AGENT` | Cortex Agent | Natural-language Q&A over the semantic view (Snowsight only) |
| Streamlit app | Streamlit in Snowflake | The benchmarking UI with grounded draft + verifier |

## Cost & time

Setup runs in a few minutes on an XSMALL warehouse. Data volumes are tiny (six categories × 24 months). Costs are warehouse compute plus Cortex `AI_COMPLETE` calls when you generate or verify a share note in the app.

## Customize with Cortex Code

Use Cortex Code to adapt this pack to your own market-share questions. Try prompts like:

- "Add two merchant categories (e.g. Sporting Goods and Building Materials) to `MARKET_SHARE_MERCHANT_CATEGORY`, map them to the right US Census variable codes, and extend the synthetic portfolio and benchmark so share in bps is computed for them too."
- "Change the benchmark window from 24 months to 36 months and recompute the growth gap as the share change over the full window."
- "Rewrite the grounded draft and verifier prompts in `app/streamlit_app.py` to report quarter-over-quarter share change instead of start-to-now, keeping the same copy-figures-exactly data rules."

## Known limitations

- The processor's own book is synthetic in both modes; there is no public source for a specific acquirer's processed volume.
- The market benchmark is at category / month granularity (US Census Advance Retail Sales); no metro or SKU detail.
- The browser Try page is a static illustration with mocked AI responses, not live inference.
- Illustrative example only — not production-ready and not an official Snowflake product.

## Cleanup

Run [`app/teardown.sql`](app/teardown.sql) to drop the dedicated database and warehouse this pack created.

## Learn more

- [Snowflake Cortex AISQL (`AI_COMPLETE`)](https://docs.snowflake.com/en/user-guide/snowflake-cortex/aisql)
- [Cortex Agents](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents)
- [Cortex Analyst](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst)
- [Streamlit in Snowflake](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)

## License

Apache 2.0 (see [`LICENSE`](LICENSE)). Illustrative example, as-is, not supported by Snowflake Support. This is not an official Snowflake product. Review and test before any production use.
