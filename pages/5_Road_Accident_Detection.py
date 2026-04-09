import streamlit as st
import numpy as np
from PIL import Image
import smtplib
from email.message import EmailMessage
from datetime import datetime
import os
from dotenv import load_dotenv
import pymysql

from ultralytics import YOLO
from model_loader import load_yolo_model

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

#-----------------------LOAD ENV -----------------------

load_dotenv()

# ----------------------- DB CONNECTION -----------------------

def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=3306
    )

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

if "cv_email_sent" not in st.session_state:
    st.session_state.cv_email_sent = False

# ----------------------- PAGE -----------------------

st.set_page_config(page_title="Road Monitoring", layout="wide")
st.title("🚧Smart Road Issue Detection System")

#-----------------------LOCATION-----------------------

CITY_DATA = {
    "Delhi": {
        "Connaught Place": ["Inner Circle", "Outer Circle"],
        "Karol Bagh": ["Ajmal Khan Road"]
    },
    "Bangalore": {
        "Whitefield": ["ITPL", "Forum Mall"],
        "MG Road": ["Metro Station"]
    },
    "Chennai": {
        "Guindy": ["Kathipara Junction"],
        "T Nagar": ["Pondy Bazaar"]
    },
    "Mumbai": {
        "Andheri": ["Link Road"],
        "Bandra": ["Bandra Station"]
    },
    "Hyderabad": {
        "Hitech City": ["Cyber Towers"],
        "Gachibowli": ["Financial District"]
    }
}

col1, col2 = st.columns(2)

with col1:
    city = st.selectbox("🏙️ City", list(CITY_DATA.keys()))
    area = st.selectbox("📍 Area", list(CITY_DATA[city].keys()))
    landmark = st.selectbox("📌 Landmark", CITY_DATA[city][area])

location = f"{city} - {area} - {landmark}"

st.success(f"📍 Selected Location: {location}")

# ----------------------- SEVERITY -----------------------

def get_severity(obj):
    if obj == "accident":
        return "CRITICAL"
    elif obj == "pathole":
        return "HIGH"
    elif obj == "roadcrack":
        return "MEDIUM"
    else:
        return "LOW"

# ----------------------- INSERT -----------------------

def insert_accident_event(detected_objects):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO road_detections 
            (location, detection_type, confidence, severity_level, image_path, detected_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """

        for obj in detected_objects:
            cursor.execute(query, (
                location,      # ✅ dynamic location
                obj,
                0.9,
                get_severity(obj),
                "uploaded_img"
            ))

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print("DB error:", e)

# ----------------------- LOAD MODEL -----------------------

model = load_yolo_model()

# ----------------------- UPLOAD IMAGE -----------------------

uploaded = st.file_uploader("📤 Upload Road Image", type=["jpg", "jpeg", "png"])

if uploaded:
    image = Image.open(uploaded).convert("RGB")

    results = model.predict(image, conf=0.25)
    annotated = results[0].plot()

    st.image(annotated, caption="Detection Output", use_container_width=True)

    classes = results[0].boxes.cls.cpu().numpy().astype(int)
    names = model.names

    if len(classes) == 0:
        st.warning("⚠️ No issues detected")

    else:
        detected = [names[c] for c in classes]
        unique_detected = list(set(detected))

        insert_accident_event(unique_detected)

        # -----------------------KPI -----------------------

        col1, col2 = st.columns(2)
        col1.metric("🚨 Issues Detected", len(unique_detected))
        col2.metric("📊 Severity Level", max([get_severity(x) for x in unique_detected]))

        st.success(f"Detected: {', '.join(unique_detected)}")

        # ----------------------- ALERT -----------------------

        if not st.session_state.cv_email_sent:

            alert_msg = ""

            if "accident" in unique_detected:
                alert_msg += "🚨🚧 Accident detected!\n"
            if "pathole" in unique_detected:
                alert_msg += "🕳️🚧 Pathole detected\n"
            if "roadcrack" in unique_detected:
                alert_msg += "💥🚧 Road crack detected\n"

            if alert_msg != "":

                email_body = f"""
🚦 URBANBOT ROAD ALERT

📍 Location: {location}

Detected Issues:
{', '.join(unique_detected)}

Details:
{alert_msg}

🛠 Action Required Immediately

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

                if send_email_alert("🚨 Road Alert", email_body):
                    st.success("📧 Alert sent!")
                    st.session_state.cv_email_sent = True
                else:
                    st.error("Email failed")

#----------------------- RESET-----------------------

if st.button("🔄 Reset Alert"):
    st.session_state.cv_email_sent = False
    st.info("Alert reset")