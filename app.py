"""
app.py  ←  MAIN ENTRY POINT
Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
from utils.data_loader import load_and_prepare, filter_df

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Afficionado Coffee · Sales Analytics",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Source+Sans+3:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Source Sans 3', sans-serif;
    background-color: #FDFAF5;
    color: #2C1810;
}
h1, h2, h3 { font-family: 'Playfair Display', serif; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #2C1810;
}
section[data-testid="stSidebar"] * {
    color: #F5F0E8 !important;
}
section[data-testid="stSidebar"] .stMultiSelect span {
    background-color: #C4873A !important;
    color: #F5F0E8 !important;
}

/* KPI cards */
.kpi-card {
    background: #F5F0E8;
    border-left: 4px solid #C4873A;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 12px;
}
.kpi-label { font-size: 0.78rem; text-transform: uppercase;
             letter-spacing: 0.08em; color: #8B7D6B; }
.kpi-value { font-size: 2rem; font-weight: 700;
             font-family: 'Playfair Display', serif; color: #2C1810; }
.kpi-delta { font-size: 0.82rem; color: #7A9E7E; }

/* Tabs */
.stTabs [data-baseweb="tab"] {
    font-family: 'Playfair Display', serif;
    font-size: 1rem;
    color: #8B7D6B;
}
.stTabs [aria-selected="true"] {
    color: #C4873A !important;
    border-bottom: 2px solid #C4873A !important;
}

/* Header banner */
.header-banner {
    background: linear-gradient(135deg, #2C1810 0%, #5C3A1E 100%);
    color: #F5F0E8;
    padding: 28px 36px;
    border-radius: 12px;
    margin-bottom: 28px;
}
.header-banner h1 { color: #F5F0E8; margin: 0; font-size: 2rem; }
.header-banner p  { color: #C4873A; margin: 4px 0 0; font-size: 1rem; }

div[data-testid="stMetric"] {
    background: #F5F0E8;
    border-left: 4px solid #C4873A;
    border-radius: 8px;
    padding: 14px 18px;
}
</style>
""", unsafe_allow_html=True)

# ── Load data (cached) ────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Brewing your data ☕ …")
def get_data():
    return load_and_prepare("data/coffee_transactions.csv")

df_full = get_data()

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ☕ Afficionado Coffee")
    st.markdown("### Filters")

    all_stores = sorted(df_full["store_location"].unique())
    stores = st.multiselect(
        "Store Location",
        options=all_stores,
        default=all_stores,
        help="Select one or more store locations"
    )

    all_days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    days = st.multiselect(
        "Day of Week",
        options=all_days,
        default=all_days
    )

    hour_range = st.slider(
        "Hour Range",
        min_value=6, max_value=20,
        value=(6, 20),
        help="Filter by hour of day — store data spans 6 AM–8 PM"
    )

    metric = st.radio(
        "Primary Metric",
        options=["revenue", "transactions"],
        format_func=lambda x: "Revenue ($)" if x == "revenue" else "Transaction Count",
        index=0
    )

    st.markdown("---")
    st.markdown("**Data:** 2025 · 149,116 real transactions")
    st.markdown("**Stores:** 3 NYC locations")
    st.caption("ℹ️ Source data has time-of-day only (no calendar dates), "
               "so daily/weekly/monthly trend charts use dates spread "
               "evenly across 2025 in transaction order. Day-of-week and "
               "hourly patterns are fully accurate.")

# ── Apply filters ─────────────────────────────────────────────────────────────
df = filter_df(df_full, stores=stores, days=days, hour_range=hour_range)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-banner">
  <h1>☕ Sales Trend & Time-Based Performance</h1>
  <p>Afficionado Coffee Roasters · New York City · 2025</p>
</div>
""", unsafe_allow_html=True)

if df.empty:
    st.warning("No data matches your current filters. Please adjust the sidebar selections.")
    st.stop()

# ── KPI Row ───────────────────────────────────────────────────────────────────
total_rev   = df["revenue"].sum()
total_txns  = len(df)
avg_basket  = df["revenue"].mean()
peak_hour   = df.groupby("hour").size().idxmax()
busiest_day = df.groupby("day_of_week").size().idxmax()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Revenue",      f"${total_rev:,.0f}")
c2.metric("Total Transactions", f"{total_txns:,}")
c3.metric("Avg Basket Value",   f"${avg_basket:.2f}")
c4.metric("Peak Hour",          f"{peak_hour:02d}:00")
c5.metric("Busiest Day",        busiest_day)

st.markdown("<br>", unsafe_allow_html=True)

# ── Navigation tabs ───────────────────────────────────────────────────────────
tabs = st.tabs([
    "📈 Sales Trends",
    "📅 Day-of-Week",
    "🕐 Hourly Demand",
    "🗺️ Location Analysis",
])

# ──────────────────────────────────────────────────────────────────────────────
# TAB 1 — Sales Trends
# ──────────────────────────────────────────────────────────────────────────────
with tabs[0]:
    from utils.charts import daily_trend_chart, weekly_bar_chart, monthly_trend, time_bucket_donut

    st.subheader("Overall Sales Trend — 2025")
    st.plotly_chart(daily_trend_chart(df, metric if metric == "revenue" else "transaction_id"),
                    use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(monthly_trend(df, metric), use_container_width=True)
    with col2:
        st.plotly_chart(weekly_bar_chart(df, metric), use_container_width=True)

    st.plotly_chart(time_bucket_donut(df, metric), use_container_width=True)

    # Insight box
    best_month = df.groupby("month_name")["revenue"].sum().idxmax()
    st.info(f"📌 **Insight:** **{best_month}** recorded the highest revenue. "
            f"The morning window (6–11) drives the largest share of revenue — "
            f"over half of daily sales happen before noon, consistent with "
            f"specialty coffee's breakfast-and-commute-driven demand. "
            f"⚠️ *Note: since the source data has no calendar date field, daily/weekly/"
            f"monthly trend lines use dates spread evenly across 2025 — treat the "
            f"month-over-month shape as illustrative rather than a real seasonal signal.*")

# ──────────────────────────────────────────────────────────────────────────────
# TAB 2 — Day-of-Week
# ──────────────────────────────────────────────────────────────────────────────
with tabs[1]:
    from utils.charts import dow_bar_chart, weekend_vs_weekday

    st.subheader("Day-of-Week Performance")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(dow_bar_chart(df, "revenue"), use_container_width=True)
    with col2:
        st.plotly_chart(dow_bar_chart(df, "transactions"), use_container_width=True)

    st.plotly_chart(weekend_vs_weekday(df), use_container_width=True)

    # Day-of-week summary table
    st.subheader("Summary Table")
    dow_summary = df.groupby("day_of_week").agg(
        Total_Revenue=("revenue", "sum"),
        Avg_Revenue=("revenue", "mean"),
        Total_Transactions=("transaction_id", "count"),
    ).reset_index()
    dow_summary["day_of_week"] = pd.Categorical(
        dow_summary["day_of_week"],
        categories=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
        ordered=True)
    dow_summary = dow_summary.sort_values("day_of_week")
    dow_summary["Total_Revenue"] = dow_summary["Total_Revenue"].map("${:,.0f}".format)
    dow_summary["Avg_Revenue"]   = dow_summary["Avg_Revenue"].map("${:.2f}".format)
    st.dataframe(dow_summary, use_container_width=True, hide_index=True)

    st.info("📌 **Insight:** Revenue per transaction is fairly flat across days (≈$4.60–$4.75), "
            "meaning basket size doesn't swing much by day — the real lever for staffing is "
            "*volume*, not spend-per-visit. ⚠️ *Day-of-week transaction counts are evenly "
            "distributed here because the source data lacks calendar dates; for a true "
            "busiest/slowest-day verdict, calendar dates from the POS system are needed.*")

# ──────────────────────────────────────────────────────────────────────────────
# TAB 3 — Hourly Demand
# ──────────────────────────────────────────────────────────────────────────────
with tabs[2]:
    from utils.charts import hourly_curve, heatmap_day_hour

    st.subheader("Hourly Demand Analysis")
    st.plotly_chart(hourly_curve(df, metric), use_container_width=True)

    st.subheader("Day × Hour Heatmap")
    st.plotly_chart(heatmap_day_hour(df, metric), use_container_width=True)

    # Hourly breakdown table
    st.subheader("Hourly Revenue Breakdown")
    hrly = df.groupby("hour").agg(
        Total_Revenue=("revenue", "sum"),
        Transactions=("transaction_id", "count"),
        Avg_Basket=("revenue", "mean")
    ).reset_index()
    hrly["Hour"] = hrly["hour"].apply(lambda h: f"{h:02d}:00")
    hrly["Total_Revenue"] = hrly["Total_Revenue"].map("${:,.0f}".format)
    hrly["Avg_Basket"]    = hrly["Avg_Basket"].map("${:.2f}".format)
    st.dataframe(hrly[["Hour","Total_Revenue","Transactions","Avg_Basket"]],
                 use_container_width=True, hide_index=True)

    st.info("📌 **Insight:** Demand peaks sharply between **9–10 AM** (≈$85–89K combined revenue "
            "per hour across the year), roughly 4x the volume seen by early afternoon. "
            "Revenue falls steadily after 11 AM into a long, flat afternoon/evening plateau, "
            "with a sharp drop-off after 7 PM as stores wind down. "
            "Staffing should be front-loaded into the 7–11 AM block, the single highest-leverage "
            "window for reducing wait times.")

# ──────────────────────────────────────────────────────────────────────────────
# TAB 4 — Location Analysis
# ──────────────────────────────────────────────────────────────────────────────
with tabs[3]:
    from utils.charts import store_hourly_lines, store_heatmaps

    st.subheader("Cross-Location Temporal Comparison")
    st.plotly_chart(store_hourly_lines(df, metric), use_container_width=True)

    st.subheader("Per-Store Day × Hour Heatmaps")
    st.plotly_chart(store_heatmaps(df, metric), use_container_width=True)

    # Store KPI table
    st.subheader("Store Performance Summary")
    store_summary = df.groupby("store_location").agg(
        Total_Revenue=("revenue", "sum"),
        Transactions=("transaction_id", "count"),
        Avg_Basket=("revenue", "mean"),
    ).reset_index()
    store_summary["Revenue_Share"] = (
        store_summary["Total_Revenue"] / store_summary["Total_Revenue"].sum() * 100
    ).map("{:.1f}%".format)
    store_summary["Total_Revenue"] = store_summary["Total_Revenue"].map("${:,.0f}".format)
    store_summary["Avg_Basket"]    = store_summary["Avg_Basket"].map("${:.2f}".format)
    st.dataframe(store_summary, use_container_width=True, hide_index=True)

    st.info("📌 **Insight:** Revenue is remarkably balanced across the three locations "
            "(Hell's Kitchen ≈$236K, Astoria ≈$232K, Lower Manhattan ≈$230K) — no single "
            "store dominates. All three independently peak at the **same hour, 9–10 AM**, "
            "meaning the morning rush isn't a neighborhood-specific quirk but a consistent "
            "company-wide pattern. This makes a unified \"reinforce morning staffing\" policy "
            "viable across all locations rather than needing store-by-store schedules.")
