from pathlib import Path
import re


def read_input(file_path: str) -> dict:
    """
    Read the Creator Agent input file and extract:
    - ticket number
    - complete input content
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    content = path.read_text(encoding="utf-8").strip()

    if not content:
        raise ValueError("Input file is empty.")

    ticket_match = re.search(
        r"Ticket\s*:\s*([A-Za-z]+-\d+)",
        content,
        re.IGNORECASE,
    )

    if not ticket_match:
        raise ValueError(
            "Ticket number not found. Expected format: Ticket: QA-1234"
        )

    ticket_number = ticket_match.group(1).upper()

    return {
        "ticket_number": ticket_number,
        "content": content,
    }
