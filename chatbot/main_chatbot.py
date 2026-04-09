from chatbot.sql_agent import SQLAgent
from chatbot.llm_client import generate_response
from chatbot.prompt import build_prompt
from chatbot.report_agent import ReportAgent
from chatbot.email_agent import EmailAgent

sql = SQLAgent()
report = ReportAgent()
email = EmailAgent()

def chatbot_answer(question):

    question_lower = question.lower()

    # ---------------- INTENT DETECTION ----------------

    if "road" in question_lower or "pothole" in question_lower or "damage" in question_lower or "accident" in question_lower:
        data = {
            "traffic": "",
            "aqi": "",
            "road": sql.get_road_data(),  
            "crowd": "",
            "complaints": ""
        }

    elif "traffic" in question_lower or "congestion" in question_lower:
        data = {
            "traffic": sql.get_traffic_data(),
            "aqi": "",
            "road": "",
            "crowd": "",
            "complaints": ""
        }

    elif "aqi" in question_lower or "air quality" in question_lower:
        data = {
            "traffic": "",
            "aqi": sql.get_aqi_data(),
            "road": "",
            "crowd": "",
            "complaints": ""
        }

    elif "crowd" in question_lower or "density" in question_lower:
        data = {
            "traffic": "",
            "aqi": "",
            "road": "",
            "crowd": sql.get_crowd_data(),
            "complaints": ""
        }

    elif "complaint" in question_lower:
        data = {
            "traffic": "",
            "aqi": "",
            "road": "",
            "crowd": "",
            "complaints": sql.get_complaint_data()
        }

    else:
        data = sql.get_all_data()

    # ---------------- CONTEXT ----------------
    
    context = f"""

TRAFFIC DATA:
{data['traffic']}

AQI DATA:
{data['aqi']}

ROAD DAMAGE DATA:
{data['road']}

CROWD DATA:
{data['crowd']}

COMPLAINTS DATA:
{data['complaints']}
"""

    # ---------------- LLM ----------------
    prompt = build_prompt(question, context)
    llm_output = generate_response(prompt)

    # ---------------- REPORT ----------------
    final_report = report.generate_report(llm_output)

    # ---------------- EMAIL ----------------
    if "email" in question_lower:
        email.send_email("Smart City Report", final_report)
        return final_report + "\n\n📧 Email Sent!"

    return final_report