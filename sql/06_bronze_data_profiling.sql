
-- ============================================
-- E-COMMERCE DATA WAREHOUSE
-- STEP 06: BRONZE DATA PROFILING
-- ============================================

-- 1. Analyze event types
SELECT
    EVENT_TYPE,
    COUNT(*) AS TOTAL_EVENTS,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (),
        2
    ) AS EVENT_PERCENTAGE
FROM MY_FIRST_DB.BRONZE.RAW_EVENTS
GROUP BY EVENT_TYPE
ORDER BY TOTAL_EVENTS DESC;
