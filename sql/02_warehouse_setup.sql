
-- =====================================================
-- PROJECT: E-COMMERCE SALES DATA WAREHOUSE
-- STEP 02: WAREHOUSE SETUP
-- PURPOSE: Create compute warehouse
-- =====================================================

CREATE WAREHOUSE IF NOT EXISTS COMPUTE_WH
    WAREHOUSE_TYPE = STANDARD
    WAREHOUSE_SIZE = XSMALL
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE;
