import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Urbanbot Introduction",
    page_icon="🌇",
    layout="wide"
)

# ---------------- TITLE ----------------
st.markdown(
    """
    <h1 style="margin-bottom:0;">🌇UrbanBot – Smart City Analytics Platform </h1>
    <hr>
    """,
    unsafe_allow_html=True
)

# ---------------- INTRO SECTION ----------------
st.markdown(
    """
    ## 🌆Project Introduction
  
The project focuses on designing and developing an intelligent Smart City Analytics Platform that utilizes **machine learning, deep learning, and natural language processing (NLP)** to monitor and analyze critical urban activities. It aims to address key city challenges such as **traffic congestion, accident detection, road infrastructure issues, air quality prediction, and crowd density estimation** in a unified system.

The platform also incorporates **citizen complaint analysis** using NLP techniques to understand public concerns and identify recurring issues. By processing data from multiple sources, the system transforms raw inputs into **meaningful insights** that support efficient urban management.

An interactive dashboard is provided to visualize real-time data and trends, enabling authorities to make informed decisions. Additionally, an **LLM-powered chatbot** is integrated to assist city administrators by delivering quick insights, summaries, and actionable recommendations based on available data.
""")
#-----------------Problem Statement--------------
st.markdown(
    """
    ## 🚧Problem Statement
- Increasing traffic congestion in urban areas  
- Frequent road accidents and unsafe driving conditions  
- Poor road infrastructure and pothole issues  
- Rising air pollution levels affecting public health  
- Overcrowding in public spaces and events  
- Growing number of citizen complaints and dissatisfaction 

➡️ Overall, these issues highlight the growing complexity of managing modern urban environments
    """)

#------------Objectives------------
st.markdown(
    """
  ## 🎯Objectives
- Monitor urban conditions in real-time  
- Detect accidents and infrastructure issues  
- Predict air quality and crowd density  
- Analyze citizen complaints using NLP  
- Provide actionable insights via dashboard  
""")

#----------Key Features--------------

st.markdown(
    """
  ## ⚙️Key Features
- 📊 Interactive Dashboard  
- 🚗 Traffic & Congestion Analysis  
- 🚨 Accident Detection  
- 🌫️ AQI Prediction  
- 👥 Crowd Monitoring  
- 💬 AI Chatbot Assistant  
""")

#--------------------Technologies Used---------------
st.markdown(
    """
   ## 💻Technologies Used

**Frontend:**
- Streamlit (Interactive Dashboard UI)

**Computer Vision:**
- YOLOv8 for detection of accidents, potholes, road cracks, and streetlight issues  
- CNN for crowd density estimation  

**Time Series Forecasting:**
- LSTM / ARIMA for traffic and air quality (AQI) prediction  

**Natural Language Processing:**
- NLP for citizen complaint analysis and sentiment detection  

**Cloud Architecture:**
- AWS S3 for model and dataset storage  
- AWS RDS for structured data (detections, metrics)  
- AWS EC2 for backend processing and model inference  

**AI Assistant:**
- LLM with Retrieval-Augmented Generation (RAG) for intelligent query handling  
""")

st.caption("🚀 UrbanBot | AI-Powered Smart City Analytics Platform")