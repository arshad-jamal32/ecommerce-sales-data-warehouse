
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# =========================================================
# PROJECT PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "reports" / "data"
CHART_DIR = BASE_DIR / "reports" / "charts"
INTERACTIVE_DIR = BASE_DIR / "reports" / "interactive"

CHART_DIR.mkdir(parents=True, exist_ok=True)
INTERACTIVE_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# LOAD EXTRACTED DATA
# =========================================================

daily = pd.read_csv(DATA_DIR / "daily_sales.csv")
products = pd.read_csv(DATA_DIR / "top_20_products.csv")
sequential = pd.read_csv(DATA_DIR / "sequential_funnel.csv")
standard = pd.read_csv(DATA_DIR / "standard_funnel.csv")


# =========================================================
# INPUT DATA VALIDATION
# =========================================================

required_files = [
    DATA_DIR / "daily_sales.csv",
    DATA_DIR / "top_20_products.csv",
    DATA_DIR / "sequential_funnel.csv",
    DATA_DIR / "standard_funnel.csv",
]

missing_files = [
    file.name for file in required_files if not file.is_file()
]

if missing_files:
    raise FileNotFoundError(
        "Required CSV files not found: " + ", ".join(missing_files)
    )


def validate_columns(dataframe, required_columns, filename):
    missing = set(required_columns) - set(dataframe.columns)

    if missing:
        raise ValueError(
            f"{filename}: Missing columns: {', '.join(sorted(missing))}"
        )

    if dataframe.empty:
        raise ValueError(f"{filename}: CSV file is empty.")


def validate_numeric_columns(dataframe, columns, filename):
    for column in columns:
        values = pd.to_numeric(dataframe[column], errors="coerce")

        if values.isna().any() or not np.isfinite(values).all():
            raise ValueError(
                f"{filename}: Invalid or non-finite values in {column}."
            )

        if (values < 0).any():
            raise ValueError(
                f"{filename}: Negative values found in {column}."
            )

        dataframe[column] = values


daily_columns = [
    "SALES_DATE",
    "TOTAL_PURCHASE_EVENTS",
    "TOTAL_REVENUE",
    "UNIQUE_BUYERS",
    "PURCHASE_SESSIONS",
    "AVG_PURCHASE_VALUE",
]

product_columns = [
    "PRODUCT_ID",
    "TOTAL_VIEWS",
    "TOTAL_CART_EVENTS",
    "TOTAL_PURCHASE_EVENTS",
    "TOTAL_REVENUE",
]

sequential_columns = [
    "SESSIONS_WITH_VIEW",
    "SESSIONS_WITH_VIEW_THEN_CART",
    "SESSIONS_COMPLETING_SEQUENTIAL_FUNNEL",
    "VIEW_TO_CART_RATE",
    "CART_TO_PURCHASE_RATE",
    "VIEW_TO_PURCHASE_RATE",
]

standard_columns = [
    "SESSIONS_WITH_VIEW",
    "SESSIONS_WITH_VIEW_AND_CART",
    "SESSIONS_COMPLETING_FUNNEL",
    "VIEW_TO_CART_RATE",
    "CART_TO_PURCHASE_RATE",
    "VIEW_TO_PURCHASE_RATE",
]

validate_columns(daily, daily_columns, "daily_sales.csv")
validate_columns(products, product_columns, "top_20_products.csv")
validate_columns(sequential, sequential_columns, "sequential_funnel.csv")
validate_columns(standard, standard_columns, "standard_funnel.csv")

if len(daily) != 31:
    raise ValueError("daily_sales.csv must contain exactly 31 daily records.")

if len(products) != 20:
    raise ValueError("top_20_products.csv must contain exactly 20 products.")

if len(sequential) != 1 or len(standard) != 1:
    raise ValueError("Each funnel CSV must contain exactly one summary row.")

daily["SALES_DATE"] = pd.to_datetime(
    daily["SALES_DATE"], errors="coerce"
)

if daily["SALES_DATE"].isna().any():
    raise ValueError("daily_sales.csv contains invalid dates.")

if daily["SALES_DATE"].duplicated().any():
    raise ValueError("daily_sales.csv contains duplicate dates.")

expected_dates = pd.date_range("2019-10-01", "2019-10-31")

if set(daily["SALES_DATE"]) != set(expected_dates):
    raise ValueError("daily_sales.csv does not cover October 2019 completely.")

if products["PRODUCT_ID"].isna().any():
    raise ValueError("top_20_products.csv contains missing product IDs.")

if products["PRODUCT_ID"].duplicated().any():
    raise ValueError("top_20_products.csv contains duplicate product IDs.")

daily_numeric = [
    "TOTAL_PURCHASE_EVENTS",
    "TOTAL_REVENUE",
    "UNIQUE_BUYERS",
    "PURCHASE_SESSIONS",
    "AVG_PURCHASE_VALUE",
]

product_numeric = [
    "TOTAL_VIEWS",
    "TOTAL_CART_EVENTS",
    "TOTAL_PURCHASE_EVENTS",
    "TOTAL_REVENUE",
]

funnel_counts = [
    "SESSIONS_WITH_VIEW",
    "SESSIONS_WITH_VIEW_THEN_CART",
    "SESSIONS_COMPLETING_SEQUENTIAL_FUNNEL",
]

standard_counts = [
    "SESSIONS_WITH_VIEW",
    "SESSIONS_WITH_VIEW_AND_CART",
    "SESSIONS_COMPLETING_FUNNEL",
]

funnel_rates = [
    "VIEW_TO_CART_RATE",
    "CART_TO_PURCHASE_RATE",
    "VIEW_TO_PURCHASE_RATE",
]

validate_numeric_columns(daily, daily_numeric, "daily_sales.csv")
validate_numeric_columns(products, product_numeric, "top_20_products.csv")
validate_numeric_columns(sequential, funnel_counts + funnel_rates, "sequential_funnel.csv")
validate_numeric_columns(standard, standard_counts + funnel_rates, "standard_funnel.csv")

for dataframe, count_columns, filename in [
    (daily, ["TOTAL_PURCHASE_EVENTS", "UNIQUE_BUYERS", "PURCHASE_SESSIONS"], "daily_sales.csv"),
    (products, product_numeric[:3], "top_20_products.csv"),
    (sequential, funnel_counts, "sequential_funnel.csv"),
    (standard, standard_counts, "standard_funnel.csv"),
]:
    for column in count_columns:
        if not np.isclose(
            dataframe[column],
            np.round(dataframe[column])
        ).all():
            raise ValueError(
                f"{filename}: Non-integer event/count values in {column}."
            )

for dataframe, filename in [
    (sequential, "sequential_funnel.csv"),
    (standard, "standard_funnel.csv"),
]:
    for column in funnel_rates:
        if (dataframe[column] > 100).any():
            raise ValueError(
                f"{filename}: Rate exceeds 100% in {column}."
            )

print("All four input CSV files passed validation.")


daily["SALES_DATE"] = pd.to_datetime(daily["SALES_DATE"])

products = products.sort_values(
    "TOTAL_REVENUE", ascending=False
).copy()

top10 = products.head(10).sort_values(
    "TOTAL_REVENUE", ascending=True
).copy()

seq = sequential.iloc[0]
std = standard.iloc[0]

print("\n========== E-COMMERCE VISUALIZATION ==========")


# =========================================================
# COMMON CHART SETTINGS
# =========================================================

plt.rcParams.update({
    "figure.figsize": (12, 7),
    "figure.dpi": 120,
    "savefig.dpi": 300,
    "font.size": 10,
    "axes.titlesize": 15,
    "axes.labelsize": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "grid.alpha": 0.25
})


def save_chart(filename):
    plt.tight_layout()
    plt.savefig(CHART_DIR / filename, bbox_inches="tight")
    plt.close()
    print(f"Created: {filename}")


# =========================================================
# 1. DAILY SALES TREND
# =========================================================

fig, ax = plt.subplots(figsize=(13, 6))

ax.plot(
    daily["SALES_DATE"],
    daily["TOTAL_REVENUE"],
    marker="o",
    linewidth=2,
    markersize=5
)

ax.set_title(
    "Daily Purchase-Event Revenue Proxy",
    fontweight="bold"
)
ax.set_xlabel("Date")
ax.set_ylabel("Revenue proxy (millions of dataset price units)")
ax.grid(axis="y", alpha=0.3)

# Display only October 2019 dates
ax.set_xlim(
    pd.Timestamp("2019-10-01"),
    pd.Timestamp("2019-10-31 23:59:59")
)

ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))

# Format revenue axis in millions
ax.yaxis.set_major_formatter(
    FuncFormatter(lambda value, position: f"{value / 1_000_000:.1f}M")
)

ax.tick_params(axis="x", rotation=45)

ax.text(
    0.01, -0.23,
    "Note: Revenue is calculated from purchase-event prices; "
    "it is not verified paid revenue.",
    transform=ax.transAxes,
    fontsize=9
)

save_chart("daily_sales_trend.png")


# =========================================================
# 2. DAILY PURCHASE EVENTS
# =========================================================

fig, ax = plt.subplots(figsize=(13, 6))

ax.bar(
    daily["SALES_DATE"],
    daily["TOTAL_PURCHASE_EVENTS"],
    width=0.8
)

ax.set_title(
    "Daily Purchase Event Volume",
    fontweight="bold"
)
ax.set_xlabel("Date")
ax.set_ylabel("Number of purchase events")
ax.grid(axis="y")

ax.tick_params(axis="x", rotation=45)

save_chart("daily_purchase_events.png")


# =========================================================
# 3. TOP 10 PRODUCTS BY REVENUE PROXY
# =========================================================

fig, ax = plt.subplots(figsize=(12, 7))

bars = ax.barh(
    top10["PRODUCT_ID"].astype(str),
    top10["TOTAL_REVENUE"]
)

ax.set_title(
    "Top 10 Products by Purchase-Event Revenue Proxy",
    fontweight="bold"
)
ax.set_xlabel("Revenue proxy (dataset price units)")
ax.set_ylabel("Product ID")
ax.grid(axis="x")

ax.bar_label(
    bars,
    labels=[
        f"{value:,.0f}"
        for value in top10["TOTAL_REVENUE"]
    ],
    padding=4,
    fontsize=8
)

ax.text(
    0.01, -0.14,
    "Note: Ranking is based on purchase-event price totals, "
    "not verified paid revenue.",
    transform=ax.transAxes,
    fontsize=9
)

save_chart("top_10_products.png")


# =========================================================
# 4. PRODUCT ENGAGEMENT ANALYSIS
# =========================================================

fig, axes = plt.subplots(
    1, 3,
    figsize=(17, 8)
)

metrics = [
    ("TOTAL_VIEWS", "Product Views"),
    ("TOTAL_CART_EVENTS", "Cart Events"),
    ("TOTAL_PURCHASE_EVENTS", "Purchase Events")
]

for ax, (column, title) in zip(axes, metrics):

    bars = ax.barh(
        top10["PRODUCT_ID"].astype(str),
        top10[column]
    )

    ax.set_title(title, fontweight="bold")
    ax.set_xlabel("Event count")
    ax.grid(axis="x")

    ax.bar_label(
        bars,
        labels=[
            f"{value:,.0f}"
            for value in top10[column]
        ],
        padding=3,
        fontsize=7
    )

    ax.tick_params(axis="y", labelsize=8)

fig.suptitle(
    "Engagement Metrics — Top 10 Products by Revenue Proxy",
    fontsize=16,
    fontweight="bold"
)

fig.text(
    0.5, 0.01,
    "Products are selected by revenue proxy. "
    "Views, cart events and purchase events are separate event counts.",
    ha="center",
    fontsize=9
)

plt.tight_layout(rect=[0, 0.05, 1, 0.94])
plt.savefig(
    CHART_DIR / "product_engagement.png",
    bbox_inches="tight"
)
plt.close()

print("Created: product_engagement.png")


# =========================================================
# 5. SEQUENTIAL CONVERSION FUNNEL
# =========================================================

funnel_labels = [
    "Sessions with View",
    "View Followed by Cart",
    "Completed Sequential Funnel"
]

funnel_values = [
    int(seq["SESSIONS_WITH_VIEW"]),
    int(seq["SESSIONS_WITH_VIEW_THEN_CART"]),
    int(seq["SESSIONS_COMPLETING_SEQUENTIAL_FUNNEL"])
]

fig, ax = plt.subplots(figsize=(11, 6))

bars = ax.bar(
    funnel_labels,
    funnel_values,
    width=0.55
)

ax.set_title(
    "Sequential E-Commerce Conversion Funnel",
    fontweight="bold"
)
ax.set_ylabel("Number of sessions")
ax.grid(axis="y")

ax.bar_label(
    bars,
    labels=[f"{value:,}" for value in funnel_values],
    padding=5
)

ax.tick_params(axis="x", rotation=10)

ax.text(
    0.01, -0.20,
    "Method: view → cart → purchase in timestamp order. "
    "Same-second event ordering cannot be established.",
    transform=ax.transAxes,
    fontsize=9
)

save_chart("sequential_conversion_funnel.png")


# =========================================================
# 6. STANDARD VS SEQUENTIAL FUNNEL RATE COMPARISON
# =========================================================

rate_labels = [
    "View to Cart",
    "Cart to Purchase",
    "View to Purchase"
]

standard_rates = [
    std["VIEW_TO_CART_RATE"],
    std["CART_TO_PURCHASE_RATE"],
    std["VIEW_TO_PURCHASE_RATE"]
]

sequential_rates = [
    seq["VIEW_TO_CART_RATE"],
    seq["CART_TO_PURCHASE_RATE"],
    seq["VIEW_TO_PURCHASE_RATE"]
]

x = range(len(rate_labels))
width = 0.36

fig, ax = plt.subplots(figsize=(11, 6))

bars1 = ax.bar(
    [i - width / 2 for i in x],
    standard_rates,
    width,
    label="Standard co-occurrence"
)

bars2 = ax.bar(
    [i + width / 2 for i in x],
    sequential_rates,
    width,
    label="Sequential"
)

ax.set_title(
    "Standard vs Sequential Funnel Rates",
    fontweight="bold"
)
ax.set_ylabel("Rate (%)")
ax.set_xticks(list(x))
ax.set_xticklabels(rate_labels)
ax.legend()
ax.grid(axis="y")

ax.bar_label(
    bars1,
    fmt="%.2f%%",
    padding=3,
    fontsize=8
)

ax.bar_label(
    bars2,
    fmt="%.2f%%",
    padding=3,
    fontsize=8
)

ax.text(
    0.01, -0.20,
    "Note: The two methods use different event-ordering rules. "
    "Compare as methodology-specific metrics, not identical cohorts.",
    transform=ax.transAxes,
    fontsize=9
)

save_chart("funnel_comparison.png")


# =========================================================
# 7. INTERACTIVE PLOTLY DASHBOARD
# =========================================================

fig = make_subplots(
    rows=3,
    cols=1,
    subplot_titles=(
        "Daily Purchase-Event Revenue Proxy",
        "Top 10 Products by Revenue Proxy",
        "Standard vs Sequential Funnel Rates"
    ),
    vertical_spacing=0.14,
    specs=[
        [{"type": "scatter"}],
        [{"type": "bar"}],
        [{"type": "bar"}]
    ]
)

# Daily trend
fig.add_trace(
    go.Scatter(
        x=daily["SALES_DATE"],
        y=daily["TOTAL_REVENUE"],
        mode="lines+markers",
        name="Daily revenue proxy",
        hovertemplate=(
            "Date: %{x|%d %b %Y}<br>"
            "Revenue proxy: %{y:,.2f}<extra></extra>"
        )
    ),
    row=1,
    col=1
)

# Top 10 products
fig.add_trace(
    go.Bar(
        x=top10["TOTAL_REVENUE"],
        y=top10["PRODUCT_ID"].astype(str),
        orientation="h",
        name="Revenue proxy",
        hovertemplate=(
            "Product ID: %{y}<br>"
            "Revenue proxy: %{x:,.2f}<extra></extra>"
        )
    ),
    row=2,
    col=1
)

# Funnel rates
fig.add_trace(
    go.Bar(
        x=rate_labels,
        y=standard_rates,
        name="Standard co-occurrence",
        hovertemplate="%{x}: %{y:.2f}%<extra></extra>"
    ),
    row=3,
    col=1
)

fig.add_trace(
    go.Bar(
        x=rate_labels,
        y=sequential_rates,
        name="Sequential",
        hovertemplate="%{x}: %{y:.2f}%<extra></extra>"
    ),
    row=3,
    col=1
)

fig.update_layout(
    title={
        "text": (
            "E-Commerce Sales & Customer Behaviour Analytics"
            "<br><sup>October 2019 | Event-level dataset</sup>"
        ),
        "x": 0.5
    },
    height=1450,
    template="plotly_white",
    barmode="group",
    hovermode="closest",
    legend_title="Metric / Method",
    margin=dict(t=120, b=110, l=100, r=60)
)

fig.update_yaxes(
    title_text="Revenue proxy (dataset price units)",
    row=1,
    col=1
)

fig.update_yaxes(
    title_text="Product ID",
    row=2,
    col=1
)

fig.update_yaxes(
    title_text="Rate (%)",
    row=3,
    col=1
)

fig.add_annotation(
    text=(
        "Revenue is a purchase-event price proxy, not verified paid revenue. "
        "Funnel rates use different methodologies. "
        "Sequential ordering uses event timestamps."
    ),
    xref="paper",
    yref="paper",
    x=0.5,
    y=-0.075,
    showarrow=False,
    font=dict(size=11)
)

dashboard_path = (
    INTERACTIVE_DIR / "ecommerce_analytics.html"
)

fig.write_html(
    dashboard_path,
    include_plotlyjs=True
)

# Remove trailing spaces and tabs from generated HTML
html_content = dashboard_path.read_text(encoding="utf-8")

cleaned_html = "\n".join(
    line.rstrip(" \t")
    for line in html_content.splitlines()
) + "\n"

dashboard_path.write_text(cleaned_html, encoding="utf-8")

print("Created: ecommerce_analytics.html")


# =========================================================
# COMPLETION SUMMARY
# =========================================================

print("\n========== VISUALIZATION SUMMARY ==========")

print("Static charts created: 6")
print(f"Chart folder: {CHART_DIR}")
print(f"Interactive dashboard: {dashboard_path}")

print("\nVisualization generation completed.")
