
import os
import sys
from pathlib import Path

import pandas as pd
import snowflake.connector
from dotenv import load_dotenv


# --------------------------------------------------
# PROJECT PATHS AND CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
DATA_DIR = BASE_DIR / "reports" / "data"

load_dotenv(ENV_FILE)

REQUIRED_ENV_VARS = [
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_HOST",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_PASSWORD",
    "SNOWFLAKE_WAREHOUSE",
    "SNOWFLAKE_DATABASE",
    "SNOWFLAKE_SCHEMA",
    "SNOWFLAKE_ROLE",
]


# --------------------------------------------------
# SQL QUERIES
# Existing Gold extraction logic preserved
# --------------------------------------------------

EXTRACTION_QUERIES = [
    (
        "daily_sales.csv",
        """
        SELECT *
        FROM MY_FIRST_DB.GOLD.DAILY_SALES
        ORDER BY SALES_DATE
        """,
    ),
    (
        "top_20_products.csv",
        """
        SELECT *
        FROM MY_FIRST_DB.GOLD.PRODUCT_PERFORMANCE
        ORDER BY TOTAL_REVENUE DESC
        LIMIT 20
        """,
    ),
    (
        "sequential_funnel.csv",
        """
        SELECT *
        FROM MY_FIRST_DB.GOLD.CONVERSION_FUNNEL_SEQUENTIAL
        """,
    ),
    (
        "standard_funnel.csv",
        """
        SELECT *
        FROM MY_FIRST_DB.GOLD.CONVERSION_FUNNEL
        """,
    ),
]


# --------------------------------------------------
# ENVIRONMENT VALIDATION
# --------------------------------------------------

def validate_environment():
    if not ENV_FILE.exists():
        raise FileNotFoundError(
            "Project .env file was not found."
        )

    missing_vars = [
        name
        for name in REQUIRED_ENV_VARS
        if not os.getenv(name) or not os.getenv(name).strip()
    ]

    if missing_vars:
        raise ValueError(
            "Missing required environment variables: "
            + ", ".join(missing_vars)
        )


# --------------------------------------------------
# DATA EXTRACTION
# --------------------------------------------------

def extract_query(cursor, query):
    cursor.execute(query)

    rows = cursor.fetchall()

    if cursor.description is None:
        raise RuntimeError(
            "Query did not return column metadata."
        )

    columns = [
        description[0]
        for description in cursor.description
    ]

    return pd.DataFrame(rows, columns=columns)


# --------------------------------------------------
# MAIN EXTRACTION WORKFLOW
# --------------------------------------------------

def main():
    connection = None
    cursor = None
    temporary_files = []

    try:
        print("\n========== GOLD DATA EXTRACTION ==========\n")

        validate_environment()

        print("Environment configuration validated.")

        connection = snowflake.connector.connect(
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            host=os.getenv("SNOWFLAKE_HOST"),
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA"),
            role=os.getenv("SNOWFLAKE_ROLE"),
            login_timeout=30,
            network_timeout=30,
            enable_server_session_keep_alive_auto_detection=True,
        )

        print("Snowflake connection successful.")

        DATA_DIR.mkdir(parents=True, exist_ok=True)

        cursor = connection.cursor()

        extracted_data = []

        # Extract all datasets before updating existing CSVs.
        for filename, query in EXTRACTION_QUERIES:
            print(f"\nExtracting: {filename}")

            dataframe = extract_query(cursor, query)

            extracted_data.append((filename, dataframe))

            print(
                f"Fetched {len(dataframe):,} rows "
                f"and {len(dataframe.columns):,} columns."
            )

        # Stage all CSV files before replacing existing reports.
        for filename, dataframe in extracted_data:
            output_path = DATA_DIR / filename
            temporary_path = DATA_DIR / f".{filename}.tmp"

            dataframe.to_csv(temporary_path, index=False)

            temporary_files.append(temporary_path)

        # Replace existing files only after all extractions
        # and temporary CSV writes have succeeded.
        for filename, dataframe in extracted_data:
            temporary_path = DATA_DIR / f".{filename}.tmp"
            output_path = DATA_DIR / filename

            os.replace(temporary_path, output_path)

            print(
                f"Exported {filename}: "
                f"{len(dataframe):,} rows"
            )

        temporary_files.clear()

        print("\nAll selected Gold extracts completed successfully.")
        return 0

    except Exception as error:
        print("\nDATA EXTRACTION FAILED")
        print(f"Error type: {type(error).__name__}")
        print(f"Error details: {error}")

        return 1

    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                print("Warning: Could not close Snowflake cursor.")

        if connection is not None:
            try:
                connection.close()
                print("\nSnowflake connection closed.")
            except Exception:
                print("Warning: Could not close Snowflake connection.")

        # Remove temporary files left behind after a failure.
        for temporary_path in temporary_files:
            try:
                if temporary_path.exists():
                    temporary_path.unlink()
            except OSError:
                print(
                    "Warning: Could not remove temporary file: "
                    f"{temporary_path.name}"
                )


if __name__ == "__main__":
    sys.exit(main())
