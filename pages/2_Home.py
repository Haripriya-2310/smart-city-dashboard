import streamlit as st
import pandas as pd
import pymysql
from dotenv import load_dotenv
import os
import plotly.express as px


st.markdown("""
<style>

/* Main background */
.stApp {
    background-color: #F5F7FA;
    color: #1C1E21;
}

/* Headings */
h1, h2, h3 {
    color: #2E7DFF;
    font-weight: 700;
}

/* Buttons */
.stButton>button {
    background-color: #2E7DFF;
    color: white;
    border-radius: 8px;
    height: 3em;
    width: 100%;
    font-size: 16px;
    border: none;
}

.stButton>button:hover {
    background-color: #1b5ed6;
}

/* Cards / Metrics */
[data-testid="metric-container"] {
    background-color: white;
    border: 1px solid #E0E0E0;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.05);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #FFFFFF;
}

/* Slider */
.stSlider > div {
    color: #2E7DFF;
}

/* Alerts */
.stAlert {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# -----------SAFE DB FETCH FUNCTION-------------

def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=3306
    )

load_dotenv()

# ------------ PAGE CONFIG ---------------------

st.set_page_config(
    page_title="UrbanBot Intelligence – Smart City Analytics Platform",
    layout="wide"
)

st.title("🧠🌇 Smart City Analytics Platform")
st.caption("AI-powered insights for traffic, air quality, and urban safety monitoring")
st.divider()

# ----------------------FETCH DATA FUNCTIONS --------------

def fetch_table(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ------------------QUERIES-----------------

traffic_df = fetch_table("SELECT * FROM traffic_events;")
crowd_df = fetch_table("SELECT * FROM crowd_metrics;")
road_df = fetch_table("SELECT * FROM road_detections;")
complaint_df = fetch_table("SELECT * FROM nlp_complaints;")
aqi_df = fetch_table("SELECT * FROM aqi_data ORDER BY timestamp DESC;")

# ------------------ KPI SECTION ---------------

st.subheader("📊 Key Metrics")
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

kpi1.metric("🚦 Total Accidents", len(traffic_df))

latest_aqi = aqi_df.iloc[0]['aqi_value']
kpi2.metric("☢️ Current AQI", latest_aqi)

kpi3.metric("👥 Crowd Alerts", len(crowd_df))
kpi4.metric("🧾 Total Complaints", len(complaint_df))
kpi5.metric("🚧 Road Issues", len(road_df))

st.divider()

# ------------------- PRIORITY ISSUES --------------------

st.subheader("🚨 Priority Issues")

# -------- Traffic --------
severe_traffic = traffic_df[traffic_df['detected_object'].isin(['HIGH', 'SEVERE'])]

if not severe_traffic.empty:
    st.warning(f"🚦 Traffic congestion detected in {len(severe_traffic)} locations")

# -------- Road Issues --------
high_severity = road_df[road_df['severity_level'].isin(['HIGH', 'CRITICAL'])]

if not high_severity.empty:
    st.error(f"🚧 {len(high_severity)} road issues require immediate attention")

# -------- Crowd --------
extreme_crowd = crowd_df[crowd_df['density_level'] == 'HIGH']

if not extreme_crowd.empty:
    st.warning(f"👥 High crowd density detected at {len(extreme_crowd)} locations")

# -------- AQI --------
critical_aqi = aqi_df[aqi_df['aqi_value'] > 200]

if not critical_aqi.empty:
    st.error(f"☢️ Poor air quality detected in {len(critical_aqi)} areas")

# -------- Complaints --------
recent_complaints = complaint_df[
    complaint_df['created_at'] >= pd.Timestamp.now() - pd.Timedelta(days=1)
]

if len(recent_complaints) > 50:
    st.info(f"🧾 High complaint volume today: {len(recent_complaints)} cases")

# -------- If Everything is Fine --------
if (
    severe_traffic.empty and
    high_severity.empty and
    extreme_crowd.empty and
    critical_aqi.empty and
    len(recent_complaints) <= 50
):
    st.success("✅ No major issues detected. City operations are stable.")

st.divider()

# ------------------ MINI TREND SNAPSHOTS ---------------------

st.subheader("📈 Trends Snapshot")

# ---------- ROW 1 (3 charts) ----------
col1, col2, col3 = st.columns(3)

# 🚦 Accidents Trend
acc_trend = traffic_df['timestamp'].value_counts().sort_index()
fig1 = px.line(
    x=acc_trend.index,
    y=acc_trend.values,
    title="🚦 Accidents Trend Over Time",
    labels={'x': 'Time', 'y': 'Accidents'}
)
col1.plotly_chart(fig1, use_container_width=True)

# ☢️ AQI Trend
aqi_trend = aqi_df.groupby('timestamp')['aqi_value'].mean().reset_index()
fig2 = px.line(
    aqi_trend,
    x='timestamp',
    y='aqi_value',
    title="☢️ AQI Trend",
)
col2.plotly_chart(fig2, use_container_width=True)

# 👥 Crowd Density
crowd_trend = crowd_df['density_level'].value_counts().reset_index()
crowd_trend.columns = ['density_level', 'count']

fig3 = px.bar(
    crowd_trend,
    x='density_level',
    y='count',
    color='density_level',
    title="👥 Crowd Density Distribution"
)
col3.plotly_chart(fig3, use_container_width=True)

# ---------- ROW 2 (2 charts) ----------
col4, col5 = st.columns(2)

# 🧾 Complaints
complaint_trend = complaint_df['category'].value_counts().reset_index()
complaint_trend.columns = ['category', 'count']

fig4 = px.bar(
    complaint_trend,
    x='category',
    y='count',
    color='category',
    title="🧾 Complaints by Category"
)
col4.plotly_chart(fig4, use_container_width=True)

# Road Issues
road_freq = road_df['detection_type'].value_counts().reset_index()
road_freq.columns = ['issue', 'count']

fig5 = px.bar(
    road_freq,
    x='issue',
    y='count',
    color='issue',
    title="🚧 Road Issues Distribution"
)
col5.plotly_chart(fig5, use_container_width=True)