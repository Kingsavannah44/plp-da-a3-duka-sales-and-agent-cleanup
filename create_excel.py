"""
create_excel.py
===============
Builds excel/duka_branch_summary.xlsx with:
  - Sheet 1 "SUMIFS_Branch"  : branch revenue table (SUMIFS logic) + Region column (XLOOKUP logic)
  - Sheet 2 "Pivot_Branch_Channel" : pivot table of revenue by branch × channel

Run after generate_data.py has produced duka_sales.csv.
"""

import os
import pandas as pd
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

os.makedirs("excel", exist_ok=True)

# ── Load data ────────────────────────────────────────────────────────────────
df = pd.read_csv("duka_sales.csv", parse_dates=["order_date"])
df["revenue"] = df["quantity"] * df["unit_price"]

# ── XLOOKUP region mapping ───────────────────────────────────────────────────
region_map = {
    "Nairobi CBD": "Central",
    "Westlands":   "Central",
    "Mombasa":     "Coast",
    "Kisumu":      "Nyanza",
    "Nakuru":      "Rift Valley",
}

# ── SUMIFS equivalent: branch revenue total ──────────────────────────────────
branch_revenue = (
    df.groupby("branch")["revenue"]
    .sum()
    .reset_index()
    .rename(columns={"revenue": "Total_Revenue"})
    .sort_values("Total_Revenue", ascending=False)
    .reset_index(drop=True)
)
branch_revenue["Region"] = branch_revenue["branch"].map(region_map)

# ── Pivot: revenue by branch × channel ───────────────────────────────────────
pivot = df.pivot_table(
    index="branch",
    columns="channel",
    values="revenue",
    aggfunc="sum",
    fill_value=0,
    margins=True,
    margins_name="Grand Total",
)
pivot = pivot.reset_index()

# ── Build workbook ───────────────────────────────────────────────────────────
wb = openpyxl.Workbook()

# ── Sheet 1: SUMIFS_Branch ───────────────────────────────────────────────────
ws1 = wb.active
ws1.title = "SUMIFS_Branch"

header_fill = PatternFill("solid", fgColor="1F4E79")
header_font = Font(color="FFFFFF", bold=True)
alt_fill    = PatternFill("solid", fgColor="D6E4F0")
thin        = Side(style="thin", color="AAAAAA")
border      = Border(left=thin, right=thin, top=thin, bottom=thin)

headers = ["Branch", "Total_Revenue (KES)", "Region", "SUMIFS Formula Note"]
ws1.append(headers)
for cell in ws1[1]:
    cell.fill = header_font and header_fill
    cell.font = header_font
    cell.alignment = Alignment(horizontal="center")
    cell.border = border

for i, row in branch_revenue.iterrows():
    data_row = [
        row["branch"],
        row["Total_Revenue"],
        row["Region"],
        f'=SUMIFS(revenue,branch,"{row["branch"]}")',
    ]
    ws1.append(data_row)
    xl_row = i + 2
    for j, cell in enumerate(ws1[xl_row], 1):
        cell.border = border
        if i % 2 == 0:
            cell.fill = alt_fill
        if j == 2:
            cell.number_format = '#,##0'
            cell.alignment = Alignment(horizontal="right")

# Column widths
ws1.column_dimensions["A"].width = 18
ws1.column_dimensions["B"].width = 22
ws1.column_dimensions["C"].width = 16
ws1.column_dimensions["D"].width = 40

# Title
ws1.insert_rows(1)
ws1["A1"] = "Duka Electronics — Branch Revenue Summary (H1 2026)"
ws1["A1"].font = Font(bold=True, size=13, color="1F4E79")
ws1.merge_cells("A1:D1")

# ── Sheet 2: Pivot_Branch_Channel ────────────────────────────────────────────
ws2 = wb.create_sheet("Pivot_Branch_Channel")

ws2.append(["Duka Electronics — Revenue by Branch & Channel (H1 2026)"])
ws2["A1"].font = Font(bold=True, size=13, color="1F4E79")
ws2.merge_cells(f"A1:{get_column_letter(len(pivot.columns))}1")
ws2.append([])  # blank spacer

col_names = list(pivot.columns)
ws2.append(col_names)
for cell in ws2[3]:
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = Alignment(horizontal="center")
    cell.border = border

for i, row in pivot.iterrows():
    ws2.append(list(row))
    xl_row = i + 4
    for j, cell in enumerate(ws2[xl_row], 1):
        cell.border = border
        if j > 1:
            cell.number_format = '#,##0'
            cell.alignment = Alignment(horizontal="right")
        if str(row.get("branch", row.get(col_names[0], ""))) == "Grand Total":
            cell.font = Font(bold=True)
            cell.fill = PatternFill("solid", fgColor="BDD7EE")

for col_idx, col_name in enumerate(col_names, 1):
    ws2.column_dimensions[get_column_letter(col_idx)].width = 18

# ── Save ─────────────────────────────────────────────────────────────────────
path = "excel/duka_branch_summary.xlsx"
wb.save(path)
print(f"Saved → {path}")

# ── Verify totals match pandas ───────────────────────────────────────────────
pandas_total = df["revenue"].sum()
xl_total     = branch_revenue["Total_Revenue"].sum()
match        = abs(pandas_total - xl_total) < 1

print(f"\nPandas grand total  : KES {pandas_total:,.0f}")
print(f"Excel SUMIFS total  : KES {xl_total:,.0f}")
print(f"Totals match        : {match}")
