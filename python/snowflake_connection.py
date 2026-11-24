
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
        # Validate environment configuration
        if not ENV_FILE.is_file():
            raise FileNotFoundError(
                ".env file not found in project root."
            )

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

        # Establish Snowflake connection
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

        print("Snowflake connection successful!")

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                CURRENT_VERSION(),
                CURRENT_DATABASE(),
                CURRENT_SCHEMA(),
                CURRENT_WAREHOUSE(),
                CURRENT_ROLE()
        """)

        result = cursor.fetchone()

        if result is None:
            raise RuntimeError(
                "Snowflake connection details could not be retrieved."
            )

        print("\n========== CONNECTION DETAILS ==========")
        print(f"Snowflake Version : {result[0]}")
        print(f"Database          : {result[1]}")
        print(f"Schema            : {result[2]}")
        print(f"Warehouse         : {result[3]}")
        print(f"Role              : {result[4]}")

        return 0

    except Exception as error:
        print("\nSnowflake connection failed.")
        print(f"Error: {error}")
        return 1

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()
            print("\nConnection closed.")


if __name__ == "__main__":
    sys.exit(main())
