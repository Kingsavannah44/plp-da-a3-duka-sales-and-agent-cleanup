# plp-da-a3-duka-sales-and-agent-cleanup

**PLP Data Analytics — Assignment 3 · Week 3**  
Two client engagements in one repository: Duka Electronics sales exploration and a mobile-money agent-network data audit & cleaning.

---

## Repository layout

```
├── generate_data.py              # Regenerates all raw CSVs (run first)
├── create_excel.py               # Builds excel/duka_branch_summary.xlsx
├── cleaning_pipeline.py          # Reusable clean_agent_data() function
├── duka_sales_exploration.ipynb  # Engagement 1 notebook
├── agent_cleanup.ipynb           # Engagement 2 notebook
├── requirements.txt
├── outputs/
│   ├── premium_online_coast_capital.csv
│   └── agent_transactions_clean.csv
└── excel/
    └── duka_branch_summary.xlsx
```

> **Raw CSVs are not committed.** `duka_sales.csv`, `agents.csv`, and `agent_transactions.csv` are listed in `.gitignore`; reviewers regenerate them with `generate_data.py`.

---

## How to regenerate data and run notebooks

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate all raw CSVs
python generate_data.py

# 3. Build the Excel workbook
python create_excel.py

# 4. Open and run notebooks top-to-bottom
jupyter notebook duka_sales_exploration.ipynb
jupyter notebook agent_cleanup.ipynb
```

Restart the kernel before running each notebook to ensure reproducibility.

---

## Engagement 1 — Duka Electronics

**Dataset:** `duka_sales.csv` — 1 000 orders, seed 2026, January–June 2026.

### Executive Summary

- **Nairobi CBD** is the top-performing branch with the highest total revenue across all 5 branches, driven by a large share of Premium-tier orders averaging above KES 28,000 per unit.
- The **3 best-selling products by units** are all in the Accessories and Phones categories, yet the **top 3 by revenue** are dominated by Laptops and TVs — reflecting that high-volume does not equal high-value.
- **Weekend orders** (Saturday + Sunday) account for roughly **29 %** of all orders but generate a higher average order revenue than weekday orders, suggesting weekend shoppers skew toward Premium products.
- **March 2026** is the single best revenue month, outperforming the worst month by more than **40 %**, pointing to a mid-quarter demand surge worth investigating for promotional causes.
- **Premium Online orders from Nairobi and Mombasa** total **48 orders** with combined revenue exceeding **KES 2.1 million**, confirming that the coastal and capital digital channels are the highest-value customer segment.

---

## Engagement 2 — Mobile Money Agent Network

**Datasets:** `agent_transactions.csv` (seed 44) + `agents.csv`

### Before and after row counts

| Stage | Rows |
|---|---|
| Raw `agent_transactions.csv` | 612 |
| After removing 12 duplicates | 600 |
| After merge (left join — no fan-out) | 600 |
| Written to `outputs/agent_transactions_clean.csv` | 600 |

### Injected problems found

| Issue | Dimension | Rows |
|---|---|---|
| Duplicate `txn_id` (12 appended rows) | Uniqueness | 12 |
| Inconsistent `txn_type` casing/spaces | Consistency | ~400 |
| Date separator `"/"` instead of `"-"` | Validity | 5 |
| Missing `amount` (NaN) | Completeness | 15 |
| Missing `amount` (literal `"N/A"`) | Completeness | 5 |
| `amount` stored as string | Validity | 612 |
| Suspicious `amount == 250 000` | Validity | 5 |
| Unknown agent `AG099` | Integrity | 8 |

---

## Cleaning pipeline

`cleaning_pipeline.py` exports `clean_agent_data(txns, agents) -> (clean_df, log_df)`.  
See the module docstring and `agent_cleanup.ipynb` Section 4 for the full log.
