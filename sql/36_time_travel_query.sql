
-- ============================================
-- STEP 36: QUERY HISTORICAL DATA USING TIME TRAVEL
-- ============================================

SELECT *
FROM MY_FIRST_DB.SILVER.TIME_TRAVEL_DEMO
AT (
    TIMESTAMP =>
    TO_TIMESTAMP_TZ('2026-11-23 09:40:32.891000-08:00')
)
ORDER BY CUSTOMER_ID;
