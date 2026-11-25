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

- **Kisumu** is the top-performing branch with total H1 revenue of **KES 19,331,848** — ahead of Nakuru (KES 17,397,414) — despite not being the busiest city, suggesting it carries a higher average order value per transaction.
- **Product_21** leads both the revenue chart (**KES 4,499,351**) and the units-sold chart (**149 units**), but Product_15 ranks third by units while missing the revenue top-3 entirely, showing that volume and value rankings diverge for lower-priced items.
- **Weekend orders** (Saturday + Sunday) represent **279 of 1,000 orders** (27.9 %) but carry an average revenue of **KES 84,510** — KES 4,409 more per order than weekdays — indicating weekend shoppers skew toward Premium products.
- **March 2026** is the best revenue month at **KES 15,423,942**, while February is the worst at **KES 10,983,572** — a gap of **40.4 %** that the sales team should investigate for seasonal or campaign-driven causes.
- **Premium Online orders from Nairobi CBD and Mombasa** total **60 orders** with combined revenue of **KES 8,095,834**, confirming that the coastal and capital digital channels are the highest-value customer segment.

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
