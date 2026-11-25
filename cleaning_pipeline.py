"""
cleaning_pipeline.py
====================
Reusable cleaning pipeline for the mobile-money agent-network dataset.

Public API
----------
clean_agent_data(txns, agents) -> (clean_df, log_df)
    Apply all cleaning rules to the raw transactions DataFrame, merge with
    the agent register, and return the cleaned DataFrame plus a cleaning log.
"""

import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _log_entry(log: list, step: str, dimension: str, column: str,
               rows_affected: int, action: str) -> None:
    """Append one entry to the running cleaning log."""
    log.append({
        "step": step,
        "dimension": dimension,
        "column": column,
        "rows_affected": rows_affected,
        "action": action,
    })


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------

def clean_agent_data(txns: pd.DataFrame,
                     agents: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Clean the raw agent transactions and merge with the agent register.

    Parameters
    ----------
    txns : pd.DataFrame
        Raw transactions loaded from agent_transactions.csv.
    agents : pd.DataFrame
        Agent register loaded from agents.csv.

    Returns
    -------
    clean_df : pd.DataFrame
        Cleaned and merged transactions. Contains:
        - txn_id, agent_id, txn_type (Deposit | Withdrawal)
        - amount (float), txn_date (datetime64)
        - amount_imputed (bool), is_outlier (bool)
        - county (from agents register)
    log_df : pd.DataFrame
        One row per cleaning step with columns:
        step | dimension | column | rows_affected | action
    """
    log: list[dict] = []
    df = txns.copy()

    # ── 1. Duplicates ────────────────────────────────────────────────────────
    before = len(df)
    df = df.drop_duplicates(subset="txn_id", keep="first").reset_index(drop=True)
    removed = before - len(df)
    _log_entry(log, "1_remove_duplicates", "Uniqueness", "txn_id",
               removed, f"Removed {removed} duplicate txn_id rows (kept first occurrence).")

    # ── 2. Standardise txn_type ──────────────────────────────────────────────
    # Raw values: "Deposit", "withdrawal", "DEPOSIT ", "Withdrawal", "deposit"
    raw_bad = df["txn_type"].str.strip().str.title().ne(
        df["txn_type"].str.strip().str.title()
    ).sum()  # just for counting non-standard before fix

    df["txn_type"] = df["txn_type"].str.strip().str.title()
    # After strip+title: "Deposit" or "Withdrawal" — both correct.
    # Confirm only those two values exist.
    unexpected = df["txn_type"].isin(["Deposit", "Withdrawal"]) == False
    n_unexpected = unexpected.sum()
    _log_entry(log, "2_standardise_txn_type", "Consistency", "txn_type",
               n_unexpected,
               "Applied str.strip().str.title() → 'Deposit' | 'Withdrawal'. "
               f"{n_unexpected} rows still unexpected after fix (should be 0).")

    # ── 3. Fix txn_date formats ───────────────────────────────────────────────
    # Some dates use '/' as separator instead of '-'
    slash_mask = df["txn_date"].str.contains("/", na=False)
    n_slash = slash_mask.sum()
    df["txn_date"] = df["txn_date"].str.replace("/", "-", regex=False)
    df["txn_date"] = pd.to_datetime(df["txn_date"], format="%Y-%m-%d", errors="coerce")
    n_unparseable = df["txn_date"].isna().sum()
    _log_entry(log, "3a_fix_date_separators", "Validity", "txn_date",
               n_slash, f"Replaced '/' with '-' in {n_slash} date strings.")
    _log_entry(log, "3b_parse_txn_date", "Validity", "txn_date",
               n_unparseable,
               f"Converted txn_date to datetime64. {n_unparseable} rows could not be parsed → NaT.")

    # ── 4. Convert amount to numeric ─────────────────────────────────────────
    # Pandas reads literal "N/A" as NaN when na_values includes it, but we
    # force it here to be safe. Already-NaN cells stay NaN.
    df["amount"] = df["amount"].replace("N/A", np.nan)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    n_non_numeric = df["amount"].isna().sum()
    _log_entry(log, "4_convert_amount_numeric", "Validity", "amount",
               n_non_numeric,
               "Replaced 'N/A' strings, then cast to float. "
               f"{n_non_numeric} rows are NaN after conversion.")

    # ── 5. Treat missing amounts ──────────────────────────────────────────────
    # Decision: impute missing amounts with the per-txn_type median.
    # Rationale: the median is robust to the injected KES 250 000 spike values
    # and preserves the natural split between deposit and withdrawal amounts.
    # Rows with imputed values are flagged so downstream users can filter them.
    df["amount_imputed"] = df["amount"].isna()
    n_imputed = df["amount_imputed"].sum()
    for tt in ["Deposit", "Withdrawal"]:
        mask = (df["txn_type"] == tt) & df["amount"].isna()
        median_val = df.loc[df["txn_type"] == tt, "amount"].median()
        df.loc[mask, "amount"] = median_val
    _log_entry(log, "5_impute_missing_amounts", "Completeness", "amount",
               n_imputed,
               f"Imputed {n_imputed} missing amounts with per-txn_type median. "
               "Flag column 'amount_imputed' marks these rows.")

    # ── 6. Flag IQR outliers ──────────────────────────────────────────────────
    Q1 = df["amount"].quantile(0.25)
    Q3 = df["amount"].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    df["is_outlier"] = (df["amount"] < lower) | (df["amount"] > upper)
    n_outliers = df["is_outlier"].sum()
    # Specifically investigate the 250 000 values
    n_250k = (df["amount"] == 250_000).sum()
    _log_entry(log, "6_flag_iqr_outliers", "Validity", "amount",
               n_outliers,
               f"IQR fences: [{lower:.0f}, {upper:.0f}]. "
               f"{n_outliers} rows flagged as outliers. "
               f"{n_250k} rows have amount == 250 000 (deliberately injected). "
               "Recommendation: hold KES 250 000 values for manual review — "
               "they may be legitimate large transactions or test records; "
               "do not drop without business confirmation.")

    # ── 7. Merge with agent register ─────────────────────────────────────────
    before_merge = len(df)
    # Identify unknown agents before merge
    known_ids = set(agents["agent_id"])
    unknown_mask = ~df["agent_id"].isin(known_ids)
    n_unknown = unknown_mask.sum()
    _log_entry(log, "7_unknown_agents", "Integrity", "agent_id",
               n_unknown,
               f"{n_unknown} transactions reference agent AG099 which is not in "
               "the agent register. These rows are retained with county = NaN "
               "so they appear in counts but are excluded from county summaries.")

    df = df.merge(agents[["agent_id", "county"]], on="agent_id", how="left")
    assert len(df) == before_merge, "Merge changed row count — check for fan-out."
    _log_entry(log, "8_merge_agents", "Completeness", "county",
               df["county"].isna().sum(),
               "Left-joined agents register on agent_id. "
               f"{df['county'].isna().sum()} rows have no county (unknown agents).")

    # ── 8. Final type safety ─────────────────────────────────────────────────
    df["amount"] = df["amount"].astype(float)

    # Build log DataFrame
    log_df = pd.DataFrame(log)

    return df, log_df
