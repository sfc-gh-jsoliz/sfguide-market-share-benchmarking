-- ============================================================================
-- Market Share & Vertical Benchmarking — setup.sql  (DEPLOY mode: real market data)
-- ----------------------------------------------------------------------------
-- Benchmarks the processor's (synthetic) own book against REAL US Census
-- Advance Retail Sales by category, from the free Snowflake Marketplace
-- "Financial Data Package" (SNOWFLAKE_PUBLIC_DATA_FINANCIAL_PACKAGE).
--
-- A specific acquirer's processed volume has no public source, so MARKET_SHARE_PORTFOLIO_MONTHLY
-- is synthetic in both modes; here the MARKET side is REAL. To use your own book,
-- replace MARKET_SHARE_PORTFOLIO_MONTHLY with your settlement data (same columns) via Cortex Code.
--
-- Prereq: mount the free "Financial Data Package" listing from the Marketplace.
-- Run setup_synthetic.sql instead for a no-listing TRY.
-- ============================================================================

CREATE DATABASE IF NOT EXISTS SNOWPACK_MARKET_SHARE;
CREATE SCHEMA IF NOT EXISTS SNOWPACK_MARKET_SHARE.CORE
  COMMENT = 'Market Share & Vertical Benchmarking: merchant-category market-share benchmarking';
CREATE WAREHOUSE IF NOT EXISTS SNOWPACK_MARKET_SHARE_WH WITH WAREHOUSE_SIZE='XSMALL' AUTO_SUSPEND=60 AUTO_RESUME=TRUE INITIALLY_SUSPENDED=TRUE;
USE WAREHOUSE SNOWPACK_MARKET_SHARE_WH;
USE SCHEMA SNOWPACK_MARKET_SHARE.CORE;

-- 1. Category dim (MCC-aligned, mapped to Census variable codes) ---------------
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

CREATE OR REPLACE TEMP TABLE _drivers (category_code STRING, base_mkt_musd FLOAT, base_share FLOAT, port_g FLOAT, mkt_g FLOAT) AS
SELECT * FROM VALUES
  ('RESTAURANTS', 95000, 0.0220,  0.009, 0.004),
  ('APPAREL',     26000, 0.0150,  0.002, 0.003),
  ('ELECTRONICS',  8000, 0.0180, -0.004, 0.002),
  ('GROCERY',     85000, 0.0120,  0.006, 0.004),
  ('FURNITURE',   11000, 0.0160,  0.001, 0.000),
  ('HEALTH',      38000, 0.0140,  0.005, 0.003)
  AS d(category_code, base_mkt_musd, base_share, port_g, mkt_g);

CREATE OR REPLACE TEMP TABLE _months AS
SELECT LAST_DAY(DATEADD(month, SEQ4(), '2024-07-01')) AS month_end, SEQ4() AS m_idx
FROM TABLE(GENERATOR(ROWCOUNT => 24));

-- 2. Processor's own book (synthetic; swap for your settlement data) -----------
CREATE OR REPLACE TABLE MARKET_SHARE_PORTFOLIO_MONTHLY
  COMMENT = 'SYNTHETIC: this processor''s processed volume by merchant category and month. Replace with your own settlement data (same columns) to go live.'
AS
SELECT c.category_code, c.category_name, m.month_end,
       ROUND(d.base_mkt_musd * 1e6 * d.base_share * (1 + d.port_g * m.m_idx), 0) AS processed_volume_usd,
       ROUND(d.base_mkt_musd * 1e6 * d.base_share * (1 + d.port_g * m.m_idx) / 72.0, 0) AS txn_count,
       (500 + UNIFORM(1, 40, RANDOM(42)) + m.m_idx*3) AS active_merchants
FROM MARKET_SHARE_MERCHANT_CATEGORY c JOIN _drivers d USING (category_code) CROSS JOIN _months m;

-- 3. Market side — REAL US Census Advance Retail Sales (deduped to latest vintage)
CREATE OR REPLACE VIEW MARKET_SHARE_RETAIL_SALES
  COMMENT = 'REAL market retail sales by category, from SNOWFLAKE_PUBLIC_DATA_FINANCIAL_PACKAGE (US Census Advance Retail Sales, seasonally adjusted, USD).'
AS
WITH ts AS (
  SELECT variable, date,
         ROW_NUMBER() OVER (PARTITION BY variable, date ORDER BY _EFFECTIVE_START_TIMESTAMP DESC) AS rn,
         value
  FROM SNOWFLAKE_PUBLIC_DATA_FINANCIAL_PACKAGE.COMMERCIAL_BANKING.FINANCIAL_ECONOMIC_INDICATORS_TIMESERIES_PIT
  WHERE variable IN (SELECT census_variable FROM MARKET_SHARE_MERCHANT_CATEGORY)
)
SELECT c.category_code, c.category_name, ts.date AS month_end, ts.value AS market_sales_usd
FROM ts JOIN MARKET_SHARE_MERCHANT_CATEGORY c ON c.census_variable = ts.variable
WHERE ts.rn = 1;

-- 4. Benchmark view (identical to synthetic) ----------------------------------
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
SELECT 'marketplace' AS mode,
       'Synthetic processor book benchmarked against REAL US Census Advance Retail Sales (free Financial Data Package listing).' AS note;

-- 6. Semantic view (identical to synthetic) -----------------------------------
CREATE OR REPLACE SEMANTIC VIEW MARKET_SHARE_SV
  TABLES ( ms AS SNOWPACK_MARKET_SHARE.CORE.MARKET_SHARE_BENCHMARK PRIMARY KEY (category_code, month_end)
           WITH SYNONYMS = ('market share','portfolio vs market','benchmark')
           COMMENT = 'Processor processed volume vs market retail sales by merchant category and month' )
  FACTS (
    ms.processed_volume_usd AS PROCESSED_VOLUME_USD, ms.market_sales_usd AS MARKET_SALES_USD,
    ms.share_bps AS SHARE_BPS, ms.txn_count AS TXN_COUNT, ms.active_merchants AS ACTIVE_MERCHANTS
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
  COMMENT = 'Market-share benchmarking semantic view (synthetic book vs REAL Census market).';

-- 7. Output table + agent (identical to synthetic) ----------------------------
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
        description: 'Processor processed volume vs real market retail sales by merchant category and month (share in bps).'
  tool_resources:
    MarketShare:
      semantic_view: SNOWPACK_MARKET_SHARE.CORE.MARKET_SHARE_SV
  $$;
