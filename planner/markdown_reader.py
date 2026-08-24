from pathlib import Path


def read_user_story(file_path: str) -> str:
    """
    Read the user story Markdown file and return its contents.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"User story file was not found: {file_path}"
        )

    if not path.is_file():
        raise ValueError(
            f"The provided path is not a file: {file_path}"
        )

    content = path.read_text(encoding="utf-8").strip()

    if not content:
        raise ValueError(
            f"The user story file is empty: {file_path}"
        )

    return content