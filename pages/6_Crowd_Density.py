import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import streamlit as st
import torch
import cv2
import pandas as pd
import numpy as np
import plotly.express as px
import smtplib
from email.message import EmailMessage
from datetime import datetime
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

# ----------------------- LOAD ENV -----------------------
load_dotenv()

# ----------------------- DB CONNECTION-----------------------

def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=3306
    )

# ----------------------- PAGE CONFIG -----------------------

st.set_page_config(page_title="Crowd Monitoring", layout="wide")
st.title("👥 Crowd Density Monitoring System")

# ----------------------- LOCATION -----------------------

CITY_DATA = {
    "Coimbatore": {
        "Singanallur": ["Bus Stand", "Lake Area"],
        "Gandhipuram": ["Central Bus Stand"],
        "RS Puram": ["DB Road"],
        "Peelamedu": ["Airport", "PSG College"]
    }
}

col1, col2 = st.columns(2)

with col1:
    city = st.selectbox("🏙️ City", list(CITY_DATA.keys()))
    area = st.selectbox("📍 Area", list(CITY_DATA[city].keys()))
    landmark = st.selectbox("📌 Landmark", CITY_DATA[city][area])

location = f"{city} - {area} - {landmark}"

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

if "crowd_email_sent" not in st.session_state:
    st.session_state.crowd_email_sent = False

# ----------------------- DENSITY LOGIC -----------------------

def get_density_level(count):
    if count < 300:
        return "LOW"
    elif count < 800:
        return "MEDIUM"
    else:
        return "HIGH"

# ----------------------- INSERT INTO DB -----------------------

def insert_crowd_data(count, density):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO crowd_metrics (timestamp, location, crowd_count, density_level)
            VALUES (NOW(), %s, %s, %s)
        """

        cursor.execute(query, (location, int(count), density))
        conn.commit()

        cursor.close()
        conn.close()

    except Exception as e:
        print("DB error:", e)

# ----------------------- LOAD MODEL -----------------------

from model_loader import load_crowd_model
model = load_crowd_model()
model.eval()

# ----------------------- IMAGE UPLOAD -----------------------

uploaded_file = st.file_uploader("📤 Upload Crowd Image", type=["jpg", "png"])

if uploaded_file:

    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    st.image(img, caption="Uploaded Image", use_container_width=True)

    img_resized = cv2.resize(img, (512, 512))
    img_tensor = torch.tensor(img_resized).permute(2, 0, 1).unsqueeze(0).float() / 255

    with torch.no_grad():
        pred = model(img_tensor)

    density_map = pred.squeeze().numpy()
    pred_count = int(density_map.sum())

    density = get_density_level(pred_count)

    # ----------------------- KPI DISPLAY -----------------------

    col1, col2 = st.columns(2)

    col1.metric("👥 Crowd Count", pred_count)
    col2.metric("📊 Density Level", density)

    # ----------------------- STORE DATA -----------------------

    insert_crowd_data(pred_count, density)

    # ----------------------- HEATMAP-----------------------

    st.subheader("🔥 Crowd Density Heatmap")

    fig = px.imshow(density_map, color_continuous_scale="jet")
    fig.update_layout(coloraxis_showscale=False)

    st.plotly_chart(fig, use_container_width=True)

    # ----------------------- ALERT-----------------------

    st.subheader("⚠️ Safety Status")

    if pred_count > 800:
        st.error("🚨 Overcrowded Area Detected!")

        if not st.session_state.crowd_email_sent:

            email_body = f"""
👥 CROWD ALERT

Location: {location}
Count: {pred_count}

⚠️ High Risk of overcrowding
Take immediate action!

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            if send_email_alert("🚨 Crowd Alert", email_body):
                st.success("📧 Alert sent!")
                st.session_state.crowd_email_sent = True
            else:
                st.error("Email failed")

    else:
        st.success("✅ Area is Safe")

# ----------------------- RESET -----------------------

if st.button("🔄 Reset Alert"):
    st.session_state.crowd_email_sent = False
    st.info("Alert reset")