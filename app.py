import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Job Market Intelligence",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 1rem;
}

.hero {
    padding: 25px 30px;
    border-radius: 18px;
    background: linear-gradient(135deg, #111827, #2563eb);
    color: white;
    margin-bottom: 20px;
}

.hero h1 {
    font-size: 38px;
    margin-bottom: 5px;
}

.hero p {
    font-size: 17px;
    margin: 0;
    opacity: 0.9;
}

.kpi {
    background: white;
    padding: 18px;
    border-radius: 15px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 3px 12px rgba(0,0,0,0.07);
}

.kpi-title {
    font-size: 13px;
    color: #64748b;
}

.kpi-value {
    font-size: 28px;
    font-weight: 700;
    color: #111827;
}

.nav-title {
    font-size: 18px;
    font-weight: 700;
    margin-top: 10px;
    margin-bottom: 10px;
}

.insight {
    padding: 18px;
    border-radius: 14px;
    background: #f8fafc;
    border-left: 5px solid #2563eb;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():

    data = pd.read_csv("jobs.csv")

    data["title"] = data["title"].fillna("").astype(str)

    data["country"] = (
        data["country"]
        .fillna("Unknown")
        .astype(str)
    )

    data["published_date"] = pd.to_datetime(
        data["published_date"],
        errors="coerce"
    )

    data["hourly_low"] = pd.to_numeric(
        data["hourly_low"],
        errors="coerce"
    )

    data["hourly_high"] = pd.to_numeric(
        data["hourly_high"],
        errors="coerce"
    )

    data["average_hourly_rate"] = (
        data["hourly_low"] +
        data["hourly_high"]
    ) / 2

    return data


df = load_data()

# =========================================================
# PAGE NAMES
# =========================================================

pages = [
    "🏠 Executive Dashboard",
    "📊 Market Overview",
    "💼 Job Titles",
    "🌍 Countries",
    "📈 Monthly Trends"
]

# =========================================================
# SESSION STATE
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = pages[0]

# =========================================================
# SIDEBAR - VERTICAL NAVIGATION
# =========================================================

st.sidebar.markdown(
    "<h1 style='text-align:center;'>💼</h1>",
    unsafe_allow_html=True
)

st.sidebar.title("Job Market AI")

st.sidebar.markdown("---")

st.sidebar.markdown(
    "### 🧭 Navigation"
)

for i, p in enumerate(pages):

    if st.sidebar.button(
        p,
        key=f"side_{i}",
        use_container_width=True
    ):
        st.session_state.page = p
        st.rerun()

st.sidebar.markdown("---")

# =========================================================
# SIDEBAR FILTER
# =========================================================

st.sidebar.markdown("### 🔎 Filters")

countries = sorted(
    df["country"]
    .dropna()
    .unique()
    .tolist()
)

selected_country = st.sidebar.selectbox(
    "Select Country",
    ["All Countries"] + countries
)

filtered_df = df.copy()

if selected_country != "All Countries":

    filtered_df = filtered_df[
        filtered_df["country"] == selected_country
    ]

# =========================================================
# HORIZONTAL NAVIGATION
# =========================================================

st.markdown(
    '<div class="nav-title">⚡ Quick Navigation</div>',
    unsafe_allow_html=True
)

nav_items = [
    ("🏠", "Home", pages[0]),
    ("📊", "Market", pages[1]),
    ("💼", "Jobs", pages[2]),
    ("🌍", "Countries", pages[3]),
    ("📈", "Trends", pages[4])
]

nav_cols = st.columns(5)

for i, (icon, label, page_name) in enumerate(nav_items):

    with nav_cols[i]:

        if st.button(
            f"{icon}  {label}",
            key=f"top_{i}",
            use_container_width=True
        ):
            st.session_state.page = page_name
            st.rerun()

st.divider()

# =========================================================
# HERO HEADER
# =========================================================

st.markdown("""
<div class="hero">

<h1>💼 Job Market Intelligence</h1>

<p>
Interactive analytics dashboard for job market trends,
salary insights and employment patterns
</p>

</div>
""", unsafe_allow_html=True)

# =========================================================
# EXECUTIVE DASHBOARD
# =========================================================

if st.session_state.page == "🏠 Executive Dashboard":

    st.subheader("📌 Executive Overview")

    # ---------------- KPI ----------------

    total_jobs = len(filtered_df)

    total_countries = filtered_df[
        "country"
    ].nunique()

    unique_titles = filtered_df[
        "title"
    ].nunique()

    hourly_jobs = int(
        filtered_df["is_hourly"]
        .fillna(False)
        .sum()
    )

    avg_rate = filtered_df[
        "average_hourly_rate"
    ].mean()

    rate_text = (
        f"${avg_rate:,.2f}"
        if not np.isnan(avg_rate)
        else "N/A"
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    kpis = [
        ("TOTAL JOB POSTINGS", f"{total_jobs:,}"),
        ("COUNTRIES", f"{total_countries}"),
        ("UNIQUE JOB TITLES", f"{unique_titles:,}"),
        ("HOURLY JOBS", f"{hourly_jobs:,}"),
        ("AVG HOURLY RATE", rate_text)
    ]

    for col, (title, value) in zip(
        [c1, c2, c3, c4, c5],
        kpis
    ):

        with col:

            st.markdown(
                f"""
                <div class="kpi">

                <div class="kpi-title">
                {title}
                </div>

                <div class="kpi-value">
                {value}
                </div>

                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("")

    # =====================================================
    # MONTHLY TREND
    # =====================================================

    monthly_jobs = (
        filtered_df
        .dropna(subset=["published_date"])
        .groupby(
            filtered_df["published_date"]
            .dt.to_period("M")
            .astype(str)
        )
        .size()
        .reset_index(name="Job_Postings")
    )

    monthly_jobs.columns = [
        "Month",
        "Job_Postings"
    ]

    if len(monthly_jobs) > 0:

        fig_month = px.area(
            monthly_jobs,
            x="Month",
            y="Job_Postings",
            markers=True,
            title="📈 Monthly Job Posting Trend"
        )

        fig_month.update_layout(
            height=400,
            hovermode="x unified"
        )

        st.plotly_chart(
            fig_month,
            use_container_width=True
        )

    # =====================================================
    # TWO COLUMN CHARTS
    # =====================================================

    left, right = st.columns(2)

    # ---------------- COUNTRIES ----------------

    with left:

        country_counts = (
            filtered_df["country"]
            .value_counts()
            .head(10)
            .reset_index()
        )

        country_counts.columns = [
            "Country",
            "Jobs"
        ]

        fig_country = px.bar(
            country_counts,
            x="Jobs",
            y="Country",
            orientation="h",
            title="🌍 Top Hiring Countries"
        )

        fig_country.update_layout(
            height=420
        )

        st.plotly_chart(
            fig_country,
            use_container_width=True
        )

    # ---------------- JOB TITLES ----------------

    with right:

        top_titles = (
            filtered_df["title"]
            .value_counts()
            .head(10)
            .reset_index()
        )

        top_titles.columns = [
            "Job Title",
            "Postings"
        ]

        fig_titles = px.bar(
            top_titles,
            x="Postings",
            y="Job Title",
            orientation="h",
            title="💼 Most Posted Job Titles"
        )

        fig_titles.update_layout(
            height=420
        )

        st.plotly_chart(
            fig_titles,
            use_container_width=True
        )

    # =====================================================
    # QUICK INSIGHT
    # =====================================================

    st.subheader("💡 Quick Market Insight")

    if len(filtered_df) > 0:

        top_country = (
            filtered_df["country"]
            .value_counts()
            .idxmax()
        )

        top_job = (
            filtered_df["title"]
            .value_counts()
            .idxmax()
        )

        st.markdown(
            f"""
            <div class="insight">

            🌍 <b>Top Hiring Country:</b>
            {top_country}

            <br><br>

            💼 <b>Most Frequently Posted Job:</b>
            {top_job}

            <br><br>

            📊 <b>Total Opportunities:</b>
            {len(filtered_df):,}

            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# MARKET OVERVIEW
# =========================================================

elif st.session_state.page == "📊 Market Overview":

    st.header("📊 Market Overview")

    st.write(
        "Explore the overall distribution of job opportunities."
    )

    country_counts = (
        filtered_df["country"]
        .value_counts()
        .head(20)
        .reset_index()
    )

    country_counts.columns = [
        "Country",
        "Jobs"
    ]

    fig = px.bar(
        country_counts,
        x="Jobs",
        y="Country",
        orientation="h",
        title="Top 20 Countries by Job Postings"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# JOB TITLES
# =========================================================

elif st.session_state.page == "💼 Job Titles":

    st.header("💼 Job Title Analysis")

    top_titles = (
        filtered_df["title"]
        .value_counts()
        .head(20)
        .reset_index()
    )

    top_titles.columns = [
        "Job Title",
        "Postings"
    ]

    fig = px.bar(
        top_titles,
        x="Postings",
        y="Job Title",
        orientation="h",
        title="Top 20 Job Titles"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        top_titles,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# COUNTRIES
# =========================================================

elif st.session_state.page == "🌍 Countries":

    st.header("🌍 Country Analysis")

    country_counts = (
        filtered_df["country"]
        .value_counts()
        .head(20)
        .reset_index()
    )

    country_counts.columns = [
        "Country",
        "Job Postings"
    ]

    fig = px.bar(
        country_counts,
        x="Country",
        y="Job Postings",
        title="Job Opportunities by Country"
    )

    fig.update_layout(
        xaxis_tickangle=-45
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        country_counts,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# MONTHLY TRENDS
# =========================================================

elif st.session_state.page == "📈 Monthly Trends":

    st.header("📈 Job Market Trends Over Time")

    monthly_jobs = (
        filtered_df
        .dropna(subset=["published_date"])
        .groupby(
            filtered_df["published_date"]
            .dt.to_period("M")
            .astype(str)
        )
        .size()
        .reset_index(name="Job_Postings")
    )

    monthly_jobs.columns = [
        "Month",
        "Job_Postings"
    ]

    if len(monthly_jobs) > 0:

        fig = px.line(
            monthly_jobs,
            x="Month",
            y="Job_Postings",
            markers=True,
            title="Monthly Job Posting Trend"
        )

        fig.update_layout(
            height=500,
            hovermode="x unified"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.dataframe(
            monthly_jobs,
            use_container_width=True,
            hide_index=True
        )

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "💼 Job Market Analysis & Recommendation System | "
    "Python • Pandas • Plotly • Streamlit"
)