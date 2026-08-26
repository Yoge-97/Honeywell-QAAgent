import os
import time

from dotenv import load_dotenv
from google import genai


load_dotenv()


def generate_karate_script(input_content: str) -> str:
    """
    Generate a Karate feature file from the approved QA test input.
    """

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY was not found in .env"
        )

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are a senior QA automation engineer specializing in Karate.

Convert the following approved QA test cases into a Karate feature file.

Requirements:
1. Return ONLY valid Karate/Gherkin content.
2. Start with Feature:
3. Include Background when required.
4. Create one Scenario for each test case.
5. Preserve the test case IDs.
6. Use clear Given, When, Then steps.
7. Do not invent requirements that are not present in the input.
8. Do not include markdown code fences.
9. Do not include explanations outside the feature file.

Approved QA input:

{input_content}
"""

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
            )
            break
        except Exception as exc:
            message = str(exc).lower()
            if attempt == 2 or not any(
                token in message
                for token in (
                    "503",
                    "unavailable",
                    "temporarily",
                    "rate limit",
                    "429",
                    "timeout",
                )
            ):
                raise
            time.sleep(2 ** attempt)

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    return response.text.strip()
