
import os
import sys
from pathlib import Path

import snowflake.connector
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

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

EXPECTED_TABLES = {
    "DAILY_SALES",
    "PRODUCT_PERFORMANCE",
    "CUSTOMER_BEHAVIOR",
    "CONVERSION_FUNNEL",
    "CONVERSION_FUNNEL_SEQUENTIAL",
}


def main():
    connection = None
    cursor = None

    try:
        # Validate environment configuration
        if not ENV_FILE.exists():
            raise FileNotFoundError(".env file not found in project root.")

        load_dotenv(ENV_FILE)

        missing_vars = [
            name for name in REQUIRED_ENV_VARS
            if not os.getenv(name)
        ]

        if missing_vars:
            raise ValueError(
                "Missing required environment variables: "
                + ", ".join(missing_vars)
            )

        print("Environment configuration validated.")

        # Connect to Snowflake
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
        )

        print("Snowflake connection successful.")

        query = """
            SELECT
                TABLE_NAME,
                COLUMN_NAME,
                DATA_TYPE,
                ORDINAL_POSITION
            FROM MY_FIRST_DB.INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'GOLD'
              AND TABLE_NAME IN (
                  'DAILY_SALES',
                  'PRODUCT_PERFORMANCE',
                  'CUSTOMER_BEHAVIOR',
                  'CONVERSION_FUNNEL',
                  'CONVERSION_FUNNEL_SEQUENTIAL'
              )
            ORDER BY TABLE_NAME, ORDINAL_POSITION
        """

        cursor = connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()

        if not results:
            raise RuntimeError(
                "No columns found for the expected Gold tables."
            )

        print("\n========== GOLD DATA DICTIONARY ==========")

        current_table = None
        inspected_tables = set()

        for table, column, data_type, position in results:
            if table != current_table:
                current_table = table
                inspected_tables.add(table)
                print(f"\n[{table}]")

            print(f"  {position:>2}. {column:<40} {data_type}")

        missing_tables = EXPECTED_TABLES - inspected_tables

        if missing_tables:
            print("\nMissing expected Gold tables:")
            for table in sorted(missing_tables):
                print(f"  - {table}")

            raise RuntimeError("Gold schema inspection is incomplete.")

        print(f"\nTotal tables inspected: {len(inspected_tables)}")
        print(f"Total columns inspected: {len(results)}")
        print("All expected Gold tables were inspected successfully.")

        return 0

    except Exception as error:
        print(f"\nSchema inspection failed: {error}")
        return 1

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()
            print("\nConnection closed.")


if __name__ == "__main__":
    sys.exit(main())
