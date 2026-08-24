import os

from dotenv import load_dotenv
from crewai import LLM


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY was not found. "
        "Please check your .env file."
    )


llm = LLM(
    model="gemini/gemini-3.6-flash",
    api_key=GEMINI_API_KEY,
)