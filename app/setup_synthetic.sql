-- ============================================================================
-- Market Share & Vertical Benchmarking — setup_synthetic.sql  (TRY mode: no listing needed)
-- ----------------------------------------------------------------------------
-- Market Share & Vertical Benchmarking for a payments processor / acquirer.
-- Benchmarks a processor's own processed volume by merchant category against
-- the market (US Census Advance Retail Sales by category).
--
-- A processor's OWN book is always synthetic here (there is no public source of
-- a specific acquirer's volume). In TRY mode the MARKET side is synthetic too,
-- so nothing external is needed. In DEPLOY mode (setup.sql) the MARKET side is
-- REAL Census retail sales from the free Marketplace "Financial Data Package".
--
-- Objects in SNOWPACK_MARKET_SHARE.CORE:
--   MARKET_SHARE_MERCHANT_CATEGORY (dim), MARKET_SHARE_PORTFOLIO_MONTHLY (synthetic own-book volume),
--   MARKET_SHARE_RETAIL_SALES (synthetic market here / real view in setup.sql),
--   MARKET_SHARE_BENCHMARK (benchmark view), MARKET_SHARE_SV (semantic view),
--   MARKET_SHARE_REPORTS, MARKET_SHARE_DATA_SOURCE_INFO, MARKET_SHARE_AGENT.
-- ============================================================================

CREATE DATABASE IF NOT EXISTS SNOWPACK_MARKET_SHARE;
CREATE SCHEMA IF NOT EXISTS SNOWPACK_MARKET_SHARE.CORE
  COMMENT = 'Market Share & Vertical Benchmarking: merchant-category market-share benchmarking';
CREATE WAREHOUSE IF NOT EXISTS SNOWPACK_MARKET_SHARE_WH WITH WAREHOUSE_SIZE='XSMALL' AUTO_SUSPEND=60 AUTO_RESUME=TRUE INITIALLY_SUSPENDED=TRUE;
USE WAREHOUSE SNOWPACK_MARKET_SHARE_WH;
USE SCHEMA SNOWPACK_MARKET_SHARE.CORE;

-- 1. Category dimension: MCC-aligned merchant categories mapped to Census codes --
CREATE OR REPLACE TABLE MARKET_SHARE_MERCHANT_CATEGORY (
  category_code STRING, category_name STRING, mcc STRING, census_variable STRING
);
INSERT INTO MARKET_SHARE_MERCHANT_CATEGORY VALUES
  ('RESTAURANTS','Restaurants & Food Service','5812','ADV_722SM_SA'),
  ('APPAREL','Clothing & Accessories','5651','ADV_448SM_SA'),
  ('ELECTRONICS','Electronics & Appliances','5732','ADV_443SM_SA'),
  ('GROCERY','Food & Beverage Stores','5411','ADV_445SM_SA'),
  ('FURNITURE','Furniture & Home Furnishings','5712','ADV_442SM_SA'),
  ('HEALTH','Health & Personal Care','5912','ADV_446SM_SA');

-- Per-category synthetic drivers (deterministic, no RANDOM):
--   base_mkt_musd = market monthly sales ($M, ~real magnitudes)
--   base_share    = processor's starting share of that category
--   port_g / mkt_g= monthly growth of the processor's book vs the market
CREATE OR REPLACE TEMP TABLE _drivers (category_code STRING, base_mkt_musd FLOAT, base_share FLOAT, port_g FLOAT, mkt_g FLOAT) AS
SELECT * FROM VALUES
  ('RESTAURANTS', 95000, 0.0220,  0.009, 0.004),   -- gaining share
  ('APPAREL',     26000, 0.0150,  0.002, 0.003),   -- flat/slightly losing
  ('ELECTRONICS',  8000, 0.0180, -0.004, 0.002),   -- losing share
  ('GROCERY',     85000, 0.0120,  0.006, 0.004),   -- gaining
  ('FURNITURE',   11000, 0.0160,  0.001, 0.000),   -- holding
  ('HEALTH',      38000, 0.0140,  0.005, 0.003)    -- gaining
  AS d(category_code, base_mkt_musd, base_share, port_g, mkt_g);

-- 24 months ending 2026-06-30 (month-end dates)
CREATE OR REPLACE TEMP TABLE _months AS
SELECT DATEADD(month, SEQ4(), '2024-07-01')::date AS month_start,
       LAST_DAY(DATEADD(month, SEQ4(), '2024-07-01')) AS month_end,
       SEQ4() AS m_idx
FROM TABLE(GENERATOR(ROWCOUNT => 24));

-- 2. Processor's own book (synthetic, absolute USD) ---------------------------
CREATE OR REPLACE TABLE MARKET_SHARE_PORTFOLIO_MONTHLY
  COMMENT = 'SYNTHETIC: this processor''s processed volume by merchant category and month.'
AS
SELECT c.category_code, c.category_name, m.month_end,
       ROUND(d.base_mkt_musd * 1e6 * d.base_share * (1 + d.port_g * m.m_idx), 0) AS processed_volume_usd,
       ROUND(d.base_mkt_musd * 1e6 * d.base_share * (1 + d.port_g * m.m_idx) / 72.0, 0) AS txn_count,
       (500 + UNIFORM(1, 40, RANDOM(42)) + m.m_idx*3) AS active_merchants
FROM MARKET_SHARE_MERCHANT_CATEGORY c
JOIN _drivers d USING (category_code)
CROSS JOIN _months m;

-- 3. Market side — SYNTHETIC in TRY mode (real Census view in setup.sql) -------
CREATE OR REPLACE TABLE MARKET_SHARE_RETAIL_SALES
  COMMENT = 'SYNTHETIC market retail sales by category. setup.sql replaces this with real Census data.'
AS
SELECT c.category_code, c.category_name, m.month_end,
       ROUND(d.base_mkt_musd * 1e6 * (1 + d.mkt_g * m.m_idx), 0) AS market_sales_usd
FROM MARKET_SHARE_MERCHANT_CATEGORY c
JOIN _drivers d USING (category_code)
CROSS JOIN _months m;

-- 4. Benchmark view: share + growth gap ---------------------------------------
CREATE OR REPLACE VIEW MARKET_SHARE_BENCHMARK
  COMMENT = 'Processor volume vs market retail sales by category and month: share (bps) and growth gap.'
AS
SELECT p.category_code, p.category_name, p.month_end,
       p.processed_volume_usd, m.market_sales_usd,
       ROUND(p.processed_volume_usd / NULLIF(m.market_sales_usd,0) * 10000, 2) AS share_bps,
       p.txn_count, p.active_merchants
FROM MARKET_SHARE_PORTFOLIO_MONTHLY p
JOIN MARKET_SHARE_RETAIL_SALES m USING (category_code, category_name, month_end);

-- 5. Data-source marker -------------------------------------------------------
CREATE OR REPLACE VIEW MARKET_SHARE_DATA_SOURCE_INFO AS
SELECT 'synthetic' AS mode,
       'Synthetic processor book AND synthetic market (no Marketplace listing required). Run setup.sql to benchmark the synthetic book against REAL US Census retail sales (free Financial Data Package listing).' AS note;

-- 6. Semantic view ------------------------------------------------------------
CREATE OR REPLACE SEMANTIC VIEW MARKET_SHARE_SV
  TABLES ( ms AS SNOWPACK_MARKET_SHARE.CORE.MARKET_SHARE_BENCHMARK PRIMARY KEY (category_code, month_end)
           WITH SYNONYMS = ('market share','portfolio vs market','benchmark')
           COMMENT = 'Processor processed volume vs market retail sales by merchant category and month' )
  FACTS (
    ms.processed_volume_usd AS PROCESSED_VOLUME_USD,
    ms.market_sales_usd AS MARKET_SALES_USD,
    ms.share_bps AS SHARE_BPS,
    ms.txn_count AS TXN_COUNT,
    ms.active_merchants AS ACTIVE_MERCHANTS
  )
  DIMENSIONS (
    ms.category_name AS CATEGORY_NAME WITH SYNONYMS = ('merchant category','vertical','segment') COMMENT = 'Merchant category (MCC-aligned)',
    ms.category_code AS CATEGORY_CODE,
    ms.month_end AS MONTH_END WITH SYNONYMS = ('month','period','as of'),
    ms.report_year AS YEAR(MONTH_END) WITH SYNONYMS = ('year')
  )
  METRICS (
    ms.total_processed_usd AS SUM(ms.processed_volume_usd) COMMENT = 'Total processed volume (USD)',
    ms.total_market_usd AS SUM(ms.market_sales_usd) COMMENT = 'Total market retail sales (USD)',
    ms.avg_share_bps AS AVG(ms.share_bps) COMMENT = 'Average market share in basis points',
    ms.total_txns AS SUM(ms.txn_count) COMMENT = 'Total transactions'
  )
  COMMENT = 'Market-share benchmarking semantic view (synthetic book vs market retail sales).';

-- 7. Output table + agent -----------------------------------------------------
CREATE TABLE IF NOT EXISTS MARKET_SHARE_REPORTS (
  run_id STRING DEFAULT UUID_STRING(), subject STRING, draft_md STRING, report_md STRING,
  status STRING, edits_applied INT, residual_hedges INT, created_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE OR REPLACE AGENT MARKET_SHARE_AGENT
  COMMENT = 'Market Share & Vertical Benchmarking agent (Cortex Analyst over MARKET_SHARE_SV)'
  PROFILE = '{"display_name": "Market Share Agent", "color": "blue"}'
  FROM SPECIFICATION
  $$
  models:
    orchestration: auto
  instructions:
    response: 'You are a payments-portfolio analyst. Use ONLY figures from the Analyst tool. share_bps is basis points (100 bps = 1%). Express USD in $B/$M. Never invent numbers. Be concise and cite the month.'
    orchestration: 'For any volume, market, share, or growth question use the MarketShare Analyst tool.'
    sample_questions:
      - question: 'Which merchant categories are gaining market share in 2026?'
  tools:
    - tool_spec:
        type: cortex_analyst_text_to_sql
        name: MarketShare
        description: 'Processor processed volume vs market retail sales by merchant category and month (share in bps).'
  tool_resources:
    MarketShare:
      semantic_view: SNOWPACK_MARKET_SHARE.CORE.MARKET_SHARE_SV
  $$;
