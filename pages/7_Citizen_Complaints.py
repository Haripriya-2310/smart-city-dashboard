import streamlit as st
import boto3
import joblib
import pymysql
import os
from dotenv import load_dotenv

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

# ----------------------- DB CONNECTION -----------------------
def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=3306
    )

# -----------------------LOAD MODEL -----------------------
from model_loader import load_complaint_model
model, vectorizer, le = load_complaint_model()

#----------------------- INSERT FUNCTION -----------------------
def insert_complaint(city, category, department, text, sentiment, priority):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        print("Connecting to DB...")

        query = """
            INSERT INTO nlp_complaints 
            (city, category, department, complaint_text, sentiment, priority)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            city,
            category,
            department,
            text,
            sentiment,
            priority
        ))

        conn.commit()
        cursor.close()
        conn.close()

        print("✅ Inserted into DB")

    except Exception as e:
        print("DB error:", e)

# ----------------------- STREAMLIT UI -----------------------
st.set_page_config(page_title="Complaint Analyzer", layout="centered")

st.title("📝 Smart City Complaint Analyzer")

# ----------------------- INPUT -----------------------
city = st.selectbox(
    "City",
    ["Chennai", "Delhi", "Hyderabad", "Bangalore", "Mumbai"]
)

category = st.selectbox(
    "Category",
    ["Air quality", "Road issues", "Crowd", "Accident", "Traffic"]
)

department = st.text_input(
    "Department",
    value=f"{category} Department"
)

text = st.text_area("Enter Complaint", height=120)

# ----------------------- BUTTON -----------------------
if st.button("Analyze Complaint"):

    if text.strip() == "":
        st.error("Please enter a complaint")
    else:
        # Predict sentiment
        vec = vectorizer.transform([text])
        pred = model.predict(vec)
        sentiment = le.inverse_transform(pred)[0]

        # Show result
        st.subheader("Result")
        st.write(f"**Sentiment:** {sentiment}")

        # Store in DB
        # priority logic
        if sentiment == "negative":
            priority = "HIGH"
        elif sentiment == "neutral":
            priority = "MEDIUM"
        else:
            priority = "LOW"

        insert_complaint(city, category, department, text, sentiment, priority)

        st.success("✅ Complaint stored in database")