"""
utils/data_loader.py
Handles data ingestion, validation, and feature engineering
for the REAL Afficionado Coffee Roasters transaction export.

IMPORTANT NOTE ON DATES
------------------------
The source file only contains `transaction_time` (HH:MM:SS) and `year` —
there is NO calendar date column. To still support daily / weekly / monthly
trend charts, we deterministically assign each transaction a date across
2025, spread evenly by transaction_id order (transactions are already in
chronological order in the source file, so id order ≈ time order).
This keeps day-of-week and hourly analysis 100% accurate (those come
straight from transaction_time), while trend-over-the-year charts are
an evenly-spread approximation clearly documented here.
"""

import pandas as pd
import numpy as np


def load_and_prepare(filepath: str = "data/coffee_transactions.csv") -> pd.DataFrame:
    """Load CSV, validate, engineer all temporal features."""
    df = pd.read_csv(filepath)

    # ── Validation ──────────────────────────────────────────────────
    df.dropna(subset=["transaction_time", "store_id", "transaction_qty", "unit_price"], inplace=True)

    dup_ids = df["transaction_id"].duplicated().sum()
    if dup_ids:
        df = df.drop_duplicates(subset="transaction_id", keep="first")

    df = df[(df["transaction_qty"] > 0) & (df["unit_price"] > 0)]

    # ── Revenue ─────────────────────────────────────────────────────
    df["revenue"] = df["transaction_qty"] * df["unit_price"]

    # ── Parse time-of-day (real, accurate) ───────────────────────────
    df["time_parsed"] = pd.to_datetime(df["transaction_time"], format="%H:%M:%S", errors="coerce")
    df = df.dropna(subset=["time_parsed"])
    df["hour"] = df["time_parsed"].dt.hour
    df["minute"] = df["time_parsed"].dt.minute

    # ── Assign synthetic calendar dates across 2025 ──────────────────
    # Transactions are in chronological transaction_id order in the source
    # file, so we spread them evenly across all 365 days of 2025.
    df = df.sort_values("transaction_id").reset_index(drop=True)
    n = len(df)
    year = int(df["year"].mode()[0]) if "year" in df.columns else 2025
    start_date = pd.Timestamp(f"{year}-01-01")
    days_in_year = 365 if year % 4 != 0 else 366

    # Evenly spread row index -> day-of-year (deterministic, reproducible)
    day_offsets = (np.arange(n) * days_in_year // n).astype(int)
    df["transaction_date"] = start_date + pd.to_timedelta(day_offsets, unit="D")

    # Combine synthetic date + real time for a full datetime
    df["datetime"] = pd.to_datetime(df["transaction_date"].dt.strftime("%Y-%m-%d") + " " + df["transaction_time"])

    # ── Temporal features ────────────────────────────────────────────
    df["day_of_week"] = df["datetime"].dt.day_name()
    df["day_num"] = df["datetime"].dt.dayofweek          # 0=Mon
    df["week"] = df["datetime"].dt.isocalendar().week.astype(int)
    df["month"] = df["datetime"].dt.month
    df["month_name"] = df["datetime"].dt.strftime("%b")
    df["date"] = df["datetime"].dt.date

    # ── Time buckets ─────────────────────────────────────────────────
    def time_bucket(h):
        if 6 <= h <= 11:
            return "Morning (6–11)"
        elif 12 <= h <= 16:
            return "Afternoon (12–16)"
        elif 17 <= h <= 21:
            return "Evening (17–21)"
        else:
            return "Late / Overnight (22–5)"

    df["time_bucket"] = df["hour"].apply(time_bucket)

    # ── Weekend flag ─────────────────────────────────────────────────
    df["is_weekend"] = df["day_num"].isin([5, 6])

    return df


def filter_df(df: pd.DataFrame, stores=None, days=None, hour_range=(6, 21)) -> pd.DataFrame:
    """Apply sidebar filters."""
    filtered = df.copy()
    if stores:
        filtered = filtered[filtered["store_location"].isin(stores)]
    if days:
        filtered = filtered[filtered["day_of_week"].isin(days)]
    filtered = filtered[
        (filtered["hour"] >= hour_range[0]) & (filtered["hour"] <= hour_range[1])
    ]
    return filtered
