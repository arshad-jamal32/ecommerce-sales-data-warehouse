
-- ============================================
-- E-COMMERCE DATA WAREHOUSE
-- STEP 04: CREATE BRONZE RAW EVENTS TABLE-- ============================================

CREATE TABLE IF NOT EXISTS
    MY_FIRST_DB.BRONZE.RAW_EVENTS
(
    EVENT_TIME     VARCHAR,
    EVENT_TYPE     VARCHAR,
    PRODUCT_ID     VARCHAR,
    CATEGORY_ID    VARCHAR,
    CATEGORY_CODE  VARCHAR,
    BRAND          VARCHAR,
    PRICE          VARCHAR,
    USER_ID        VARCHAR,
    USER_SESSION   VARCHAR
);
