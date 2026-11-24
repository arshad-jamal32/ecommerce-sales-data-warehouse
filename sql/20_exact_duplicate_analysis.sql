
-- ============================================
-- E-COMMERCE DATA WAREHOUSE
-- STEP 20: EXACT DUPLICATE RECORD ANALYSIS
-- ============================================

WITH DUPLICATE_GROUPS AS
(
    SELECT
        COUNT(*) AS OCCURRENCES

    FROM MY_FIRST_DB.SILVER.CLEAN_EVENTS

    GROUP BY
        EVENT_TIME,
        EVENT_TYPE,
        PRODUCT_ID,
        CATEGORY_ID,
        CATEGORY_CODE,
        BRAND,
        PRICE,
        USER_ID,
        USER_SESSION

    HAVING COUNT(*) > 1
)

SELECT
    COUNT(*) AS DUPLICATE_GROUPS,

    COALESCE(
        SUM(OCCURRENCES),
        0
    ) AS TOTAL_ROWS_IN_DUPLICATE_GROUPS,

    COALESCE(
        SUM(OCCURRENCES - 1),
        0
    ) AS EXTRA_DUPLICATE_ROWS,

    COALESCE(
        MAX(OCCURRENCES),
        0
    ) AS MAX_OCCURRENCES

FROM DUPLICATE_GROUPS;
