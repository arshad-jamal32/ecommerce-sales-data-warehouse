
from pathlib import Path
import sys

import numpy as np
import pandas as pd


# --------------------------------------------------
# PROJECT CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "reports" / "data"

EXPECTED_REVENUE = 229_957_502.27
EXPECTED_PURCHASE_EVENTS = 742_849

RATE_TOLERANCE = 0.011

errors = []
warnings = []


# --------------------------------------------------
# COMMON VALIDATION HELPERS
# --------------------------------------------------

def check(condition, message):
    if bool(condition):
        print(f"PASS  {message}")
    else:
        print(f"FAIL  {message}")
        errors.append(message)


def load_csv(filename, expected_rows):
    path = DATA_DIR / filename

    if not path.exists():
        check(False, f"{filename}: file exists")
        return None

    try:
        df = pd.read_csv(path)
    except Exception as error:
        check(False, f"{filename}: CSV could be read ({error})")
        return None

    check(
        len(df) == expected_rows,
        f"{filename}: expected {expected_rows} rows, found {len(df)}"
    )

    check(not df.empty, f"{filename}: file is not empty")

    return df


def validate_schema(df, expected_columns, label):
    actual_columns = set(df.columns)

    check(
        actual_columns == expected_columns,
        f"{label}: column structure matches expected schema"
    )

    return actual_columns == expected_columns


def validate_numeric_columns(df, columns, label, integer_columns=None):
    integer_columns = set(integer_columns or [])
    valid_columns = {}

    for col in columns:
        if col not in df.columns:
            valid_columns[col] = False
            continue

        df[col] = pd.to_numeric(df[col], errors="coerce")

        numeric = df[col].notna().all()
        finite = np.isfinite(df[col].to_numpy(dtype=float)).all()

        valid = numeric and finite

        check(
            valid,
            f"{label}: {col} contains valid finite numeric values"
        )

        if not valid:
            valid_columns[col] = False
            continue

        non_negative = (df[col] >= 0).all()

        check(
            non_negative,
            f"{label}: {col} has no negative values"
        )

        if col in integer_columns:
            is_integer = np.equal(
                df[col].to_numpy(dtype=float) % 1,
                0
            ).all()

            check(
                is_integer,
                f"{label}: {col} contains whole-number counts"
            )

            valid_columns[col] = non_negative and is_integer
        else:
            valid_columns[col] = non_negative

    return valid_columns


def validate_rates(df, formulas, label):
    """
    Independently recalculate funnel rates from their counts.

    A tolerance of 0.011 percentage points allows
    rates rounded to two decimal places.
    """

    for rate_column, numerator, denominator in formulas:
        if not all(
            col in df.columns
            for col in [rate_column, numerator, denominator]
        ):
            continue

        if df[
            [rate_column, numerator, denominator]
        ].isna().any().any():
            check(
                False,
                f"{label}: {rate_column} can be recalculated"
            )
            continue

        expected_values = []

        for _, row in df.iterrows():
            denominator_value = row[denominator]

            if denominator_value == 0:
                expected_values.append(np.nan)
            else:
                expected_values.append(
                    row[numerator] / denominator_value * 100
                )

        expected = pd.Series(expected_values, index=df.index)

        if expected.isna().any():
            check(
                False,
                f"{label}: {rate_column} has a non-zero denominator"
            )
            continue

        difference = (df[rate_column] - expected).abs()

        check(
            (difference <= RATE_TOLERANCE).all(),
            f"{label}: {rate_column} matches its count-based calculation"
        )


# --------------------------------------------------
# MAIN VALIDATION
# --------------------------------------------------

def main():
    print("\n========== LOCAL GOLD DATA VALIDATION ==========\n")

    if not DATA_DIR.exists():
        check(False, "Reports data directory exists")
        return 1

    # --------------------------------------------------
    # 1. DAILY SALES
    # --------------------------------------------------

    daily = load_csv("daily_sales.csv", 31)

    if daily is not None:
        expected_columns = {
            "SALES_DATE",
            "TOTAL_PURCHASE_EVENTS",
            "TOTAL_REVENUE",
            "UNIQUE_BUYERS",
            "PURCHASE_SESSIONS",
            "AVG_PURCHASE_VALUE",
        }

        if validate_schema(daily, expected_columns, "DAILY_SALES"):

            daily["SALES_DATE"] = pd.to_datetime(
                daily["SALES_DATE"],
                errors="coerce"
            )

            check(
                daily["SALES_DATE"].notna().all(),
                "DAILY_SALES: all dates are valid"
            )

            if daily["SALES_DATE"].notna().all():
                actual_dates = set(
                    daily["SALES_DATE"].dt.normalize()
                )

                expected_dates = set(
                    pd.date_range(
                        "2019-10-01",
                        "2019-10-31",
                        freq="D"
                    )
                )

                check(
                    actual_dates == expected_dates,
                    "DAILY_SALES: complete October 2019 date coverage"
                )

                check(
                    daily["SALES_DATE"].is_unique,
                    "DAILY_SALES: dates are unique"
                )

            numeric_columns = [
                "TOTAL_PURCHASE_EVENTS",
                "TOTAL_REVENUE",
                "UNIQUE_BUYERS",
                "PURCHASE_SESSIONS",
                "AVG_PURCHASE_VALUE",
            ]

            valid = validate_numeric_columns(
                daily,
                numeric_columns,
                "DAILY_SALES",
                integer_columns={
                    "TOTAL_PURCHASE_EVENTS",
                    "UNIQUE_BUYERS",
                    "PURCHASE_SESSIONS",
                }
            )

            if valid.get("TOTAL_PURCHASE_EVENTS"):
                check(
                    int(daily["TOTAL_PURCHASE_EVENTS"].sum())
                    == EXPECTED_PURCHASE_EVENTS,
                    "DAILY_SALES: purchase-event total matches SQL result"
                )

            if valid.get("TOTAL_REVENUE"):
                check(
                    abs(
                        daily["TOTAL_REVENUE"].sum()
                        - EXPECTED_REVENUE
                    ) < 0.05,
                    "DAILY_SALES: revenue proxy total matches SQL result"
                )

    # --------------------------------------------------
    # 2. TOP 20 PRODUCTS
    # --------------------------------------------------

    products = load_csv("top_20_products.csv", 20)

    if products is not None:
        expected_columns = {
            "PRODUCT_ID",
            "CATEGORY_ID",
            "CATEGORY_CODE",
            "BRAND",
            "BRAND_CONFLICT_FLAG",
            "TOTAL_VIEWS",
            "TOTAL_CART_EVENTS",
            "TOTAL_PURCHASE_EVENTS",
            "TOTAL_REVENUE",
            "UNIQUE_USERS",
        }

        if validate_schema(
            products,
            expected_columns,
            "TOP_20_PRODUCTS"
        ):

            check(
                products["PRODUCT_ID"].notna().all(),
                "TOP_20_PRODUCTS: no missing product IDs"
            )

            check(
                products["PRODUCT_ID"].nunique() == 20,
                "TOP_20_PRODUCTS: all 20 product IDs are unique"
            )

            product_metrics = [
                "TOTAL_VIEWS",
                "TOTAL_CART_EVENTS",
                "TOTAL_PURCHASE_EVENTS",
                "TOTAL_REVENUE",
                "UNIQUE_USERS",
            ]

            valid = validate_numeric_columns(
                products,
                product_metrics,
                "TOP_20_PRODUCTS",
                integer_columns={
                    "TOTAL_VIEWS",
                    "TOTAL_CART_EVENTS",
                    "TOTAL_PURCHASE_EVENTS",
                    "UNIQUE_USERS",
                }
            )

            if valid.get("TOTAL_REVENUE"):
                check(
                    products["TOTAL_REVENUE"].is_monotonic_decreasing,
                    "TOP_20_PRODUCTS: sorted by revenue descending"
                )

            flags = products["BRAND_CONFLICT_FLAG"].astype("string").str.upper()

            check(
                flags.notna().all()
                and flags.isin({"TRUE", "FALSE"}).all(),
                "TOP_20_PRODUCTS: all brand conflict flags are valid"
            )

    # --------------------------------------------------
    # 3. SEQUENTIAL CONVERSION FUNNEL
    # --------------------------------------------------

    sequential = load_csv("sequential_funnel.csv", 1)

    if sequential is not None:
        expected_columns = {
            "TOTAL_SESSIONS_ANALYZED",
            "SESSIONS_WITH_VIEW",
            "SESSIONS_WITH_VIEW_THEN_CART",
            "SESSIONS_COMPLETING_SEQUENTIAL_FUNNEL",
            "VIEW_TO_CART_RATE",
            "CART_TO_PURCHASE_RATE",
            "VIEW_TO_PURCHASE_RATE",
        }

        if validate_schema(
            sequential,
            expected_columns,
            "SEQUENTIAL_FUNNEL"
        ):

            count_columns = [
                "TOTAL_SESSIONS_ANALYZED",
                "SESSIONS_WITH_VIEW",
                "SESSIONS_WITH_VIEW_THEN_CART",
                "SESSIONS_COMPLETING_SEQUENTIAL_FUNNEL",
            ]

            rate_columns = [
                "VIEW_TO_CART_RATE",
                "CART_TO_PURCHASE_RATE",
                "VIEW_TO_PURCHASE_RATE",
            ]

            valid = validate_numeric_columns(
                sequential,
                count_columns + rate_columns,
                "SEQUENTIAL_FUNNEL",
                integer_columns=count_columns
            )

            if all(valid.get(col) for col in count_columns):
                values = sequential.iloc[0]

                check(
                    values["TOTAL_SESSIONS_ANALYZED"]
                    >= values["SESSIONS_WITH_VIEW"]
                    >= values["SESSIONS_WITH_VIEW_THEN_CART"]
                    >= values["SESSIONS_COMPLETING_SEQUENTIAL_FUNNEL"],
                    "SEQUENTIAL_FUNNEL: stage counts are logically ordered"
                )

            if all(valid.get(col) for col in rate_columns):
                for col in rate_columns:
                    check(
                        sequential[col].between(0, 100).all(),
                        f"SEQUENTIAL_FUNNEL: {col} is between 0 and 100"
                    )

                validate_rates(
                    sequential,
                    [
                        (
                            "VIEW_TO_CART_RATE",
                            "SESSIONS_WITH_VIEW_THEN_CART",
                            "SESSIONS_WITH_VIEW",
                        ),
                        (
                            "CART_TO_PURCHASE_RATE",
                            "SESSIONS_COMPLETING_SEQUENTIAL_FUNNEL",
                            "SESSIONS_WITH_VIEW_THEN_CART",
                        ),
                        (
                            "VIEW_TO_PURCHASE_RATE",
                            "SESSIONS_COMPLETING_SEQUENTIAL_FUNNEL",
                            "SESSIONS_WITH_VIEW",
                        ),
                    ],
                    "SEQUENTIAL_FUNNEL"
                )

    # --------------------------------------------------
    # 4. STANDARD CO-OCCURRENCE FUNNEL
    # --------------------------------------------------

    standard = load_csv("standard_funnel.csv", 1)

    if standard is not None:
        expected_columns = {
            "TOTAL_SESSIONS_ANALYZED",
            "SESSIONS_WITH_VIEW",
            "SESSIONS_WITH_CART",
            "SESSIONS_WITH_PURCHASE",
            "SESSIONS_WITH_VIEW_AND_CART",
            "SESSIONS_COMPLETING_FUNNEL",
            "VIEW_TO_CART_RATE",
            "CART_TO_PURCHASE_RATE",
            "VIEW_TO_PURCHASE_RATE",
        }

        if validate_schema(
            standard,
            expected_columns,
            "STANDARD_FUNNEL"
        ):

            count_columns = [
                "TOTAL_SESSIONS_ANALYZED",
                "SESSIONS_WITH_VIEW",
                "SESSIONS_WITH_CART",
                "SESSIONS_WITH_PURCHASE",
                "SESSIONS_WITH_VIEW_AND_CART",
                "SESSIONS_COMPLETING_FUNNEL",
            ]

            rate_columns = [
                "VIEW_TO_CART_RATE",
                "CART_TO_PURCHASE_RATE",
                "VIEW_TO_PURCHASE_RATE",
            ]

            valid = validate_numeric_columns(
                standard,
                count_columns + rate_columns,
                "STANDARD_FUNNEL",
                integer_columns=count_columns
            )

            if all(valid.get(col) for col in count_columns):
                values = standard.iloc[0]

                check(
                    values["TOTAL_SESSIONS_ANALYZED"]
                    >= values["SESSIONS_WITH_VIEW"],
                    "STANDARD_FUNNEL: total sessions >= view sessions"
                )

                check(
                    values["SESSIONS_WITH_VIEW_AND_CART"]
                    <= values["SESSIONS_WITH_VIEW"]
                    and values["SESSIONS_WITH_VIEW_AND_CART"]
                    <= values["SESSIONS_WITH_CART"],
                    "STANDARD_FUNNEL: view-and-cart count is logically valid"
                )

                check(
                    values["SESSIONS_COMPLETING_FUNNEL"]
                    <= values["SESSIONS_WITH_VIEW_AND_CART"]
                    and values["SESSIONS_COMPLETING_FUNNEL"]
                    <= values["SESSIONS_WITH_PURCHASE"],
                    "STANDARD_FUNNEL: completed funnel count is logically valid"
                )

            if all(valid.get(col) for col in rate_columns):
                for col in rate_columns:
                    check(
                        standard[col].between(0, 100).all(),
                        f"STANDARD_FUNNEL: {col} is between 0 and 100"
                    )

                validate_rates(
                    standard,
                    [
                        (
                            "VIEW_TO_CART_RATE",
                            "SESSIONS_WITH_VIEW_AND_CART",
                            "SESSIONS_WITH_VIEW",
                        ),
                        (
                            "CART_TO_PURCHASE_RATE",
                            "SESSIONS_COMPLETING_FUNNEL",
                            "SESSIONS_WITH_VIEW_AND_CART",
                        ),
                        (
                            "VIEW_TO_PURCHASE_RATE",
                            "SESSIONS_COMPLETING_FUNNEL",
                            "SESSIONS_WITH_VIEW",
                        ),
                    ],
                    "STANDARD_FUNNEL"
                )

    # --------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------

    print("\n========== VALIDATION SUMMARY ==========\n")

    if errors:
        print(f"VALIDATION FAILED: {len(errors)} issue(s) found.")

        for error in errors:
            print(f"- {error}")

        if warnings:
            print("\nWarnings:")
            for warning in warnings:
                print(f"- {warning}")

        return 1

    print("ALL VALIDATION CHECKS PASSED.")
    print("All four Gold extracts are ready for visualization.")

    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"- {warning}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
