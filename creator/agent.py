import json
from pathlib import Path

from crewai import Agent, Task, Crew, Process

from shared.llm import llm


PLANNER_OUTPUT_FILE = Path(
    "output/planner_output.json"
)

CREATOR_OUTPUT_FILE = Path(
    "output/creator_output.json"
)


def create_creator_agent():

    return Agent(
        role="QA Test Script Creator",
        goal=(
            "Convert approved QA test cases into "
            "maintainable Karate test scripts."
        ),
        backstory=(
            "You are an experienced QA automation engineer "
            "specialized in API and UI test automation using "
            "the Karate framework. You create clean, reusable, "
            "maintainable test scripts based strictly on "
            "approved test cases."
        ),
        llm=llm,
        verbose=True,
    )


def read_planner_output():

    if not PLANNER_OUTPUT_FILE.exists():
        raise FileNotFoundError(
            "Planner output file does not exist."
        )

    return json.loads(
        PLANNER_OUTPUT_FILE.read_text(
            encoding="utf-8"
        )
    )


def run_creator():

    planner_output = read_planner_output()

    creator_agent = create_creator_agent()

    creator_task = Task(
        description=f"""
You are given the approved Planner output below.

Planner Output:

{json.dumps(planner_output, indent=2)}

Your responsibility is to create Karate test scripts
for the approved test cases.

Follow these rules:

1. Use only the approved test cases.
2. Do not invent requirements.
3. Create one or more Karate feature files as appropriate.
4. Use clear Feature and Scenario names.
5. Follow Karate syntax.
6. Keep the scripts readable.
7. Reuse common steps where possible.
8. Include positive and negative scenarios from the
   approved test cases.
9. Respect the test data and preconditions defined by
   the Planner.
10. Return the generated Karate scripts in this JSON format.

[
    {{
        "file_name": "booking_form.feature",
        "content": "complete Karate feature file content"
    }}
]

IMPORTANT:

The content must contain ONLY the Karate feature file.

Do NOT include:
- explanations
- headings
- Markdown
- code fences
- ```karate
- ```
- introductory text
- concluding text

The content must start directly with:

Feature:

and contain only valid Karate syntax.
""",
        expected_output=(
            "A complete set of Karate test scripts "
            "based on the approved Planner output."
        ),
        agent=creator_agent,
    )

    crew = Crew(
        agents=[creator_agent],
        tasks=[creator_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()

    return result


def save_creator_output(result):

    CREATOR_OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    CREATOR_OUTPUT_FILE.write_text(
        str(result),
        encoding="utf-8",
    )
def save_karate_file(file_name, content):
    """
    Save one generated Karate feature file.
    """

    karate_directory = Path("output/karate")

    karate_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path = karate_directory / file_name

    file_path.write_text(
        content,
        encoding="utf-8",
    )

    print(
        f"Karate file created: {file_path}"
    )
def save_karate_files_from_result(result):
    """
    Extract Karate files from the Creator result
    and save them.
    """

    result_text = str(result).strip()

    files = json.loads(result_text)

    for file_data in files:
        file_name = file_data["file_name"]
        content = file_data["content"]

        save_karate_file(
            file_name,
            content,
        )

if __name__ == "__main__":

    result = run_creator()

    save_creator_output(result)

    print(
        "\nCreator output saved to:"
    )

    print(
        "output/creator_output.json"
    )