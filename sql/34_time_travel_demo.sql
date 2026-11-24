
-- ============================================
-- STEP 34: SNOWFLAKE TIME TRAVEL DEMO
-- ============================================

-- Create an isolated demo table
CREATE OR REPLACE TABLE
    MY_FIRST_DB.SILVER.TIME_TRAVEL_DEMO
    DATA_RETENTION_TIME_IN_DAYS = 1
AS
SELECT
    1 AS CUSTOMER_ID,
    'Rahul' AS CUSTOMER_NAME,
    5000 AS BALANCE
UNION ALL
SELECT
    2,
    'Priya',
    8000;

-- Verify initial records
SELECT *
FROM MY_FIRST_DB.SILVER.TIME_TRAVEL_DEMO
ORDER BY CUSTOMER_ID;

-- Capture the current timestamp
SELECT CURRENT_TIMESTAMP() AS BEFORE_CHANGE_TIME;
