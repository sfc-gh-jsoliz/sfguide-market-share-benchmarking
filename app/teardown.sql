-- ============================================================================
-- Market Share & Vertical Benchmarking — teardown.sql
-- ----------------------------------------------------------------------------
-- Removes everything this pack created: the dedicated database (all tables,
-- views, semantic view, reports table, and agent) and the dedicated warehouse.
-- Safe to run repeatedly. Does NOT touch the Marketplace "Financial Data
-- Package" listing (unmount that from Snowsight if you no longer need it).
-- ============================================================================

DROP DATABASE IF EXISTS SNOWPACK_MARKET_SHARE;
DROP WAREHOUSE IF EXISTS SNOWPACK_MARKET_SHARE_WH;
