
-- ============================================
-- STEP 33: CLEANUP INCREMENTAL TEST DATA
-- ============================================

-- Temporarily stop automated task
ALTER TASK MY_FIRST_DB.SILVER.PRODUCT_INCREMENTAL_TASK SUSPEND;

-- Delete test record from target table
DELETE FROM MY_FIRST_DB.SILVER.DIM_PRODUCTS_INCREMENTAL_DEMO
WHERE PRODUCT_ID = 999999999998;

-- Delete test records from source table
DELETE FROM MY_FIRST_DB.SILVER.DIM_PRODUCTS_MERGE_DEMO
WHERE PRODUCT_ID = 999999999998;

-- Resume automated task
ALTER TASK MY_FIRST_DB.SILVER.PRODUCT_INCREMENTAL_TASK RESUME;
