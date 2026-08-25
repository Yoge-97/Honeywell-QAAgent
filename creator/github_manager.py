import os
import secrets
import subprocess
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


def run_git_command(command: list[str]) -> str:
    """
    Run a Git command and return its output.

    Raises:
        RuntimeError: If the Git command fails.
    """

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Git command failed:\n"
            f"{' '.join(command)}\n\n"
            f"{result.stderr.strip()}"
        )

    return result.stdout.strip()


def create_branch(ticket_number: str) -> str:
    """
    Create a unique ticket-specific feature branch.

    Example:
        feature/QA-1234-karate-tests-a8f31c
    """

    unique_id = secrets.token_hex(3)

    branch_name = (
        f"feature/{ticket_number}-karate-tests-{unique_id}"
    )

    run_git_command(
        ["git", "checkout", "-b", branch_name]
    )

    print(
        f"Created unique branch: {branch_name}"
    )

    return branch_name


def write_karate_file(
    karate_content: str,
    ticket_number: str,
) -> Path:
    """
    Write the generated Karate feature file.
    """

    output_directory = Path(
        "src/test/java/karate"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    feature_file = (
        output_directory
        / f"{ticket_number.lower()}_booking.feature"
    )

    feature_file.write_text(
        karate_content,
        encoding="utf-8",
    )

    print(
        f"Karate feature written to: {feature_file}"
    )

    return feature_file


def commit_changes(
    feature_file: Path,
    ticket_number: str,
) -> None:
    """
    Stage and commit the generated Karate file.
    """

    run_git_command(
        ["git", "add", str(feature_file)]
    )

    run_git_command(
        [
            "git",
            "commit",
            "-m",
            f"{ticket_number}: Add Karate automation tests",
        ]
    )

    print(
        f"Committed changes for {ticket_number}"
    )


def push_branch(branch_name: str) -> None:
    """
    Push the feature branch to GitHub.
    """

    run_git_command(
        [
            "git",
            "push",
            "-u",
            "origin",
            branch_name,
        ]
    )

    print(
        f"Pushed branch to GitHub: {branch_name}"
    )


def create_pull_request(
    branch_name: str,
    ticket_number: str,
) -> str:
    """
    Create a GitHub Pull Request using GitHub CLI.
    """

    owner = os.getenv(
        "GITHUB_OWNER",
        "Yoge-97",
    )

    repository = os.getenv(
        "GITHUB_REPOSITORY",
        "Honeywell-QAAgent",
    )

    base_branch = os.getenv(
        "GITHUB_BASE_BRANCH",
        "main",
    )

    if not owner:
        raise ValueError(
            "GITHUB_OWNER is not configured in .env"
        )

    if not repository:
        raise ValueError(
            "GITHUB_REPOSITORY is not configured in .env"
        )

    command = [
        "gh",
        "pr",
        "create",
        "--repo",
        f"{owner}/{repository}",
        "--base",
        base_branch,
        "--head",
        branch_name,
        "--title",
        f"{ticket_number}: Add Karate automation tests",
        "--body",
        (
            f"## Ticket\n\n"
            f"{ticket_number}\n\n"
            f"## Changes\n\n"
            f"Generated Karate automation tests "
            f"by the QA Creator Agent.\n\n"
            f"## Branch\n\n"
            f"{branch_name}"
        ),
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Pull Request creation failed:\n"
            f"{result.stderr.strip()}"
        )

    pull_request_url = result.stdout.strip()

    print(
        f"Pull Request created: {pull_request_url}"
    )

    return pull_request_url