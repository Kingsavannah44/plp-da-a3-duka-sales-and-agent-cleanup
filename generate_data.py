# generate_data.py
# Run this script to regenerate all datasets used in this project.
# It produces: duka_sales.csv, agents.csv, agent_transactions.csv

import numpy as np
import pandas as pd

# ── Engagement 1: Duka Electronics ────────────────────────────────────────────
# seed = 2026, 1 000 orders, January–June 2026

rng1 = np.random.default_rng(2026)
n1 = 1000

branches = ["Nairobi CBD", "Westlands", "Mombasa", "Kisumu", "Nakuru"]
categories = ["Phones", "Laptops", "TVs", "Accessories", "Tablets"]
channels = ["In-Store", "Online"]

duka = pd.DataFrame({
    "order_id": [f"ORD{i:04d}" for i in range(1, n1 + 1)],
    "order_date": (
        pd.to_datetime("2026-01-01")
        + pd.to_timedelta(rng1.integers(0, 181, n1), unit="D")
    ).strftime("%Y-%m-%d"),
    "branch": rng1.choice(branches, n1),
    "channel": rng1.choice(channels, n1),
    "product": [
        f"Product_{rng1.integers(1, 31)}" for _ in range(n1)
    ],
    "category": rng1.choice(categories, n1),
    "quantity": rng1.integers(1, 6, n1),
    "unit_price": rng1.choice(
        [4_999, 7_499, 9_999, 14_999, 19_999, 24_999, 28_999, 34_999, 49_999, 79_999],
        n1,
    ),
})

duka.to_csv("duka_sales.csv", index=False)
print(f"duka_sales.csv written  → {len(duka):,} rows")

# ── Engagement 2: Mobile-money agent network ──────────────────────────────────
# seed = 44, 600 base transactions + injected problems

rng2 = np.random.default_rng(44)
n2 = 600

agents = pd.DataFrame({
    "agent_id": [f"AG{i:03d}" for i in range(1, 21)],
    "county": rng2.choice(["Nairobi", "Kiambu", "Nakuru", "Mombasa", "Kisumu"], 20),
    "onboarded": pd.date_range("2024-01-01", periods=20, freq="MS")
    .strftime("%Y-%m-%d"),
})

txns = pd.DataFrame({
    "txn_id": [f"TX{i:05d}" for i in range(1, n2 + 1)],
    "agent_id": rng2.choice(agents["agent_id"], n2),
    "txn_type": rng2.choice(
        ["Deposit", "withdrawal", "DEPOSIT ", "Withdrawal", "deposit"], n2
    ),
    "amount": rng2.lognormal(7.5, 0.8, n2).round(0).astype(str),
    "txn_date": (
        pd.to_datetime("2026-03-01")
        + pd.to_timedelta(rng2.integers(0, 60, n2), unit="D")
    ).strftime("%Y-%m-%d"),
})

idx = rng2.choice(n2, 30, replace=False)
txns.loc[idx[:15], "amount"] = np.nan
txns.loc[idx[15:20], "amount"] = "N/A"
txns.loc[idx[20:25], "amount"] = "250000"
txns.loc[idx[25:], "txn_date"] = txns.loc[idx[25:], "txn_date"].str.replace("-", "/")

txns = pd.concat([txns, txns.sample(12, random_state=1)], ignore_index=True)
txns.loc[rng2.choice(len(txns), 8, replace=False), "agent_id"] = "AG099"

agents.to_csv("agents.csv", index=False)
txns.to_csv("agent_transactions.csv", index=False)
print(f"agents.csv written            → {len(agents):,} rows")
print(f"agent_transactions.csv written → {len(txns):,} rows")
