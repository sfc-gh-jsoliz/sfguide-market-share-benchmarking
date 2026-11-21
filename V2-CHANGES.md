# v2 changes: Market Share & Vertical Benchmarking

This branch (`v2-rebuild` on the fork `sfc-gh-ooral/sfguide-market-share-benchmarking`) brings the pack up to the Snow Packs v2 bar. It keeps your data stories, features, stack (Streamlit + SQL + notebook) and owner line. Nothing was pushed to your repository.

## What changed, screen by screen

### App shell (new)
- Before: one Streamlit page with a title, a mode banner and a sidebar button.
- Now: a branded left rail (logo, the plain app name "Market Share & Vertical Benchmarking", five sections, a Sample/Live switch, a role chip and an environment badge). Design tokens, palette and type are in `docs/DESIGN.md` (espresso rail, fuchsia brand, ochre accent; checked for WCAG AA).
- Code split into `app/data.py` (Sample CSVs or Live Snowpark, no fallback), `app/ai.py`, `app/brand.py` and `app/views/`.
- Live mode locally uses key-pair auth from three environment variables; in Streamlit in Snowflake it uses the app's session. If Live is picked with no connection, the app shows the setup steps instead of sample data.

### Overview (new)
- KPI tiles with sparklines and a count-up: book share in bps, processed volume, verticals gaining share, widest growth gap.
- The share ribbon: a slope chart of each vertical's share at the start vs now (3-month averages), with tooltips.
- Gainers and losers list with status pills, and a one-line insight.

### Verticals (was the latest-month table)
- Sortable, filterable table (status chips, search) with an inline share bar; selecting a row opens share history, indexed growth vs the market, and the monthly figures.

### Growth gap (new)
- Diverging bars of the YoY growth gap per vertical, a four-box read-out, and the growth gap over time. The gap is now a column in `MARKET_SHARE_BENCHMARK` (`LAG(..., 12)`), so Live and Sample compute it the same way.

### Share notes (was the sidebar button and card gallery)
- Pick the whole book or one vertical. Staged progress steps, a streaming reveal, the Verified / Needs review badge, the verifier's flagged claims, and the fact pack shown as sources.
- The fact pack now carries pre-formatted `*_display` figures from SQL and the verifier compares them character for character; status is derived in code from the verifier's edits and hedge count. All 7 captured notes ran live; 6 came back Verified and 1 Needs review (the Furniture note called a Holding vertical a gainer), which is kept as an honest example.
- `MARKET_SHARE_REPORTS` gains `scope`, `edits`, `fact_pack`, `model` and `latency_ms` columns (added with `ADD COLUMN IF NOT EXISTS`, so existing rows survive).

### Ask an analyst (new in the app)
- The Cortex Agent was Snowsight-only before; the app now calls it with `DATA_AGENT_RUN` and shows the answer, the SQL Cortex Analyst wrote, and the result rows.

### Data and SQL
- `data/generate.py`: a seeded, standard-library generator using your drivers and formulas. It adds a seasonal factor applied equally to book and market (so share is unaffected) and small fixed-seed noise in place of `RANDOM()`. It writes the CSVs and the INSERT block in `sql/setup.sql`. Planted stories are documented in `data/README.md`.
- `sql/setup.sql` (replaces `app/setup_synthetic.sql`): creates a least-privilege role `MARKET_SHARE_ROLE` and runs everything else as that role; adds `MARKET_SHARE_VERTICAL_SUMMARY`, growth columns in the benchmark view and an `APP_STAGE`.
- `sql/setup_census.sql` (replaces `app/setup.sql`): run after `setup.sql` to swap the market side for US Census retail sales. It keeps your query, adds `LAST_DAY()` on the Census date so months join to month-end, and grants the listing to the pack role. Not re-verified in this build because the listing wasn't mounted in the test account.
- `sql/cleanup.sql` (replaces `app/teardown.sql`): also drops the role, and drops objects as the owning role first.

### Hosted example and landing page
- `docs/try/`: a dependency-free copy of the app (hash routing, SVG charts with tooltips, a vertical drawer, replayed AI), built with `npm run build:example`, which also writes `docs/.nojekyll`.
- `docs/index.html`: a new landing page in the same brand, with the share ribbon as the hero, captioned Live screenshots, a capability table, cost and setup.
- `docs/images/` (landing screenshots) and `docs/catalog/` (960x600 catalog cards).
- The old root `index.html` and `try/index.html` are now redirect stubs to `docs/`, so your current Pages URLs keep working until you switch Pages. `styles.css` and `assets/` were removed.

### Notebook
- Only the prerequisite line changed (new script names and the pack role).

## What was verified live

In a test Snowflake account with key-pair auth: `sql/setup.sql` ran twice in a row (about 16 s each), every screen ran in Live mode, the Live numbers equal the Sample numbers exactly (all benchmark and summary columns), 7 share notes and 5 agent questions ran live from the app and the capture script, and `sql/cleanup.sql` removed the database, warehouse and role (confirmed with `SHOW` commands).

## After you merge

1. Merge `v2-rebuild` into your `main` (fast-forward is possible if you haven't pushed to `main` since the fork).
2. In **Settings > Pages**, change the source to `main` and folder `/docs`. The guide is then at your existing URL and the example at `/try/`. The root redirect stubs can stay or go.
3. Wait for the Pages build, then check that `/try/` loads and that `try/app.js`, `try/app.css`, `try/data.js` and `assets/tokens.css` return 200.
4. Optional: turn on **Settings > Template repository** and add topics (`snowflake`, `financial-services`, `payments`, `cortex`, `streamlit`).
5. Tell the catalog maintainer, so the Snow Packs entry and its card images can be updated (the new cards are in `docs/catalog/`).

To keep it v2-ready later, give your CoCo `COCO-V2-INSTRUCTIONS.md`.
