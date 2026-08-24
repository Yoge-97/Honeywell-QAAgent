from pathlib import Path

from planner.agent import (
    run_planner,
    revise_planner,
)

from creator.agent import (
    run_creator,
    save_creator_output,
    save_karate_files_from_result,
)

from shared.workflow_state import (
    save_workflow_state,
)


PLANNER_OUTPUT_FILE = Path(
    "output/planner_output.json"
)

REVIEW_FEEDBACK_FILE = Path(
    "output/review_feedback.txt"
)


def save_planner_output(planner_output):
    """
    Save the Planner output as JSON.
    """

    PLANNER_OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    PLANNER_OUTPUT_FILE.write_text(
        planner_output.model_dump_json(
            indent=2
        ),
        encoding="utf-8",
    )


def human_validation():
    """
    Ask the human reviewer to approve or reject
    the Planner output.
    """

    print("\n")
    print("=" * 60)
    print("HUMAN VALIDATION")
    print("=" * 60)

    print(
        "\nPlease review the Planner output:"
    )

    print(
        "output/planner_output.json"
    )

    print(
        "\nCurrent status:"
    )

    print(
        "WAITING_FOR_HUMAN"
    )

    while True:

        decision = input(
            "\nEnter approve or reject: "
        ).strip().lower()

        # --------------------------------------------------
        # APPROVE
        # --------------------------------------------------

        if decision in {"approve", "a"}:

            save_workflow_state(
                status="APPROVED",
                approval="approved",
            )

            print(
                "\nPlanner output APPROVED."
            )

            return "approved"

        # --------------------------------------------------
        # REJECT
        # --------------------------------------------------

        if decision in {"reject", "r"}:

            feedback = input(
                "\nEnter the reason for rejection: "
            ).strip()

            if not feedback:

                print(
                    "\nRejection reason cannot be empty."
                )

                continue

            REVIEW_FEEDBACK_FILE.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            REVIEW_FEEDBACK_FILE.write_text(
                feedback,
                encoding="utf-8",
            )

            save_workflow_state(
                status="REJECTED",
                approval="rejected",
            )

            print(
                "\nPlanner output REJECTED."
            )

            print(
                "Review feedback saved."
            )

            return "rejected"

        # --------------------------------------------------
        # INVALID INPUT
        # --------------------------------------------------

        print(
            "\nInvalid choice."
        )

        print(
            "Please enter approve or reject."
        )


def run_planner_revision():
    """
    Run Planner again using human review feedback.
    """

    print("\n")
    print("=" * 60)
    print("PLANNER REVISION")
    print("=" * 60)

    print(
        "\nStarting Planner revision..."
    )

    revised_output = revise_planner(
        user_story_path="input/user_story.md",
        feedback_path=str(
            REVIEW_FEEDBACK_FILE
        ),
    )

    save_planner_output(
        revised_output
    )

    save_workflow_state(
        status="WAITING_FOR_HUMAN",
        approval=None,
    )

    print(
        "\nRevised Planner output saved."
    )

    print(
        "output/planner_output.json"
    )

    print(
        "\nWorkflow returned to Human Validation."
    )


def run_creator_agent():
    """
    Run the Creator Agent after Planner approval.
    """

    print("\n")
    print("=" * 60)
    print("CREATOR AGENT")
    print("=" * 60)

    print(
        "\nStarting Creator Agent..."
    )

    creator_output = run_creator()

    save_creator_output(
        creator_output
    )

    save_karate_files_from_result(
        creator_output
    )

    save_workflow_state(
        status="CREATOR_COMPLETED",
        approval="approved",
    )

    print(
        "\nCreator Agent completed."
    )

    print(
        "Creator output saved to:"
    )

    print(
        "output/creator_output.json"
    )


def run_workflow():
    """
    Run the complete QA Testing Agent workflow.
    """

    print("=" * 60)
    print("QA TESTING AGENT")
    print("=" * 60)

    # ======================================================
    # STEP 1 — PLANNER
    # ======================================================

    print(
        "\nStarting Planner Agent..."
    )

    planner_output = run_planner(
        "input/user_story.md"
    )

    # ======================================================
    # STEP 2 — SAVE PLANNER OUTPUT
    # ======================================================

    save_planner_output(
        planner_output
    )

    print(
        "\nPlanner completed successfully."
    )

    print(
        "Planner output saved to:"
    )

    print(
        "output/planner_output.json"
    )

    # ======================================================
    # STEP 3 — WAIT FOR HUMAN VALIDATION
    # ======================================================

    save_workflow_state(
        status="WAITING_FOR_HUMAN",
        approval=None,
    )

    decision = human_validation()

    # ======================================================
    # STEP 4 — APPROVED
    # ======================================================

    if decision == "approved":

        run_creator_agent()

        return

    # ======================================================
    # STEP 5 — REJECTED
    # ======================================================

    if decision == "rejected":

        run_planner_revision()

        # --------------------------------------------------
        # After revision, ask for human validation again.
        # --------------------------------------------------

        revised_decision = human_validation()

        # --------------------------------------------------
        # Revised Planner APPROVED
        # --------------------------------------------------

        if revised_decision == "approved":

            run_creator_agent()

            return

        # --------------------------------------------------
        # Revised Planner REJECTED
        # --------------------------------------------------

        if revised_decision == "rejected":

            print(
                "\nPlanner revision was rejected."
            )

            print(
                "Another revision cycle can be started."
            )

            return


def main():

    run_workflow()


if __name__ == "__main__":
    main()