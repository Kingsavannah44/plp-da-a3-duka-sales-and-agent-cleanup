"""
build_outputs.py
Generates the two committed output CSVs from the generated raw data.
Run once after generate_data.py.
"""
import os
import pandas as pd
import numpy as np
from cleaning_pipeline import clean_agent_data

os.makedirs("outputs", exist_ok=True)

# ── Engagement 1: premium_online_coast_capital.csv ───────────────────────────
df = pd.read_csv("duka_sales.csv", parse_dates=["order_date"])
df["revenue"]    = df["quantity"] * df["unit_price"]
df["month"]      = df["order_date"].dt.to_period("M")
df["weekday"]    = df["order_date"].dt.day_name()
df["is_weekend"] = df["order_date"].dt.dayofweek >= 5
df["price_band"] = np.where(df["unit_price"] >= 28_000, "Premium", "Value")

premium_online = df[
    (df["price_band"] == "Premium") &
    (df["channel"]    == "Online")  &
    (df["branch"].isin(["Nairobi CBD", "Mombasa"]))
].copy()

premium_online.to_csv("outputs/premium_online_coast_capital.csv", index=False)
print(f"premium_online_coast_capital.csv → {len(premium_online)} rows")
print(f"  Total revenue: KES {premium_online['revenue'].sum():,.0f}")

# ── Engagement 2: agent_transactions_clean.csv ────────────────────────────────
txns   = pd.read_csv("agent_transactions.csv", keep_default_na=False)
agents = pd.read_csv("agents.csv")

clean_df, log_df = clean_agent_data(txns, agents)
clean_df.to_csv("outputs/agent_transactions_clean.csv", index=False)

print(f"\nagent_transactions_clean.csv → {len(clean_df)} rows")
print(f"  Columns: {list(clean_df.columns)}")
print(f"  Duplicate txn_ids: {clean_df['txn_id'].duplicated().sum()}")
print(f"  txn_type values:   {sorted(clean_df['txn_type'].unique())}")
print(f"  amount dtype:      {clean_df['amount'].dtype}")
print(f"  txn_date dtype:    {clean_df['txn_date'].dtype}")
print(f"  amount_imputed:    {clean_df['amount_imputed'].sum()} rows")
print(f"  is_outlier:        {clean_df['is_outlier'].sum()} rows")
print(f"  county NaN (AG099):{clean_df['county'].isna().sum()} rows")

print("\nCleaning log:")
print(log_df.to_string(index=False))
