import streamlit as st

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="About Me - Hari Priya",
    page_icon="👩‍💻",
    layout="wide"
)

# ================= CUSTOM STYLE =================
st.markdown("""
    <style>
        body {
            background-color: #f5f7fa;
        }
        .main-title {
            font-size: 40px;
            font-weight: bold;
            color: #2c3e50;
        }
        .sub-title {
            font-size: 20px;
            color: #555;
        }
        .section-title {
            font-size: 24px;
            font-weight: bold;
            color: #1f77b4;
            margin-top: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown('<p class="main-title">Hari Priya Selvaraj</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">MSc Computer Science | Aspiring Data Scientist </p>', unsafe_allow_html=True)

st.divider()

# ================= SUMMARY =================
st.markdown('<p class="section-title">Professional Summary</p>', unsafe_allow_html=True)

st.write("""
MSc Computer Science graduate with hands-on experience in data analysis, machine learning, and NLP 
using Python. Skilled in data cleaning, exploratory data analysis (EDA), feature engineering, and building 
predictive models using Scikit-learn and SQL. Developed interactive dashboards using Power BI and 
Streamlit to derive actionable business insights.

Skilled in:
- Data Cleaning & EDA
- Feature Engineering
- Predictive Modeling (Scikit-learn)
- SQL & Dashboard Development

Built interactive dashboards using **Streamlit & Power BI** to generate actionable insights.
""")

# ================= SKILLS =================
st.markdown('<p class="section-title">Technical Skills</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.write("**Programming:** Python")
    st.write("**Libraries:** Pandas, NumPy, Matplotlib, Seaborn")

with col2:
    st.write("**ML & NLP:** Scikit-learn, Sentiment Analysis, SpaCy")
    st.write("**Tools:** SQL, Git, GitHub, Power BI, Streamlit")

st.write("**Core Skills:** Data Cleaning, EDA, Feature Engineering, Statistical Analysis")

# ================= EDUCATION =================
st.markdown('<p class="section-title">Education</p>', unsafe_allow_html=True)

st.write("""
🎓 **MSc Computer Science**  
Avinashilingam Institute (2021–2023)

🎓 **BSc Computer Science**  
Karpagam Academy (2018–2021)
""")

# ================= CERTIFICATIONS =================
st.markdown('<p class="section-title">Certifications</p>', unsafe_allow_html=True)

st.write("""
- Data Analysis with Python – freeCodeCamp  
- Internet of Things – Cloudkampus  
""")

# ================= FOOTER =================
st.divider()
