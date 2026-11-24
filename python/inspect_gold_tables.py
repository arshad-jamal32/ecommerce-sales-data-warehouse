
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


def main():
    connection = None
    cursor = None

    try:
        # Load environment configuration
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
                ROW_COUNT,
                BYTES
            FROM MY_FIRST_DB.INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = 'GOLD'
              AND TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """

        cursor = connection.cursor()

        cursor.execute(query)
        results = cursor.fetchall()

        print("\n========== GOLD TABLE INVENTORY ==========")

        if results:
            for table_name, row_count, bytes_used in results:
                rows_display = (
                    f"{row_count:,}" if row_count is not None else "N/A"
                )
                bytes_display = (
                    f"{bytes_used:,} bytes"
                    if bytes_used is not None else "N/A"
                )

                print(
                    f"{table_name:<40} "
                    f"Rows: {rows_display} "
                    f"Storage: {bytes_display}"
                )
        else:
            print("No Gold tables found.")

        print(f"\nTotal Gold tables: {len(results)}")
        return 0

    except Exception as error:
        print(f"\nInspection failed: {error}")
        return 1

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()
            print("\nConnection closed.")


if __name__ == "__main__":
    sys.exit(main())
