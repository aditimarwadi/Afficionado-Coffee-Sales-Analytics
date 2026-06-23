"""
utils/charts.py
Reusable Plotly chart functions for every dashboard page.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Brand palette ────────────────────────────────────────────────────────────
CREAM     = "#F5F0E8"
ESPRESSO  = "#2C1810"
CARAMEL   = "#C4873A"
SAGE      = "#7A9E7E"
DUSTY     = "#8B7D6B"
ACCENT    = "#E8A838"
STORE_COLORS = {"Hell's Kitchen": "#C4873A", "Astoria": "#7A9E7E", "Lower Manhattan": "#8B7D6B"}

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Georgia, serif", color="#2C1810"),
    margin=dict(l=20, r=20, t=50, b=20),
)

DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


# ── 1. Daily revenue trend ───────────────────────────────────────────────────
def daily_trend_chart(df: pd.DataFrame, metric: str = "revenue") -> go.Figure:
    daily = df.groupby("date")[metric].sum().reset_index()
    daily["rolling_7"] = daily[metric].rolling(7, center=True).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily["date"], y=daily[metric],
        mode="lines", name="Daily",
        line=dict(color=CARAMEL, width=1.2),
        opacity=0.45
    ))
    fig.add_trace(go.Scatter(
        x=daily["date"], y=daily["rolling_7"],
        mode="lines", name="7-day avg",
        line=dict(color=ESPRESSO, width=2.5)
    ))
    label = "Revenue ($)" if metric == "revenue" else "Transactions"
    fig.update_layout(
        **CHART_LAYOUT,
        title=f"Daily {label} — 2025",
        xaxis_title="Date",
        yaxis_title=label,
        legend=dict(orientation="h", y=1.05),
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="#EDE8E0"),
    )
    return fig


# ── 2. Weekly aggregation bar ────────────────────────────────────────────────
def weekly_bar_chart(df: pd.DataFrame, metric: str = "revenue") -> go.Figure:
#     weekly = df.groupby("week")[metric].sum().reset_index()
#     fig = px.bar(
#         weekly, x="week", y=metric,
#         color_discrete_sequence=[CARAMEL],
#         labels={"week": "Week of Year", metric: metric.title()}
#     )
#     fig.update_layout(**CHART_LAYOUT, title=f"Weekly {metric.title()} — 2025",
#                       xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#EDE8E0"))
#     return fig
 if metric == "revenue":
    weekly = df.groupby("week")["revenue"].sum().reset_index()
    y_col = "revenue"
    label = "Revenue ($)"

 else:
    weekly = df.groupby("week").size().reset_index(name="transactions")
    y_col = "transactions"
    label = "Transaction Count"

 fig = px.bar(
    weekly,
    x="week",
    y=y_col,
    color_discrete_sequence=[CARAMEL],
    labels={"week": "Week of Year", y_col: label}
)

 fig.update_layout(
    **CHART_LAYOUT,
    title=f"Weekly {label} - 2025",
    xaxis=dict(showgrid=False),
    yaxis=dict(gridcolor="#EDE8E0")
)

 return fig
   
    


# ── 3. Day-of-week performance ───────────────────────────────────────────────
def dow_bar_chart(df: pd.DataFrame, metric: str = "revenue") -> go.Figure:
    if metric == "revenue":
        dow = df.groupby("day_of_week")["revenue"].mean().reset_index()
        dow.columns = ["day_of_week", "value"]
        ylabel = "Avg Daily Revenue ($)"
    else:
        dow = df.groupby(["date", "day_of_week"]).size().reset_index(name="txns")
        dow = dow.groupby("day_of_week")["txns"].mean().reset_index()
        dow.columns = ["day_of_week", "value"]
        ylabel = "Avg Transactions / Day"

    dow["day_of_week"] = pd.Categorical(dow["day_of_week"], categories=DAY_ORDER, ordered=True)
    dow = dow.sort_values("day_of_week")
    dow["color"] = dow["day_of_week"].isin(["Saturday", "Sunday"]).map(
        {True: ACCENT, False: CARAMEL})

    fig = px.bar(dow, x="day_of_week", y="value",
                 color="color", color_discrete_map="identity",
                 labels={"day_of_week": "Day", "value": ylabel},
                 text=dow["value"].round(0).astype(int))
    fig.update_traces(textposition="outside")
    fig.update_layout(**CHART_LAYOUT, title=f"{ylabel} by Day of Week",
                      showlegend=False,
                      xaxis=dict(showgrid=False),
                      yaxis=dict(gridcolor="#EDE8E0"))
    return fig


# ── 4. Weekday vs Weekend comparison ─────────────────────────────────────────
def weekend_vs_weekday(df: pd.DataFrame) -> go.Figure:
    grp = df.groupby("is_weekend").agg(
        avg_revenue=("revenue", "mean"),
        avg_txns=("transaction_id", "count")
    ).reset_index()
    grp["label"] = grp["is_weekend"].map({True: "Weekend", False: "Weekday"})

    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=["Avg Revenue per Transaction", "Avg Transactions"])
    fig.add_trace(go.Bar(x=grp["label"], y=grp["avg_revenue"].round(2),
                         marker_color=[CARAMEL, ACCENT], showlegend=False), row=1, col=1)
    fig.add_trace(go.Bar(x=grp["label"], y=grp["avg_txns"],
                         marker_color=[CARAMEL, ACCENT], showlegend=False), row=1, col=2)
    fig.update_layout(**CHART_LAYOUT, title="Weekday vs Weekend Comparison")
    return fig


# ── 5. Hourly demand curve ───────────────────────────────────────────────────
def hourly_curve(df: pd.DataFrame, metric: str = "revenue") -> go.Figure:
    if metric == "revenue":
        hourly = df.groupby("hour")["revenue"].sum().reset_index()
        ylabel = "Total Revenue ($)"
    else:
        hourly = df.groupby("hour").size().reset_index(name="transactions")
        hourly.columns = ["hour", "revenue"]
        ylabel = "Transaction Count"

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hourly["hour"], y=hourly["revenue"],
        mode="lines+markers",
        fill="tozeroy",
        fillcolor=f"rgba(196,135,58,0.15)",
        line=dict(color=CARAMEL, width=3),
        marker=dict(size=7, color=ESPRESSO)
    ))
    fig.update_layout(
        **CHART_LAYOUT,
        title=f"Hourly {ylabel}",
        xaxis=dict(title="Hour of Day", tickmode="linear", dtick=1, showgrid=False),
        yaxis=dict(title=ylabel, gridcolor="#EDE8E0"),
    )
    return fig


# ── 6. Heatmap: Day × Hour ───────────────────────────────────────────────────
def heatmap_day_hour(df: pd.DataFrame, metric: str = "revenue") -> go.Figure:
    if metric == "revenue":
        pivot = df.groupby(["day_of_week", "hour"])["revenue"].sum().unstack(fill_value=0)
    else:
        pivot = df.groupby(["day_of_week", "hour"]).size().unstack(fill_value=0)

    pivot = pivot.reindex([d for d in DAY_ORDER if d in pivot.index])

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[f"{h:02d}:00" for h in pivot.columns],
        y=pivot.index.tolist(),
        colorscale=[[0, CREAM], [0.5, CARAMEL], [1, ESPRESSO]],
        showscale=True,
        colorbar=dict(title=metric.title())
    ))
    fig.update_layout(**CHART_LAYOUT, title="Day × Hour Heatmap",
                      xaxis_title="Hour", yaxis_title="")
    return fig


# ── 7. Store comparison — hourly line chart ──────────────────────────────────
def store_hourly_lines(df: pd.DataFrame, metric: str = "revenue") -> go.Figure:
    if metric == "revenue":
        grp = df.groupby(["store_location", "hour"])["revenue"].sum().reset_index()
        ylabel = "Total Revenue ($)"
    else:
        grp = df.groupby(["store_location", "hour"]).size().reset_index(name="count")
        grp.columns = ["store_location", "hour", "revenue"]
        ylabel = "Transaction Count"

    fig = go.Figure()
    for store, color in STORE_COLORS.items():
        sub = grp[grp["store_location"] == store]
        fig.add_trace(go.Scatter(
            x=sub["hour"], y=sub["revenue"],
            mode="lines+markers", name=store,
            line=dict(color=color, width=2.5),
            marker=dict(size=6)
        ))
    fig.update_layout(
        **CHART_LAYOUT,
        title=f"Hourly {ylabel} by Location",
        xaxis=dict(title="Hour of Day", tickmode="linear", dtick=1, showgrid=False),
        yaxis=dict(title=ylabel, gridcolor="#EDE8E0"),
        legend=dict(orientation="h", y=1.05)
    )
    return fig


# ── 8. Store heatmaps (subplots) ─────────────────────────────────────────────
def store_heatmaps(df: pd.DataFrame, metric: str = "revenue") -> go.Figure:
    stores = df["store_location"].unique()
    fig = make_subplots(rows=1, cols=len(stores),
                        subplot_titles=list(stores))

    for i, store in enumerate(stores, 1):
        sub = df[df["store_location"] == store]
        if metric == "revenue":
            pivot = sub.groupby(["day_of_week", "hour"])["revenue"].sum().unstack(fill_value=0)
        else:
            pivot = sub.groupby(["day_of_week", "hour"]).size().unstack(fill_value=0)

        pivot = pivot.reindex([d for d in DAY_ORDER if d in pivot.index])
        fig.add_trace(go.Heatmap(
            z=pivot.values,
            x=[f"{h:02d}:00" for h in pivot.columns],
            y=pivot.index.tolist(),
            colorscale=[[0, CREAM], [0.5, CARAMEL], [1, ESPRESSO]],
            showscale=(i == len(stores)),
        ), row=1, col=i)

    fig.update_layout(**CHART_LAYOUT, title="Per-Location Day × Hour Heatmaps", height=380)
    return fig


# ── 9. Time bucket donut ──────────────────────────────────────────────────────
def time_bucket_donut(df: pd.DataFrame, metric: str = "revenue") -> go.Figure:
    if metric == "revenue":
        grp = df.groupby("time_bucket")["revenue"].sum().reset_index()
        grp.columns = ["bucket", "value"]
    else:
        grp = df.groupby("time_bucket").size().reset_index(name="value")
        grp.columns = ["bucket", "value"]

    colors = [CARAMEL, ACCENT, SAGE, DUSTY]
    fig = go.Figure(go.Pie(
        labels=grp["bucket"], values=grp["value"],
        hole=0.5,
        marker_colors=colors,
        textinfo="label+percent",
        insidetextorientation="auto"
    ))
    fig.update_layout(**CHART_LAYOUT, title="Revenue Share by Time Bucket",
                      showlegend=False)
    return fig


# ── 10. Monthly trend ─────────────────────────────────────────────────────────
def monthly_trend(df: pd.DataFrame, metric: str = "revenue") -> go.Figure:
    month_order = ["Jan","Feb","Mar","Apr","May","Jun",
                   "Jul","Aug","Sep","Oct","Nov","Dec"]
    if metric == "revenue":
        grp = df.groupby(["month", "month_name"])["revenue"].sum().reset_index()
        grp.columns = ["month_num", "month_name", "value"]
        ylabel = "Total Revenue ($)"
    else:
        grp = df.groupby(["month", "month_name"]).size().reset_index(name="value")
        grp.columns = ["month_num", "month_name", "value"]
        ylabel = "Transaction Count"

    grp["month_name"] = pd.Categorical(grp["month_name"], categories=month_order, ordered=True)
    grp = grp.sort_values("month_name")

    fig = px.line(grp, x="month_name", y="value",
                  markers=True,
                  color_discrete_sequence=[CARAMEL],
                  labels={"month_name": "Month", "value": ylabel})
    fig.update_traces(line=dict(width=3), marker=dict(size=9, color=ESPRESSO))
    fig.update_layout(**CHART_LAYOUT, title=f"Monthly {ylabel}",
                      xaxis=dict(showgrid=False),
                      yaxis=dict(gridcolor="#EDE8E0"))
    return fig
