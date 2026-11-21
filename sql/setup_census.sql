-- ============================================================================
-- Market Share & Vertical Benchmarking - sql/setup_census.sql  (optional)
-- ----------------------------------------------------------------------------
-- Run AFTER sql/setup.sql to benchmark the same synthetic processor book
-- against US Census Advance Retail Sales by category (seasonally adjusted, USD)
-- from the free Snowflake Marketplace "Financial Data Package" listing
-- (database SNOWFLAKE_PUBLIC_DATA_FINANCIAL_PACKAGE). Get the listing first.
--
-- The processor's own book stays synthetic: a specific acquirer's volume has no
-- public source. Replace MARKET_SHARE_PORTFOLIO_MONTHLY with your settlement
-- data (same columns) to benchmark your own book.
--
-- Not re-verified in the v2 rebuild (the listing was not mounted in the test
-- account); the query is the original pack's. Re-run sql/setup.sql to go back
-- to the synthetic market.
-- ============================================================================
USE ROLE ACCOUNTADMIN;
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE_PUBLIC_DATA_FINANCIAL_PACKAGE TO ROLE MARKET_SHARE_ROLE;
USE ROLE MARKET_SHARE_ROLE;
USE WAREHOUSE SNOWPACK_MARKET_SHARE_WH;
USE SCHEMA SNOWPACK_MARKET_SHARE.CORE;

DROP TABLE IF EXISTS MARKET_SHARE_RETAIL_SALES;
CREATE OR REPLACE VIEW MARKET_SHARE_RETAIL_SALES
  COMMENT = 'US Census Advance Retail Sales by category (SNOWFLAKE_PUBLIC_DATA_FINANCIAL_PACKAGE), latest vintage per month.'
AS
WITH ts AS (
  SELECT variable, date, value,
         ROW_NUMBER() OVER (PARTITION BY variable, date ORDER BY _EFFECTIVE_START_TIMESTAMP DESC) AS rn
  FROM SNOWFLAKE_PUBLIC_DATA_FINANCIAL_PACKAGE.COMMERCIAL_BANKING.FINANCIAL_ECONOMIC_INDICATORS_TIMESERIES_PIT
  WHERE variable IN (SELECT census_variable FROM MARKET_SHARE_MERCHANT_CATEGORY)
)
SELECT c.category_code, c.category_name, LAST_DAY(ts.date) AS month_end, ts.value AS market_sales_usd
FROM ts JOIN MARKET_SHARE_MERCHANT_CATEGORY c ON c.census_variable = ts.variable
WHERE ts.rn = 1;

CREATE OR REPLACE VIEW MARKET_SHARE_DATA_SOURCE_INFO AS
SELECT 'marketplace' AS mode,
       'Synthetic processor book benchmarked against US Census Advance Retail Sales (free Financial Data Package listing).' AS note;

SELECT category_name, share_start_bps, share_now_bps, status FROM MARKET_SHARE_VERTICAL_SUMMARY;
