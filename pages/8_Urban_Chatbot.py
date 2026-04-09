import streamlit as st
from chatbot.main_chatbot import chatbot_answer

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

# Page config
st.set_page_config(page_title="Smart City AI", layout="wide")

st.title("🚦 Smart City AI Assistant")
st.markdown("Ask about traffic, accidents, AQI, complaints, etc.")


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
user_input = st.chat_input("Ask something about your city...")

if user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    # Get AI response
    with st.spinner("Analyzing data..."):
        response = chatbot_answer(user_input)

    # Show AI response
    with st.chat_message("assistant"):
        st.write(response)

    st.session_state.messages.append({"role": "assistant", "content": response})