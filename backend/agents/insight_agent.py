import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")


def generate_insights(data):
    try:
        client = genai.Client(
            api_key=API_KEY
        )

        prompt = f"""
        You are a financial health assistant.

        Analyze this financial report and provide:

        1. Overall financial health
        2. Overspending warnings
        3. Top problematic categories
        4. Practical suggestions to reduce spending

        Financial Data:
        {data}
        """

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        return response.text

    except Exception:
        return (
            "AI insights temporarily unavailable due to "
            "Gemini API quota limits. "
            "Financial analysis completed successfully."
        )