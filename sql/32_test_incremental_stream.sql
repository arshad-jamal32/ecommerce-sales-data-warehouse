-- ============================================
-- STEP 32: TEST INCREMENTAL STREAM
-- ============================================

INSERT INTO MY_FIRST_DB.SILVER.DIM_PRODUCTS_MERGE_DEMO
(
    PRODUCT_ID,
    CATEGORY_ID,
    CATEGORY_CODE,
    BRAND,
    BRAND_VARIANT_COUNT,
    BRAND_CONFLICT_FLAG
)
VALUES
(
    999999999998,
    999999,
    'demo.test.product',
    'incremental_test_brand',
    1,
    FALSE
);