import pymysql
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

class SQLAgent:

    def get_connection(self):
        return pymysql.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=3306
        )

    def fetch_dataframe(self, query):
        conn = self.get_connection()
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    
    def get_all_data(self):
        queries = {

            "traffic": """
                SELECT location, timestamp, detected_object, confidence
                FROM traffic_events
                ORDER BY timestamp  DESC LIMIT 5
            """,

            "aqi": """
                SELECT city, aqi_value, timestamp
                FROM aqi_data
                ORDER BY timestamp DESC LIMIT 5
            """,

            "road": """
                SELECT location, detection_type, severity_level, detected_at
                FROM road_detections
                ORDER BY detected_at DESC LIMIT 5
            """,

            "crowd": """
                SELECT location, crowd_count, density_level, timestamp
                FROM crowd_metrics
                ORDER BY timestamp DESC LIMIT 5
            """,

            "complaints": """
                SELECT city, category, sentiment, priority, created_at
                FROM nlp_complaints
                ORDER BY created_at DESC LIMIT 5
            """
        }

    def get_traffic_data(self):
        query = """
            SELECT location, timestamp, detected_object, confidence
            FROM traffic_events
            ORDER BY timestamp DESC LIMIT 5
        """
        df = self.fetch_dataframe(query)
        return df.to_string(index=False)


    def get_aqi_data(self):
        query = """
            SELECT city, aqi_value, timestamp
            FROM aqi_data
            ORDER BY timestamp DESC LIMIT 5
        """
        df = self.fetch_dataframe(query)
        return df.to_string(index=False)


    def get_road_data(self):
        query = """
            SELECT location, detection_type, severity_level, detected_at
            FROM road_detections
            ORDER BY detected_at DESC LIMIT 5
        """
        df = self.fetch_dataframe(query)
        return df.to_string(index=False)


    def get_crowd_data(self):
        query = """
            SELECT location, crowd_count, density_level, timestamp
            FROM crowd_metrics
            ORDER BY timestamp DESC LIMIT 5
        """
        df = self.fetch_dataframe(query)
        return df.to_string(index=False)


    def get_complaint_data(self):
        query = """
            SELECT city, category, sentiment, priority, created_at
            FROM nlp_complaints
            ORDER BY created_at DESC LIMIT 5
        """
        df = self.fetch_dataframe(query)
        return df.to_string(index=False)

            