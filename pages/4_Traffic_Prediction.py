import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import smtplib
from email.message import EmailMessage
from datetime import datetime
import os
from dotenv import load_dotenv
import pymysql

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

# ------------------ LOAD ENV ------------------------
load_dotenv()

# ----------------------- DB ---------------------

def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=3306
    )

# ----------------------- LOAD MODEL -----------------------
from model_loader import load_traffic_model
model, scaler_X, scaler_y = load_traffic_model()

# ----------------------- TITLE -----------------------

st.title("🚦 Smart Traffic Monitoring System")

# ----------------------- LOCATION -----------------------

CITY_DATA = {
    "Delhi": {"Connaught Place": ["Inner Circle"]},
    "Bangalore": {"Whitefield": ["ITPL"]},
    "Chennai": {"Guindy": ["Kathipara Junction"]},
    "Mumbai": {"Andheri": ["Link Road"]},
    "Hyderabad": {"Hitech City": ["Cyber Towers"]}
}

col1, col2 = st.columns(2)

with col1:
    city = st.selectbox("🏙️ City", list(CITY_DATA.keys()))
    area = st.selectbox("📍 Area", list(CITY_DATA[city].keys()))
    landmark = st.selectbox("📌 Landmark", CITY_DATA[city][area])

location = f"{city} - {area} - {landmark}"
st.success(f"📍 Selected Location: {location}")

# ----------------------- TRAFFIC CONTROL -----------------------

st.subheader("🚗 Traffic Controls")

traffic_speed = st.slider("Traffic Speed (km/h)", 5, 80, 30)

#----------------------- FEATURES -----------------------

feature_cols = [
    'latitude', 'longitude',
    'traffic_speed_kmh', 'road_occupancy_pct',
    'sentiment_score', 'ride_sharing_demand',
    'parking_availability', 'emission_levels_g_km',
    'energy_consumption_l_h'
]

TIMESTEPS = 30

# ----------------------- CONGESTION -----------------------

def congestion_level(vehicle_count, speed):
    # combine model + real-world logic
    if speed < 20:
        return "HIGH 🔴"
    elif speed < 40:
        return "MEDIUM 🟡"
    else:
        return "LOW 🟢"

# ----------------------- EMAIL -----------------------

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

# ----------------------- SESSION -----------------------

if "email_sent" not in st.session_state:
    st.session_state.email_sent = False

# ----------------------- INSERT -----------------------

def insert_traffic_forecast(vehicle_count, level, lat, lon):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO traffic_events 
            (timestamp, location, detected_object, confidence, latitude, longitude)
            VALUES (NOW(), %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            location,
            level,
            float(vehicle_count),
            float(lat),
            float(lon)
        ))

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print("DB error:", e)

# ----------------------- FILE UPLOAD-----------------------

# ----------------------- LOAD DATA (AUTO) -----------------------

@st.cache_data
def load_data():
    return pd.read_csv("C:/Users/harip/Downloads/GUVI DS/traffic_data.csv")   

df = load_data()

st.success("✅ Using preloaded dataset")


# ----------------------- VALIDATION -----------------------

missing = [col for col in feature_cols if col not in df.columns]
if missing:
        st.error(f"Missing columns: {missing}")
        st.stop()

if len(df) < 1:
        st.error("Dataset must have at least 1 row")
        st.stop()

# ----------------------- PREDICT -----------------------

if st.button("🚀 Predict Traffic"):

        latest = df[feature_cols].iloc[-1:].copy()

        # ----------------------- CITY LAT/LON -----------------------

        city_lat_lon = {
            "Delhi": (28.63, 77.21),
            "Bangalore": (12.97, 77.59),
            "Chennai": (13.08, 80.27),
            "Mumbai": (19.07, 72.87),
            "Hyderabad": (17.44, 78.39)
        }

        lat, lon = city_lat_lon[city]

        latest['latitude'] = lat
        latest['longitude'] = lon

        # ----------------------- APPLY TRAFFIC SPEED -----------------------

        latest['traffic_speed_kmh'] = traffic_speed

        # ----------------------- SCALE -----------------------

        scaled_X = scaler_X.transform(latest)

        # ----------------------- LSTM INPUT -----------------------

        X_input = np.repeat(scaled_X, TIMESTEPS, axis=0)
        X_input = X_input.reshape(1, TIMESTEPS, len(feature_cols))

        # ----------------------- PREDICT -----------------------

        pred_scaled = model.predict(X_input)
        pred_actual = scaler_y.inverse_transform(pred_scaled)

        predicted_vehicle = int(pred_actual[0][0])

        # ----------------------- CONGESTION -----------------------

        level = congestion_level(predicted_vehicle, traffic_speed)

        # ----------------------- SAVE -----------------------

        insert_traffic_forecast(predicted_vehicle, level, lat, lon)

        #----------------------- ALERT -----------------------

        if "HIGH" in level:
            st.error(f"🚨 {level} Traffic Detected")

            if not st.session_state.email_sent:

                email_body = f"""
🚦 TRAFFIC ALERT

📍 Location: {location}
Vehicle Count: {predicted_vehicle}
Congestion: {level}

Speed: {traffic_speed} km/h

Lat: {lat}
Lon: {lon}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

                if send_email_alert("🚨 Traffic Alert", email_body):
                    st.success("📧 Alert sent!")
                    st.session_state.email_sent = True
                else:
                    st.error("Email failed")

        elif "MEDIUM" in level:
            st.warning(f"⚠️ {level} Traffic")
        else:
            st.success(f"✅ {level} Traffic")

        # ----------------------- METRICS -----------------------
        st.metric("🚗 Predicted Vehicles", predicted_vehicle)
        st.metric("🚦 Congestion Level", level)
        st.metric("🚗 Traffic Speed", f"{traffic_speed} km/h")

        # ----------------------- GRAPH -----------------------
        st.subheader("📈 Traffic Trend")

        fig, ax = plt.subplots()

        if "vehicle_count" in df.columns:
            recent = df["vehicle_count"].values[-20:]
        else:
            recent = np.random.randint(50, 200, 20)

        x = list(range(len(recent)))

        ax.plot(x, recent, marker='o', label="Past Traffic")
        ax.scatter(len(recent), predicted_vehicle, s=120, label="Prediction")

        ax.set_title("Traffic Forecast")
        ax.set_xlabel("Time Step")
        ax.set_ylabel("Vehicles")

        ax.legend()
        ax.grid(True)

        st.pyplot(fig)

# ----------------------- RESET -----------------------

if st.button("🔄 Reset Alert"):
    st.session_state.email_sent = False
    st.info("Alert reset")