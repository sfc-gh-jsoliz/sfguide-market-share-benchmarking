-- ============================================================================
-- Market Share & Vertical Benchmarking - sql/cleanup.sql
-- Removes everything sql/setup.sql created: the database (tables, views,
-- semantic view, agent, stage, Streamlit app), the warehouse and the role.
-- Objects are owned by MARKET_SHARE_ROLE, so they are dropped as that role;
-- ACCOUNTADMIN then drops the role. Safe to run on an already-clean account.
-- Does not touch the Marketplace listing used by setup_census.sql.
-- ============================================================================
USE ROLE ACCOUNTADMIN;
EXECUTE IMMEDIATE $$
BEGIN
  USE ROLE MARKET_SHARE_ROLE;
  DROP DATABASE IF EXISTS SNOWPACK_MARKET_SHARE;
  DROP WAREHOUSE IF EXISTS SNOWPACK_MARKET_SHARE_WH;
EXCEPTION WHEN OTHER THEN NULL;
END;
$$;
USE ROLE ACCOUNTADMIN;
DROP DATABASE IF EXISTS SNOWPACK_MARKET_SHARE;
DROP WAREHOUSE IF EXISTS SNOWPACK_MARKET_SHARE_WH;
DROP ROLE IF EXISTS MARKET_SHARE_ROLE;
SHOW DATABASES LIKE 'SNOWPACK_MARKET_SHARE';
SHOW WAREHOUSES LIKE 'SNOWPACK_MARKET_SHARE_WH';
SHOW ROLES LIKE 'MARKET_SHARE_ROLE';
