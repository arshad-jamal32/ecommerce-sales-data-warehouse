
-- =====================================================
-- PROJECT: E-COMMERCE SALES DATA WAREHOUSE
-- STEP 01: DATABASE AND SCHEMA SETUP
-- PURPOSE: Create database and required schemas
-- =====================================================

-- Create project database
CREATE DATABASE IF NOT EXISTS MY_FIRST_DB
    DATA_RETENTION_TIME_IN_DAYS = 1;

-- Create schemas
CREATE SCHEMA IF NOT EXISTS MY_FIRST_DB.MY_SCHEMA;

CREATE SCHEMA IF NOT EXISTS MY_FIRST_DB.BRONZE;

CREATE SCHEMA IF NOT EXISTS MY_FIRST_DB.SILVER;

CREATE SCHEMA IF NOT EXISTS MY_FIRST_DB.GOLD;
