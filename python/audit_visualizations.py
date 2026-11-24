from pathlib import Path
import sys

from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
CHART_DIR = BASE_DIR / "reports" / "charts"
INTERACTIVE_DIR = BASE_DIR / "reports" / "interactive"

EXPECTED_CHARTS = [
    "daily_sales_trend.png",
    "daily_purchase_events.png",
    "top_10_products.png",
    "product_engagement.png",
    "sequential_conversion_funnel.png",
    "funnel_comparison.png",
]

DASHBOARD_FILE = INTERACTIVE_DIR / "ecommerce_analytics.html"

MIN_WIDTH = 1000
MIN_HEIGHT = 500
MIN_FILE_SIZE = 20 * 1024

errors = []


def check_chart(filename):
    path = CHART_DIR / filename

    if not path.is_file():
        errors.append(f"MISSING: {filename}")
        print(f"[FAIL] {filename} - file not found")
        return

    size = path.stat().st_size

    if size < MIN_FILE_SIZE:
        errors.append(f"File size too small: {filename}")
        print(f"[FAIL] {filename} - file size below 20 KB")
        return

    try:
        with Image.open(path) as img:
            width, height = img.size
            img.verify()

        if width < MIN_WIDTH or height < MIN_HEIGHT:
            errors.append(f"Insufficient dimensions: {filename}")
            print(
                f"[FAIL] {filename} - dimensions "
                f"{width}x{height}"
            )
            return

        print(
            f"[PASS] {filename} - "
            f"{width}x{height}, {size / 1024:.1f} KB"
        )

    except Exception as error:
        errors.append(f"Unreadable image: {filename}")
        print(f"[FAIL] {filename} - {error}")


def check_dashboard():
    if not DASHBOARD_FILE.is_file():
        errors.append("Interactive dashboard is missing")
        print("[FAIL] Interactive dashboard - file not found")
        return

    size = DASHBOARD_FILE.stat().st_size

    if size < MIN_FILE_SIZE:
        errors.append("Interactive dashboard file size too small")
        print("[FAIL] Interactive dashboard - file size below 20 KB")
        return

    try:
        html = DASHBOARD_FILE.read_text(
            encoding="utf-8",
            errors="replace"
        ).lower()

        required_markers = {
            "HTML document": "<html",
            "Plotly content": "plotly",
            "Daily sales content": "daily",
            "Revenue proxy content": "revenue proxy",
            "Funnel content": "funnel",
        }

        missing = []

        for label, marker in required_markers.items():
            if marker not in html:
                missing.append(label)

        if missing:
            errors.append(
                "Dashboard missing markers: " + ", ".join(missing)
            )
            print(
                "[FAIL] Interactive dashboard - missing: "
                + ", ".join(missing)
            )
            return

        if "</html>" not in html:
            errors.append("Dashboard HTML closing tag missing")
            print("[FAIL] Interactive dashboard - incomplete HTML document")
            return

        print(
            f"[PASS] Interactive dashboard - "
            f"{size / (1024 * 1024):.2f} MB"
        )

    except Exception as error:
        errors.append(f"Dashboard could not be read: {error}")
        print(f"[FAIL] Interactive dashboard - {error}")


def main():
    print("\n========== VISUALIZATION AUDIT ==========\n")

    print("Checking static charts...")

    for filename in EXPECTED_CHARTS:
        check_chart(filename)

    print("\nChecking interactive dashboard...")
    check_dashboard()

    print("\n========== AUDIT SUMMARY ==========")

    if errors:
        print(f"Audit completed with {len(errors)} issue(s).")

        for error in errors:
            print(f"- {error}")

        return 1

    print("All 6 static charts passed structural checks.")
    print("Interactive dashboard passed structural checks.")
    print("All visualization audit checks passed.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
