
-- ============================================
-- STEP 35: MODIFY TIME TRAVEL DEMO TABLE
-- ============================================

-- Update Rahul's balance
UPDATE MY_FIRST_DB.SILVER.TIME_TRAVEL_DEMO
SET BALANCE = 1000
WHERE CUSTOMER_ID = 1;

-- Delete Priya's record
DELETE FROM MY_FIRST_DB.SILVER.TIME_TRAVEL_DEMO
WHERE CUSTOMER_ID = 2;

-- Check current table state
SELECT *
FROM MY_FIRST_DB.SILVER.TIME_TRAVEL_DEMO
ORDER BY CUSTOMER_ID;
