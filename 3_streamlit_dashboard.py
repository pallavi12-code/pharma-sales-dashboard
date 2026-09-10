"""Interactive dashboard for the project's synthetic pharmaceutical sales data."""

import streamlit as st
import pandas as pd
import plotly.express as px
from analytics import generate_pharma_data

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Synthetic Pharma Sales Analytics",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    .metric-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 16px 20px;
        border-left: 4px solid #0066cc;
    }
    .metric-value { font-size: 28px; font-weight: 700; color: #0066cc; }
    .metric-label { font-size: 13px; color: #6c757d; margin-top: 4px; }
    .insight-box {
        background: #e8f4f8;
        border-left: 4px solid #17a2b8;
        padding: 12px 16px;
        border-radius: 4px;
        font-size: 14px;
        color: #155d6e;
        margin: 8px 0 16px 0;
    }
    h1 { color: #003366 !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { border-radius: 6px 6px 0 0; }
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────

@st.cache_data
def load_data(seed: int = 42) -> pd.DataFrame:
    return generate_pharma_data(seed)

try:
    df = load_data()
except (TypeError, ValueError) as exc:
    st.error(f"Unable to generate dashboard data: {exc}")
    st.stop()

# ── Sidebar filters ───────────────────────────────────────────────────────────

st.sidebar.title("Filters")
st.sidebar.caption("Synthetic data demo")

years = sorted(df["year"].unique())
sel_years = st.sidebar.multiselect("Year", years, default=years)

regions = sorted(df["region"].unique())
sel_regions = st.sidebar.multiselect("Region", regions, default=regions)

categories = sorted(df["category"].unique())
sel_cats = st.sidebar.multiselect("Therapeutic Area", categories, default=categories)

channels = sorted(df["channel"].unique())
sel_channels = st.sidebar.multiselect("Channel", channels, default=channels)

st.sidebar.markdown("---")
st.sidebar.caption("Built with Python, SQL, and Streamlit. This dataset is simulated and is not real pharmaceutical market data.")

# ── Filter data ───────────────────────────────────────────────────────────────

mask = (
    df["year"].isin(sel_years) &
    df["region"].isin(sel_regions) &
    df["category"].isin(sel_cats) &
    df["channel"].isin(sel_channels)
)
fdf = df[mask].copy()

if fdf.empty:
    st.warning("No data for selected filters. Please adjust the sidebar.")
    st.stop()

# ── Header ────────────────────────────────────────────────────────────────────

st.title("💊 Synthetic Pharma Sales Analytics")
st.markdown("Interactive analysis of simulated pharmaceutical sales records. Results are for demonstration only.")
st.markdown("---")

# ── KPI cards ─────────────────────────────────────────────────────────────────

total_rev   = fdf["revenue"].sum() / 1e6
total_units = fdf["units_sold"].sum()
avg_margin  = fdf["gross_margin_pct"].mean()
total_mkt   = fdf["mkt_spend"].sum() / 1e6
roi         = total_rev / total_mkt if total_mkt > 0 else 0

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(f'<div class="metric-card"><div class="metric-value">₹{total_rev:.1f}M</div><div class="metric-label">Total Revenue</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{total_units:,.0f}</div><div class="metric-label">Units Sold</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{avg_margin:.1f}%</div><div class="metric-label">Avg Gross Margin</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-card"><div class="metric-value">₹{total_mkt:.1f}M</div><div class="metric-label">Marketing Spend</div></div>', unsafe_allow_html=True)
with c5:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{roi:.1f}x</div><div class="metric-label">Marketing ROI</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4 = st.tabs(["📈 Revenue Trends", "💊 Drug Performance", "🗺️ Regional View", "📊 Deep Dive"])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab1:
    st.subheader("Revenue Trends Over Time")
    st.markdown('<div class="insight-box">💡 <b>Dataset note:</b> The generator applies a Q4 seasonal multiplier; this pattern is synthetic and should not be interpreted as a market fact.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # Quarterly revenue trend
        trend = fdf.groupby(["year", "quarter"])["revenue"].sum().reset_index()
        trend["period"] = trend["year"].astype(str) + "-" + trend["quarter"]
        trend = trend.sort_values(["year", "quarter"])
        trend["revenue_M"] = trend["revenue"] / 1e6

        fig = px.line(trend, x="period", y="revenue_M",
                      markers=True, title="Quarterly Revenue (₹M)",
                      labels={"revenue_M": "Revenue (₹M)", "period": "Period"},
                      color_discrete_sequence=["#0066cc"])
        fig.update_layout(height=350, plot_bgcolor="white", paper_bgcolor="white")
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # YoY by category
        yoy = fdf.groupby(["year", "category"])["revenue"].sum().reset_index()
        yoy["revenue_M"] = yoy["revenue"] / 1e6

        fig2 = px.bar(yoy, x="year", y="revenue_M", color="category",
                      title="Revenue by Therapeutic Area per Year",
                      labels={"revenue_M": "Revenue (₹M)", "year": "Year"},
                      barmode="group",
                      color_discrete_sequence=px.colors.qualitative.Set2)
        fig2.update_layout(height=350, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig2, use_container_width=True)

    # Seasonality heatmap
    st.subheader("Seasonality Heatmap")
    heat = fdf.groupby(["year", "quarter"])["revenue"].sum().unstack("quarter") / 1e6
    fig3 = px.imshow(heat, text_auto=".1f", color_continuous_scale="Blues",
                     title="Revenue (₹M) by Year × Quarter",
                     labels={"color": "Revenue (₹M)"})
    fig3.update_layout(height=280)
    st.plotly_chart(fig3, use_container_width=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab2:
    st.subheader("Drug Portfolio Performance")
    st.markdown('<div class="insight-box">💡 <b>Interpretation:</b> Compare revenue and margin together when exploring the simulated portfolio.</div>', unsafe_allow_html=True)

    drug_perf = fdf.groupby(["drug_name", "category"]).agg(
        revenue_M=("revenue", lambda x: x.sum() / 1e6),
        gross_margin=("gross_margin_pct", "mean"),
        units_sold=("units_sold", "sum"),
        mkt_spend_M=("mkt_spend", lambda x: x.sum() / 1e6),
    ).reset_index()
    drug_perf["mkt_roi"] = drug_perf["revenue_M"] / drug_perf["mkt_spend_M"]

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(drug_perf.sort_values("revenue_M", ascending=True),
                     x="revenue_M", y="drug_name", color="category",
                     orientation="h", title="Total Revenue by Drug (₹M)",
                     labels={"revenue_M": "Revenue (₹M)", "drug_name": "Drug"},
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(height=380, plot_bgcolor="white", paper_bgcolor="white",
                          showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Bubble chart: Revenue vs Margin (size = units)
        fig2 = px.scatter(drug_perf, x="revenue_M", y="gross_margin",
                          size="units_sold", color="category", text="drug_name",
                          title="Revenue vs Margin (bubble = units sold)",
                          labels={"revenue_M": "Revenue (₹M)", "gross_margin": "Gross Margin %"},
                          color_discrete_sequence=px.colors.qualitative.Set2)
        fig2.update_traces(textposition="top center", textfont_size=10)
        fig2.update_layout(height=380, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig2, use_container_width=True)

    # Channel mix
    st.subheader("Channel Mix by Drug")
    ch_drug = fdf.groupby(["drug_name", "channel"])["revenue"].sum().reset_index()
    ch_drug["revenue_M"] = ch_drug["revenue"] / 1e6
    fig3 = px.bar(ch_drug, x="drug_name", y="revenue_M", color="channel",
                  barmode="stack", title="Revenue by Channel per Drug",
                  labels={"revenue_M": "Revenue (₹M)", "drug_name": "Drug"},
                  color_discrete_sequence=px.colors.qualitative.Pastel)
    fig3.update_layout(height=350, plot_bgcolor="white", paper_bgcolor="white", xaxis_tickangle=30)
    st.plotly_chart(fig3, use_container_width=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab3:
    st.subheader("Regional Performance")
    st.markdown("<div class='insight-box'>💡 <b>Interpretation:</b> Regional differences reflect the generator's configured multipliers, not observed market conditions.</div>", unsafe_allow_html=True)

    reg_perf = fdf.groupby("region").agg(
        revenue_M=("revenue", lambda x: x.sum() / 1e6),
        gross_margin=("gross_margin_pct", "mean"),
        units_sold=("units_sold", "sum"),
    ).reset_index()
    reg_perf["rev_share"] = (reg_perf["revenue_M"] / reg_perf["revenue_M"].sum() * 100).round(1)

    col1, col2 = st.columns(2)

    with col1:
        fig = px.pie(reg_perf, values="revenue_M", names="region",
                     title="Revenue Share by Region",
                     color_discrete_sequence=px.colors.qualitative.Set2,
                     hole=0.4)
        fig.update_layout(height=360)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.bar(reg_perf.sort_values("gross_margin", ascending=False),
                      x="region", y="gross_margin",
                      title="Gross Margin % by Region",
                      labels={"gross_margin": "Gross Margin %", "region": "Region"},
                      color="gross_margin", color_continuous_scale="Blues")
        fig2.update_layout(height=360, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig2, use_container_width=True)

    # Drug × Region heatmap
    st.subheader("Drug × Region Revenue Heatmap")
    heat2 = fdf.groupby(["drug_name", "region"])["revenue"].sum().unstack("region") / 1e6
    fig3 = px.imshow(heat2, text_auto=".1f", color_continuous_scale="Blues",
                     title="Revenue (₹M) by Drug × Region",
                     labels={"color": "Revenue (₹M)"})
    fig3.update_layout(height=360)
    st.plotly_chart(fig3, use_container_width=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab4:
    st.subheader("Deep Dive — Custom Analysis")

    analysis = st.selectbox("Choose analysis:", [
        "Year-over-year growth by drug",
        "Marketing ROI ranking",
        "New drug ramp-up (Immuflex)",
        "Top 10 drug × region segments",
    ])

    if analysis == "Year-over-year growth by drug":
        yoy = fdf.groupby(["drug_name", "year"])["revenue"].sum().reset_index()
        yoy["revenue_M"] = yoy["revenue"] / 1e6
        yoy = yoy.sort_values(["drug_name", "year"])
        yoy["prev"] = yoy.groupby("drug_name")["revenue_M"].shift(1)
        yoy["yoy_pct"] = ((yoy["revenue_M"] - yoy["prev"]) / yoy["prev"] * 100).round(1)
        yoy_clean = yoy.dropna(subset=["yoy_pct"])
        fig = px.bar(yoy_clean, x="drug_name", y="yoy_pct", color="year",
                     barmode="group", title="YoY Revenue Growth % by Drug",
                     labels={"yoy_pct": "YoY Growth %", "drug_name": "Drug"},
                     color_discrete_sequence=px.colors.qualitative.Set1)
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", xaxis_tickangle=30)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('<div class="insight-box">📝 Growth above 0% indicates an increase versus the previous simulated year.</div>', unsafe_allow_html=True)

    elif analysis == "Marketing ROI ranking":
        roi = fdf.groupby("drug_name").agg(
            revenue_M=("revenue", lambda x: x.sum() / 1e6),
            mkt_spend_M=("mkt_spend", lambda x: x.sum() / 1e6),
        ).reset_index()
        roi["roi"] = (roi["revenue_M"] / roi["mkt_spend_M"]).round(2)
        fig = px.bar(roi.sort_values("roi", ascending=False),
                     x="drug_name", y="roi",
                     title="Marketing ROI (Revenue ÷ Spend)",
                     labels={"roi": "Revenue per ₹ Spent", "drug_name": "Drug"},
                     color="roi", color_continuous_scale="Greens")
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", xaxis_tickangle=30)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('<div class="insight-box">📝 This is a descriptive revenue-to-spend ratio on synthetic data, not causal marketing ROI.</div>', unsafe_allow_html=True)

    elif analysis == "New drug ramp-up (Immuflex)":
        ramp = fdf[fdf["drug_name"] == "Immuflex"].groupby(["year", "quarter"])["revenue"].sum().reset_index()
        ramp["period"] = ramp["year"].astype(str) + "-" + ramp["quarter"]
        ramp["revenue_M"] = ramp["revenue"] / 1e6
        ramp = ramp.sort_values(["year", "quarter"])
        fig = px.area(ramp, x="period", y="revenue_M",
                      title="Immuflex — Launch Ramp-Up (launched 2021)",
                      labels={"revenue_M": "Revenue (₹M)", "period": "Period"},
                      color_discrete_sequence=["#0066cc"])
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", xaxis_tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('<div class="insight-box">📝 This view shows the simulated launch trajectory for Immuflex.</div>', unsafe_allow_html=True)

    elif analysis == "Top 10 drug × region segments":
        seg = fdf.groupby(["drug_name", "region"])["revenue"].sum().reset_index()
        seg["revenue_M"] = (seg["revenue"] / 1e6).round(2)
        seg = seg.sort_values("revenue_M", ascending=False).head(10)
        seg["segment"] = seg["drug_name"] + " / " + seg["region"]
        fig = px.bar(seg, x="revenue_M", y="segment", orientation="h",
                     title="Top 10 Drug × Region Revenue Segments",
                     labels={"revenue_M": "Revenue (₹M)", "segment": "Segment"},
                     color="revenue_M", color_continuous_scale="Blues")
        fig.update_layout(height=400, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('<div class="insight-box">📝 These are the highest-revenue segments in the filtered synthetic dataset.</div>', unsafe_allow_html=True)

    # Raw data explorer
    st.markdown("---")
    st.subheader("Raw Data Explorer")
    st.markdown("Inspect the underlying dataset — just like querying a database.")
    st.dataframe(
        fdf[["year", "quarter", "drug_name", "category", "region", "channel",
             "units_sold", "revenue", "gross_margin_pct", "mkt_spend"]].head(100),
        use_container_width=True
    )
    st.caption(f"Showing first 100 of {len(fdf):,} filtered rows")
