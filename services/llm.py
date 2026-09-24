"""One place to create the Groq chat model, shared by every agent."""

import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

DEFAULT_MODEL = "llama-3.3-70b-versatile"


def get_llm(temperature: float = 0) -> ChatGroq:
    """Return a ChatGroq model configured from the .env file."""
    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError("GROQ_API_KEY is not set. Copy .env.example to .env and add your key.")
    return ChatGroq(model=os.getenv("GROQ_MODEL", DEFAULT_MODEL), temperature=temperature)
