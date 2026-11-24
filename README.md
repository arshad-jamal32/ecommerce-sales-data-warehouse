# E-Commerce Sales Data Warehouse | Snowflake

An end-to-end e-commerce analytics data warehouse project built using Snowflake SQL and Python. The project processes event-level e-commerce behavior data and transforms it into analytical datasets, quality checks, and visual reports.

## 1. Project Overview

This project uses the REES46 e-commerce behavior dataset for October 2019 to build a Snowflake-based data warehouse.

The warehouse follows a Bronze-Silver-Gold architecture:

- **Bronze:** Stores the raw event-level data.
- **Silver:** Cleans and prepares the data for analysis.
- **Gold:** Contains analytical tables for sales, product performance, customer behavior, and conversion funnels.

Python scripts extract Gold-layer data, validate exported datasets, and generate static and interactive visualizations.

## 2. Technology Stack

| Technology | Purpose |
|---|---|
| Snowflake | Cloud data warehouse |
| Snowflake SQL | Data transformation, analytics, and quality checks |
| Python 3.11.9 | Data extraction, validation, and visualization |
| Pandas | Data manipulation |
| NumPy | Numerical operations |
| Matplotlib | Static charts |
| Plotly | Interactive dashboard |
| Pillow | Image validation |
| python-dotenv | Environment variable management |
| Git | Version control |

## 3. Data Source

- Dataset: REES46 E-Commerce Behavior Data
- Period: October 2019
- Data type: Event-level user behavior
- Events include product views, cart interactions, and purchase events.

The original dataset is large and is not included in this repository. Obtain it from its original Kaggle source and configure the Snowflake ingestion process separately.

## 4. Data Warehouse Architecture

```text
             E-Commerce Event Dataset
                       |
                       v
                BRONZE LAYER
                 Raw Events
                       |
                       v
                 SILVER LAYER
             Cleaned and Prepared Data
                       |
                       v
                  GOLD LAYER
              Analytical Data Models
                       |
          +------------+------------+
          |            |            |
          v            v            v
      Daily Sales  Product       Customer
                   Performance   Behavior
          |
          v
     Conversion Funnels
          |
          v
   Python Data Extraction
          |
          v
   CSV Validation and Audits
          |
          v
   Static Charts and Interactive Dashboard
```

## 5. Gold Layer Tables

| Table | Description |
|---|---|
| DAILY_SALES | Daily purchase-event counts and revenue proxy |
| PRODUCT_PERFORMANCE | Product views, cart events, and purchase events |
| CUSTOMER_BEHAVIOR | Customer-level behavioral metrics |
| CONVERSION_FUNNEL | Session-level event co-occurrence funnel |
| CONVERSION_FUNNEL_SEQUENTIAL | Timestamp-based sequential funnel |

## 6. Key Project Metrics

The following metrics were generated from the October 2019 dataset:

| Metric | Result |
|---|---:|
| Raw events loaded | 42,448,764 |
| Daily sales records | 31 |
| Product performance records | 166,794 |
| Customer behavior records | 3,022,290 |
| Purchase events | 742,849 |
| Product view events | 40,779,399 |
| Cart events | 926,516 |
| Purchase-event revenue proxy | 229,957,502.27 |

These are event-level analytical metrics, not verified order or payment records.

## 7. Data Quality and Validation

The project includes SQL and Python validation checks covering:

- Missing values and data type validation
- Non-positive product price analysis
- Inconsistent product brand analysis
- Exact duplicate record analysis
- Gold-layer duplicate key checks
- Referential integrity checks
- Gold metrics sanity checks
- Exported CSV schema and data validation
- Funnel calculation and consistency checks
- Visualization file validation

### Validation results

- Bronze ingestion: 42,448,764 rows loaded, 0 reported load errors.
- Gold duplicate key checks: 0 duplicate keys.
- Referential integrity: 0 missing referenced rows.
- Gold sanity checks: 0 invalid rows.
- Customer event count reconciliation: no mismatches.
- Exported CSV validation: all configured checks passed.
- Visualization audit: all 6 static charts and the interactive dashboard passed structural checks.

## 8. SQL Implementation

The `sql/` directory contains 39 numbered SQL scripts.

| Script range | Implementation |
|---|---|
| 01-05 | Database, warehouse, stage, raw table, and ingestion setup |
| 06-10 | Bronze profiling, data quality analysis, and Silver preparation |
| 11-18 | Product and user dimensions, Gold tables, and standard funnel |
| 19-27 | Data quality audits, duplicate analysis, integrity checks, and sequential funnel |
| 28-33 | MERGE, Streams, and Tasks demonstrations |
| 34-39 | Time Travel, data restoration, zero-copy cloning, and clone testing |

Execute scripts in their intended order and review their comments and prerequisites before running them.

## 9. Python Workflow

The `python/` directory contains scripts for:

1. `snowflake_connection.py` - Snowflake connection and configuration.
2. `inspect_gold_tables.py` - Gold table inventory and row counts.
3. `inspect_gold_schema.py` - Gold schema and column inspection.
4. `extract_gold_data.py` - Export Gold data into CSV files.
5. `validate_extracted_data.py` - Validate exported datasets.
6. `create_visualizations.py` - Generate charts and the interactive dashboard.
7. `audit_visualizations.py` - Validate generated visualization files.

## 10. Project Setup

### Prerequisites

- Python 3.11
- A Snowflake account
- Access to the required Snowflake database, schema, warehouse, and role
- The original dataset for a fresh warehouse build

### Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd ecommerce-sales-data-warehouse
```

### Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### Configure Snowflake credentials

Create a local `.env` file using the example:

```powershell
Copy-Item .env.example .env
```

Update the placeholders in `.env` with your own Snowflake connection details.

**Never commit `.env` or expose Snowflake credentials.**

### Run the Python workflow

After the Snowflake Gold tables have been created:

```powershell
python .\python\inspect_gold_tables.py
python .\python\inspect_gold_schema.py
python .\python\extract_gold_data.py
python .\python\validate_extracted_data.py
python .\python\create_visualizations.py
python .\python\audit_visualizations.py
```

## 11. Reports and Visualizations

Generated outputs are stored under `reports/`.

### Static charts

- Daily purchase events
- Daily sales trend
- Funnel comparison
- Product engagement
- Sequential conversion funnel
- Top 10 products

### Exported datasets

- `daily_sales.csv`
- `sequential_funnel.csv`
- `standard_funnel.csv`
- `top_20_products.csv`

### Interactive dashboard

`reports/interactive/ecommerce_analytics.html`

Open the HTML file in a web browser to explore the interactive analytics dashboard.

## 12. Important Analytical Limitations

The dataset contains behavioral events, not a complete order or payment ledger. Therefore:

1. A purchase event must not be interpreted as a verified order or successful payment.
2. The sum of prices on purchase events is a revenue proxy, not verified paid revenue.
3. The analysis covers October 2019 only and should not be treated as a current business performance report.
4. Event percentages represent event shares, not necessarily conversion rates.
5. The standard funnel measures session-level event co-occurrence, not chronological progression.
6. The sequential funnel uses strict timestamp ordering. Events recorded within the same second cannot be reliably ordered.
7. A session's cart and purchase events may refer to different products.
8. Conflicting product brands are handled deterministically; the selected brand is not necessarily authoritative.

These limitations are important when interpreting the analytical results.

## 13. Repository Structure

```text
ecommerce-sales-data-warehouse/
|
|-- documentation/
|   |-- data_dictionary.md
|
|-- python/
|   |-- snowflake_connection.py
|   |-- inspect_gold_tables.py
|   |-- inspect_gold_schema.py
|   |-- extract_gold_data.py
|   |-- validate_extracted_data.py
|   |-- create_visualizations.py
|   |-- audit_visualizations.py
|
|-- reports/
|   |-- charts/
|   |-- data/
|   |-- interactive/
|
|-- sql/
|   |-- 01_database_schema_setup.sql
|   |-- ...
|   |-- 39_clone_independence_test.sql
|
|-- .env.example
|-- .gitignore
|-- README.md
|-- requirements.txt
```

## 14. Future Improvements

- Automate incremental ingestion and transformation.
- Introduce scheduled data quality monitoring.
- Add a BI reporting layer.
- Extend analysis to additional monthly datasets.
- Implement least-privilege Snowflake roles for production-style access.
- Add automated testing to the development workflow.

---

**Project Focus:** Data Warehousing | Snowflake SQL | ETL | Data Quality | E-Commerce Analytics | Python | Data Visualization
