
-- ============================================
-- E-COMMERCE DATA WAREHOUSE
-- STEP 09: NON-POSITIVE PRICE ANALYSIS
-- ============================================

-- 1. Analyze zero and negative prices by event type
SELECT
    EVENT_TYPE,
    COUNT_IF(TRY_TO_DECIMAL(TRIM(PRICE), 18, 2) = 0)
        AS ZERO_PRICE_RECORDS,
    COUNT_IF(TRY_TO_DECIMAL(TRIM(PRICE), 18, 2) < 0)
        AS NEGATIVE_PRICE_RECORDS,
    COUNT_IF(TRY_TO_DECIMAL(TRIM(PRICE), 18, 2) <= 0)
        AS TOTAL_NON_POSITIVE_RECORDS
FROM MY_FIRST_DB.BRONZE.RAW_EVENTS
GROUP BY EVENT_TYPE
ORDER BY EVENT_TYPE;

-- 2. Inspect sample records with zero or negative prices
SELECT
    EVENT_TIME,
    EVENT_TYPE,
    PRODUCT_ID,
    CATEGORY_CODE,
    BRAND,
    PRICE,
    USER_ID,
    USER_SESSION
FROM MY_FIRST_DB.BRONZE.RAW_EVENTS
WHERE TRY_TO_DECIMAL(TRIM(PRICE), 18, 2) <= 0
LIMIT 20;
