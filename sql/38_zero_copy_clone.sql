
-- ============================================
-- STEP 38: ZERO-COPY CLONING DEMO
-- ============================================

-- Create a zero-copy clone
CREATE TABLE
    MY_FIRST_DB.SILVER.TIME_TRAVEL_DEMO_CLONE
CLONE
    MY_FIRST_DB.SILVER.TIME_TRAVEL_DEMO;

-- Verify original table
SELECT *
FROM MY_FIRST_DB.SILVER.TIME_TRAVEL_DEMO
ORDER BY CUSTOMER_ID;

-- Verify cloned table
SELECT *
FROM MY_FIRST_DB.SILVER.TIME_TRAVEL_DEMO_CLONE
ORDER BY CUSTOMER_ID;
