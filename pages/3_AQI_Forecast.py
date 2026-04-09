import streamlit as st
import pandas as pd
import numpy as np
import smtplib
from email.message import EmailMessage
from datetime import datetime
import os
from dotenv import load_dotenv
import pymysql
import plotly.graph_objects as go

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

# --------------- LOAD ENV ----------------
load_dotenv()

# ------------------ DB -------------------------

def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=3306
    )

# ------------------- LOAD MODEL --------------------

from model_loader import load_aqi_model
model, scaler = load_aqi_model()

# ----------------- PAGE CONFIG ---------------------

st.set_page_config(page_title="AQI Monitoring", layout="wide")
st.title("☢️ Smart AQI Monitoring System")

# -------------------- LOCATION ---------------------

CITY_DATA = {
    "Delhi": {"Connaught Place": ["Inner Circle"]},
    "Bangalore": {"Whitefield": ["ITPL"]},
    "Chennai": {"Guindy": ["Kathipara Junction"]},
    "Mumbai": {"Andheri": ["Link Road"]},
    "Hyderabad": {"Hitech City": ["Cyber Towers"]}
}
# ------------------- CITY AQI FACTOR -------------------

CITY_FACTOR = {
    "Delhi": 1.4,
    "Mumbai": 1.2,
    "Chennai": 0.9,
    "Bangalore": 0.8,
    "Hyderabad": 1.0
}
col1, col2 = st.columns(2)

with col1:
    city = st.selectbox("🏙️ City", list(CITY_DATA.keys()))
    area = st.selectbox("📍 Area", list(CITY_DATA[city].keys()))
    landmark = st.selectbox("📌 Landmark", CITY_DATA[city][area])

location = f"{city} - {area} - {landmark}"
st.success(f"📍 Selected Location: {location}")

# -------------------- AQI LEVEL ----------------

def aqi_level(aqi):
    if aqi <= 50:
        return "GOOD 🟢"
    elif aqi <= 100:
        return "MODERATE 🟡"
    elif aqi <= 200:
        return "UNHEALTHY 🟠"
    else:
        return "HAZARDOUS 🔴"

# ----------------------------- EMAIL ----------------------------------

def send_email_alert(subject, body):
    try:
        msg = EmailMessage()
        msg["From"] = os.getenv("EMAIL_USER")
        msg["To"] = os.getenv("EMAIL_RECEIVER")
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASSWORD"))
            server.send_message(msg)

        return True
    except Exception as e:
        print("Email error:", e)
        return False

# ------------------------ SESSION ------------------------

if "aqi_email_sent" not in st.session_state:
    st.session_state.aqi_email_sent = False

# ------------------------------ INSERT -------------------------

def insert_aqi(location, current_aqi, predicted_aqi):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO aqi_data 
            (timestamp, city, aqi_value, prediction)
            VALUES (NOW(), %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            location,
            int(current_aqi),
            int(predicted_aqi),
        ))

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print("DB error:", e)

# ------------------------DATASET UPLOAD ------------------------

# ------------------------ LOAD DATA (AUTO) ------------------------

@st.cache_data
def load_aqi_data():
    return pd.read_csv("C:/Users/harip/Downloads/GUVI DS/air_data.csv")   

df = load_aqi_data()

st.success("✅ Using preloaded AQI dataset")

feature_cols = [
    'pm2.5','pm10','no2','so2','co','ozone','aerosol_optical_depth'
]

target_col = "aqi_value"

# ---------------------------- VALIDATION -------------------------

missing = [c for c in feature_cols if c not in df.columns]
if missing:
        st.error(f"Missing columns: {missing}")
        st.stop()

if len(df) < 10:
        st.error("Need at least 10 rows")
        st.stop()

# ---------------------------- PREDICT ---------------------------

if st.button("🚀 Predict AQI"):

        X = df[feature_cols].values
        X_scaled = scaler.transform(X)

        TIMESTEPS = 10
        X_seq = []

        for i in range(TIMESTEPS, len(X_scaled)):
            X_seq.append(X_scaled[i-TIMESTEPS:i])

        X_seq = np.array(X_seq)

        predictions = model.predict(X_seq).flatten()
        next_aqi = predictions[-1]

        # 🎯 City-based scaling
        factor = CITY_FACTOR[city]
        CITY_NOISE = {
            "Delhi": 15,
            "Mumbai": 10,
            "Chennai": 5,
            "Bangalore": 3,
            "Hyderabad": 8
        }
        noise = np.random.uniform(-CITY_NOISE[city], CITY_NOISE[city])

        # Adjust values
        adjusted_predicted = (next_aqi * factor) + noise
        adjusted_current = (df[target_col].iloc[-1] * factor) + noise

        current_aqi = int(adjusted_current)
        predicted_aqi = int(adjusted_predicted)

        # ----------------------- DISPLAY -----------------

        st.subheader("☢️ AQI Results")

        c1, c2 = st.columns(2)

        c1.metric("🌍 Current AQI", current_aqi)
        c2.metric("🔮 Predicted AQI", predicted_aqi)

        st.write("📊 AQI Level:", aqi_level(predicted_aqi))
        
        # ------------------------- SAVE -----------------------------

        insert_aqi(location, current_aqi, predicted_aqi)

        # --------------------- ALERT -----------------------------

        if predicted_aqi > 200:
            st.error("🚨 Hazardous Air Quality")

            if not st.session_state.aqi_email_sent:

                email_body = f"""
☢️ AQI ALERT

📍 Location: {location}
AQI: {predicted_aqi}


⚠ Health Risk:
Avoid outdoor exposure

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

                if send_email_alert("🚨 AQI Alert", email_body):
                    st.success("📧 Alert sent!")
                    st.session_state.aqi_email_sent = True
                else:
                    st.error("Email failed")

        # ----------------- GRAPH ----------------------------
        st.subheader("📈 AQI Trend")

        recent = df[target_col].values[-20:]
        x = list(range(len(recent)))

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=x, y=recent,
            mode='lines+markers',
            name='Recent AQI'
        ))

        fig.add_trace(go.Scatter(
            x=[len(recent)],
            y=[predicted_aqi],
            mode='markers',
            name='Prediction',
            marker=dict(size=12, symbol='star')
        ))

        fig.update_layout(
            title="AQI Forecast",
            xaxis_title="Time",
            yaxis_title="AQI"
        )

        st.plotly_chart(fig, use_container_width=True)

# ----------------------- RESET -----------------------

if st.button("🔄 Reset AQI Alert"):
    st.session_state.aqi_email_sent = False
    st.info("Alert reset")