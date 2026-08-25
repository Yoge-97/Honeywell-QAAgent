from creator.input_reader import read_input
from creator.karate_generator import generate_karate_script
from creator.github_manager import (
    create_branch,
    write_karate_file,
    commit_changes,
    push_branch,
    create_pull_request,
)


def run_creator(input_file: str) -> dict:
    """
    Run the complete Creator workflow:

    1. Read input
    2. Extract ticket number
    3. Generate Karate script
    4. Create ticket branch
    5. Write Karate feature
    6. Commit changes
    7. Push branch
    8. Create Pull Request
    """

    print("\n[1/8] Reading input...")

    input_data = read_input(input_file)

    ticket_number = input_data["ticket_number"]
    input_content = input_data["content"]

    print(f"Ticket: {ticket_number}")

    print("\n[2/8] Generating Karate script...")

    karate_content = generate_karate_script(
        input_content
    )

    print("Karate script generated.")

    print("\n[3/8] Creating Git branch...")

    branch_name = create_branch(
        ticket_number
    )

    print(f"Branch created: {branch_name}")

    print("\n[4/8] Writing Karate feature...")

    feature_file = write_karate_file(
        karate_content,
        ticket_number,
    )

    print(f"Feature file: {feature_file}")

    print("\n[5/8] Committing changes...")

    commit_changes(
        feature_file,
        ticket_number,
    )

    print("Commit created.")

    print("\n[6/8] Pushing branch...")

    push_branch(branch_name)

    print("Branch pushed to GitHub.")

    print("\n[7/8] Creating Pull Request...")

    pull_request_url = create_pull_request(
        branch_name,
        ticket_number,
    )

    print("\n[8/8] Creator workflow completed.")

    print(f"\nPull Request: {pull_request_url}")

    return {
        "ticket_number": ticket_number,
        "branch_name": branch_name,
        "feature_file": str(feature_file),
        "pull_request_url": pull_request_url,
    }
