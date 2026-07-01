"""
Ransomware Monitoring Dashboard
Cyber Threat Intelligence dashboard for analysing ransomware attack data.
Built with Streamlit, Plotly, Pandas

This application does NOT generate simulated data.
Users must upload a CSV or XLSX dataset (or select one from the mounted /app/data folder).
"""

import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Ensure project root is on the Python path ─────────────────────────────────
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

from src.utils import (
    REQUIRED_COLUMNS,
    load_uploaded_file,
    load_file_from_path,
    scan_data_directory,
    validate_columns,
    clean_dataframe,
    compute_summary,
    search_ioc,
    filter_dataframe,
)

# ── Data directory (used for Docker volume mount) ─────────────────────────────
DATA_DIR = os.path.join(ROOT_DIR, "data")

# ── Plotly colour palette (cyber-themed) ───────────────────────────────────────
COLORS = [
    "#00d4ff", "#ff4d6d", "#9b5de5", "#fee440", "#00f5d4",
    "#f15bb5", "#00bbf9", "#fb5607", "#8338ec", "#3a86a7",
    "#06d6a0", "#ef476f",
]


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Ransomware Monitoring Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS for premium dark look ───────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Import Google Font ─────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── Global ──────────────────────────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #111827 50%, #0f172a 100%);
    }

    /* ── Sidebar ─────────────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1321 0%, #1a1f36 100%);
        border-right: 1px solid rgba(0,212,255,0.15);
    }

    /* ── KPI / Metric Cards ──────────────────────────────────────────── */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(15,23,42,0.9) 0%, rgba(30,41,59,0.8) 100%);
        border: 1px solid rgba(0,212,255,0.2);
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 4px 20px rgba(0,212,255,0.08);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,212,255,0.15);
    }
    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
        font-weight: 500;
        text-transform: uppercase;
        font-size: 0.72rem !important;
        letter-spacing: 0.08em;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #e2e8f0 !important;
        font-weight: 700;
        font-size: 1.6rem !important;
    }

    /* ── Section Headers ─────────────────────────────────────────────── */
    .section-header {
        font-size: 1.15rem;
        font-weight: 700;
        color: #e2e8f0;
        margin: 2rem 0 0.75rem 0;
        padding-bottom: 8px;
        border-bottom: 2px solid rgba(0,212,255,0.25);
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* ── Glass card wrapper ──────────────────────────────────────────── */
    .glass-card {
        background: rgba(15,23,42,0.65);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(100,116,139,0.18);
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 16px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.25);
    }

    /* ── Dataframe styling ───────────────────────────────────────────── */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }

    /* ── Title area ──────────────────────────────────────────────────── */
    .dashboard-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00d4ff, #9b5de5, #ff4d6d);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
        line-height: 1.2;
    }
    .dashboard-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        font-weight: 400;
        margin-top: 0;
    }

    /* ── Welcome card ────────────────────────────────────────────────── */
    .welcome-card {
        background: linear-gradient(135deg, rgba(15,23,42,0.85) 0%, rgba(30,41,59,0.7) 100%);
        border: 1px solid rgba(0,212,255,0.2);
        border-radius: 16px;
        padding: 40px 36px;
        margin: 30px auto;
        max-width: 820px;
        box-shadow: 0 8px 40px rgba(0,0,0,0.35);
    }
    .welcome-card h2 {
        color: #e2e8f0;
        margin-bottom: 12px;
    }
    .welcome-card p, .welcome-card li {
        color: #94a3b8;
        font-size: 0.95rem;
        line-height: 1.7;
    }
    .welcome-card code {
        background: rgba(0,212,255,0.1);
        color: #00d4ff;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.85rem;
    }

    /* ── IOC search input ────────────────────────────────────────────── */
    .stTextInput input {
        background: rgba(15,23,42,0.8) !important;
        border: 1px solid rgba(0,212,255,0.3) !important;
        color: #e2e8f0 !important;
        border-radius: 8px !important;
    }
    .stTextInput input:focus {
        border-color: #00d4ff !important;
        box-shadow: 0 0 0 2px rgba(0,212,255,0.2) !important;
    }

    /* ── Scrollbar ───────────────────────────────────────────────────── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0a0e1a; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }

    /* ── Divider override ────────────────────────────────────────────── */
    hr { border-color: rgba(100,116,139,0.2) !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ══════════════════════════════════════════════════════════════════════════════
#  HEADER (always visible)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<p class="dashboard-title">Ransomware Monitoring Dashboard</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="dashboard-subtitle">'
    "Cyber Threat Intelligence  ·  Upload your ransomware dataset to begin analysis"
    "</p>",
    unsafe_allow_html=True,
)
st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR — Data Source Selection
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## Dataset")

    source_option = st.radio(
        "Select data source",
        ["Upload dataset manually", "Use dataset from /app/data"],
        index=0,
        key="data_source_radio",
    )

    uploaded_file = None
    selected_data_file = None

    if source_option == "Upload dataset manually":
        uploaded_file = st.file_uploader(
            "Upload CSV or XLSX",
            type=["csv", "xlsx"],
            key="file_uploader",
        )
    else:
        available_files = scan_data_directory(DATA_DIR)
        if available_files:
            selected_data_file = st.selectbox(
                "Available datasets",
                available_files,
                key="data_folder_select",
            )
        else:
            st.info("No CSV/XLSX files found in the data folder.")

    st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
#  LOAD THE DATASET (or show welcome screen)
# ══════════════════════════════════════════════════════════════════════════════
df_raw = None
load_error = None

try:
    if source_option == "Upload dataset manually" and uploaded_file is not None:
        df_raw = load_uploaded_file(uploaded_file)
    elif source_option == "Use dataset from /app/data" and selected_data_file:
        full_path = os.path.join(DATA_DIR, selected_data_file)
        df_raw = load_file_from_path(full_path)
except Exception as exc:
    load_error = str(exc)


# ── If no data loaded yet, show welcome / instruction screen ───────────────────
if df_raw is None and load_error is None:
    st.markdown(
        """
        <div class="welcome-card">
            <h2>Welcome</h2>
            <p>
                Upload a <strong>CSV</strong> or <strong>XLSX</strong> ransomware dataset
                using the sidebar to start your analysis. This application does <em>not</em>
                use pre-generated, simulated, or Kaggle data &mdash; it only analyses the
                dataset <strong>you</strong> provide.
            </p>
            <p style="margin-top:18px;"><strong>Required columns:</strong></p>
            <ul>
                <li><code>date</code> &mdash; attack date</li>
                <li><code>ransomware_group</code> &mdash; name of the ransomware group</li>
                <li><code>country</code> &mdash; targeted country</li>
                <li><code>target_sector</code> &mdash; targeted sector</li>
                <li><code>attack_vector</code> &mdash; attack vector used</li>
                <li><code>technique</code> &mdash; MITRE ATT&amp;CK technique</li>
                <li><code>severity</code> &mdash; integer between 0 and 10</li>
                <li><code>ioc_ip</code> &mdash; indicator IP address</li>
                <li><code>ioc_hash</code> &mdash; indicator SHA-256 hash</li>
            </ul>
            <p style="margin-top:14px; color:#64748b; font-size:0.85rem;">
                Alternatively, select <em>"Use dataset from /app/data"</em> in the sidebar
                if a file has been placed in the mounted data volume (Docker).
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

if load_error:
    st.error(f"Failed to load the file: {load_error}")
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
#  VALIDATE COLUMNS
# ══════════════════════════════════════════════════════════════════════════════
missing = validate_columns(df_raw)
if missing:
    st.error(
        f"**The uploaded dataset is missing required columns:** `{'`, `'.join(missing)}`\n\n"
        "Please upload a file that contains all of the following columns:\n"
        + ", ".join(f"`{c}`" for c in REQUIRED_COLUMNS)
    )
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
#  CLEAN DATA
# ══════════════════════════════════════════════════════════════════════════════
df_clean, data_warnings = clean_dataframe(df_raw)

if data_warnings:
    with st.expander("Data cleaning warnings", expanded=False):
        for w in data_warnings:
            st.warning(w)

if df_clean.empty:
    st.error("No valid rows remain after data cleaning. Please check your dataset.")
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR — Filters (dynamic, based on uploaded data)
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## Filters")
    st.caption("Refine the dashboard view")

    st.markdown("---")

    # Date range
    min_date = df_clean["date"].min().date()
    max_date = df_clean["date"].max().date()
    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="filter_date_range",
    )

    st.markdown("")

    # Ransomware group
    all_groups = sorted(df_clean["ransomware_group"].unique())
    sel_groups = st.multiselect("Ransomware Group", all_groups, default=[], key="filter_groups")

    # Country
    all_countries = sorted(df_clean["country"].unique())
    sel_countries = st.multiselect("Country", all_countries, default=[], key="filter_countries")

    # Target sector
    all_sectors = sorted(df_clean["target_sector"].unique())
    sel_sectors = st.multiselect("Target Sector", all_sectors, default=[], key="filter_sectors")

    # Severity slider
    min_sev = int(df_clean["severity"].min())
    max_sev = int(df_clean["severity"].max())
    sev_range = st.slider(
        "Severity Range",
        min_value=0,
        max_value=10,
        value=(min_sev, max_sev),
        key="filter_severity",
    )

    st.markdown("---")
    st.caption("Ransomware Monitoring Dashboard v2.0")


# ── Apply filters ──────────────────────────────────────────────────────────────
df = filter_dataframe(
    df_clean,
    date_range=date_range if isinstance(date_range, tuple) and len(date_range) == 2 else None,
    groups=sel_groups or None,
    countries=sel_countries or None,
    sectors=sel_sectors or None,
    severity_range=sev_range,
)


# ══════════════════════════════════════════════════════════════════════════════
#  HELPER — shared Plotly layout
# ══════════════════════════════════════════════════════════════════════════════
_layout_defaults = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#cbd5e1"),
    margin=dict(l=40, r=20, t=40, b=40),
    legend=dict(
        bgcolor="rgba(15,23,42,0.6)",
        bordercolor="rgba(100,116,139,0.2)",
        borderwidth=1,
    ),
    xaxis=dict(gridcolor="rgba(100,116,139,0.12)", zeroline=False),
    yaxis=dict(gridcolor="rgba(100,116,139,0.12)", zeroline=False),
)


def apply_layout(fig, **overrides):
    """Apply the shared dark layout and any per-chart overrides."""
    merged = {**_layout_defaults, **overrides}
    fig.update_layout(**merged)
    return fig


# ══════════════════════════════════════════════════════════════════════════════
#  1 · OVERVIEW SUMMARY (KPI cards)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-header">Overview Summary</div>',
    unsafe_allow_html=True,
)

summary = compute_summary(df)
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Total Attacks", summary["total_attacks"])
c2.metric("Unique Groups", summary["unique_groups"])
c3.metric("Top Country", summary["top_country"])
c4.metric("Top Sector", summary["top_sector"])
c5.metric("Avg Severity", summary["avg_severity"])
c6.metric("Max Severity", summary["max_severity"])

st.markdown("")

if df.empty:
    st.info("No data matches the current filters. Adjust the sidebar filters.")
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
#  2 · RANSOMWARE GROUP DISTRIBUTION
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-header">Ransomware Group Distribution</div>',
    unsafe_allow_html=True,
)

col_grp1, col_grp2 = st.columns(2)

grp_counts = df["ransomware_group"].value_counts().reset_index()
grp_counts.columns = ["Ransomware Group", "Attacks"]

with col_grp1:
    fig_bar_grp = px.bar(
        grp_counts,
        x="Ransomware Group",
        y="Attacks",
        color="Ransomware Group",
        color_discrete_sequence=COLORS,
        title="Attacks by Ransomware Group",
    )
    apply_layout(fig_bar_grp)
    fig_bar_grp.update_traces(
        marker_line_width=0,
        opacity=0.92,
        hovertemplate="<b>%{x}</b><br>Attacks: %{y}<extra></extra>",
    )
    st.plotly_chart(fig_bar_grp, use_container_width=True, key="chart_bar_group")

with col_grp2:
    fig_pie_grp = px.pie(
        grp_counts,
        names="Ransomware Group",
        values="Attacks",
        color_discrete_sequence=COLORS,
        title="Group Share",
        hole=0.45,
    )
    apply_layout(fig_pie_grp)
    fig_pie_grp.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Attacks: %{value}<br>Share: %{percent}<extra></extra>",
    )
    st.plotly_chart(fig_pie_grp, use_container_width=True, key="chart_pie_group")


# ══════════════════════════════════════════════════════════════════════════════
#  3 · COUNTRY-BASED ATTACK DISTRIBUTION
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-header">Country-Based Attack Distribution</div>',
    unsafe_allow_html=True,
)

country_counts = df["country"].value_counts().reset_index()
country_counts.columns = ["Country", "Attacks"]

fig_country = px.bar(
    country_counts,
    x="Country",
    y="Attacks",
    color="Country",
    color_discrete_sequence=COLORS,
    title="Attacks by Country",
)
apply_layout(fig_country)
fig_country.update_traces(
    marker_line_width=0,
    opacity=0.92,
    hovertemplate="<b>%{x}</b><br>Attacks: %{y}<extra></extra>",
)
st.plotly_chart(fig_country, use_container_width=True, key="chart_bar_country")


# ══════════════════════════════════════════════════════════════════════════════
#  4 · SECTOR-BASED ATTACK DISTRIBUTION
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-header">Sector-Based Attack Distribution</div>',
    unsafe_allow_html=True,
)

sector_counts = df["target_sector"].value_counts().reset_index()
sector_counts.columns = ["Sector", "Attacks"]

col_sec1, col_sec2 = st.columns(2)

with col_sec1:
    fig_sec_bar = px.bar(
        sector_counts,
        x="Sector",
        y="Attacks",
        color="Sector",
        color_discrete_sequence=COLORS,
        title="Attacks by Sector",
    )
    apply_layout(fig_sec_bar)
    fig_sec_bar.update_traces(marker_line_width=0, opacity=0.92)
    st.plotly_chart(fig_sec_bar, use_container_width=True, key="chart_bar_sector")

with col_sec2:
    fig_sec_pie = px.pie(
        sector_counts,
        names="Sector",
        values="Attacks",
        color_discrete_sequence=COLORS,
        title="Sector Share",
        hole=0.45,
    )
    apply_layout(fig_sec_pie)
    fig_sec_pie.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig_sec_pie, use_container_width=True, key="chart_pie_sector")


# ══════════════════════════════════════════════════════════════════════════════
#  5 · TIME SERIES TREND
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-header">Attack Trend Over Time</div>',
    unsafe_allow_html=True,
)

df_ts = df.copy()
df_ts["month"] = df_ts["date"].dt.to_period("M").dt.to_timestamp()
monthly = df_ts.groupby("month").size().reset_index(name="Attacks")

fig_ts = px.area(
    monthly,
    x="month",
    y="Attacks",
    title="Monthly Ransomware Attacks",
    color_discrete_sequence=["#00d4ff"],
)
apply_layout(fig_ts)
fig_ts.update_traces(
    line=dict(width=2.5),
    fillcolor="rgba(0,212,255,0.12)",
    hovertemplate="<b>%{x|%B %Y}</b><br>Attacks: %{y}<extra></extra>",
)
fig_ts.update_xaxes(title_text="Month")
fig_ts.update_yaxes(title_text="Number of Attacks")
st.plotly_chart(fig_ts, use_container_width=True, key="chart_timeseries")


# ══════════════════════════════════════════════════════════════════════════════
#  6 · SEVERITY ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-header">Severity Analysis</div>',
    unsafe_allow_html=True,
)

col_sv1, col_sv2 = st.columns(2)

with col_sv1:
    avg_sev = (
        df.groupby("ransomware_group")["severity"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )
    avg_sev.columns = ["Ransomware Group", "Avg Severity"]
    avg_sev["Avg Severity"] = avg_sev["Avg Severity"].round(2)

    fig_sev_bar = px.bar(
        avg_sev,
        x="Ransomware Group",
        y="Avg Severity",
        color="Avg Severity",
        color_continuous_scale=["#00d4ff", "#9b5de5", "#ff4d6d"],
        title="Average Severity by Group",
    )
    apply_layout(fig_sev_bar)
    fig_sev_bar.update_traces(
        marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>Avg Severity: %{y:.2f}<extra></extra>",
    )
    st.plotly_chart(fig_sev_bar, use_container_width=True, key="chart_sev_avg")

with col_sv2:
    fig_sev_hist = px.histogram(
        df,
        x="severity",
        nbins=10,
        title="Severity Distribution",
        color_discrete_sequence=["#9b5de5"],
    )
    apply_layout(fig_sev_hist)
    fig_sev_hist.update_traces(
        marker_line_width=0,
        opacity=0.88,
        hovertemplate="Severity: %{x}<br>Count: %{y}<extra></extra>",
    )
    fig_sev_hist.update_xaxes(title_text="Severity Level", dtick=1)
    fig_sev_hist.update_yaxes(title_text="Count")
    st.plotly_chart(fig_sev_hist, use_container_width=True, key="chart_sev_dist")


# ══════════════════════════════════════════════════════════════════════════════
#  7 · MITRE ATT&CK TECHNIQUE BREAKDOWN
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-header">MITRE ATT&CK Technique Breakdown</div>',
    unsafe_allow_html=True,
)

tech_counts = df["technique"].value_counts().reset_index()
tech_counts.columns = ["Technique", "Count"]

fig_tech = px.bar(
    tech_counts,
    y="Technique",
    x="Count",
    orientation="h",
    color="Count",
    color_continuous_scale=["#0f172a", "#00d4ff"],
    title="Attacks by MITRE ATT&CK Technique",
)
apply_layout(fig_tech, height=400)
fig_tech.update_traces(marker_line_width=0)
fig_tech.update_yaxes(autorange="reversed")
st.plotly_chart(fig_tech, use_container_width=True, key="chart_technique")


# ══════════════════════════════════════════════════════════════════════════════
#  8 · ATTACK VECTOR ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-header">Attack Vector Analysis</div>',
    unsafe_allow_html=True,
)

vec_counts = df["attack_vector"].value_counts().reset_index()
vec_counts.columns = ["Attack Vector", "Count"]

fig_vec = px.bar(
    vec_counts,
    x="Attack Vector",
    y="Count",
    color="Attack Vector",
    color_discrete_sequence=COLORS,
    title="Attacks by Vector",
)
apply_layout(fig_vec)
fig_vec.update_traces(marker_line_width=0, opacity=0.92)
st.plotly_chart(fig_vec, use_container_width=True, key="chart_vector")


# ══════════════════════════════════════════════════════════════════════════════
#  9 · IOC SEARCH MODULE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown(
    '<div class="section-header">IOC Search Module</div>',
    unsafe_allow_html=True,
)
st.caption("Enter an IP address or SHA256 hash to search the uploaded dataset.")

ioc_query = st.text_input(
    "Search IOC (IP or Hash)",
    placeholder="e.g. 192.168.1.1 or a3f5c8...",
    key="ioc_input",
)

if ioc_query:
    # Search against cleaned (unfiltered) dataset
    results = search_ioc(df_clean, ioc_query)
    if results.empty:
        st.warning("No IOC record found.")
    else:
        st.success(f"{len(results)} matching record(s) found.")
        display_cols = [
            "date", "ransomware_group", "country", "target_sector",
            "attack_vector", "technique", "severity", "ioc_ip", "ioc_hash",
        ]
        st.dataframe(
            results[display_cols].reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; color:#475569; font-size:0.8rem; padding:12px 0;">
        Ransomware Monitoring Dashboard v2.0  ·  Built with Streamlit & Plotly  ·
        No simulated data  ·  Upload your own dataset
    </div>
    """,
    unsafe_allow_html=True,
)
