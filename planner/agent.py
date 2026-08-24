from pathlib import Path
from crewai import Agent, Task, Crew, Process

from planner.markdown_reader import read_user_story
from planner.prompts import (
    PLANNER_SYSTEM_PROMPT,
    PLANNER_USER_PROMPT,
)
from planner.schemas import PlannerOutput
from shared.llm import llm


def create_planner_agent() -> Agent:
    """
    Create the QA Planner Agent.
    """

    planner_agent = Agent(
        role="Senior QA Test Planner",
        goal=(
            "Analyze the provided software user story and create a "
            "complete QA test plan, strategy, scenarios, test cases, "
            "test data, and preconditions."
        ),
        backstory=PLANNER_SYSTEM_PROMPT,
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    return planner_agent


def create_planner_task(
    user_story: str,
    planner_agent: Agent,
) -> Task:
    """
    Create the Planner task using the Markdown user story.
    """

    user_prompt = PLANNER_USER_PROMPT.format(
        user_story=user_story
    )

    planner_task = Task(
        description=user_prompt,
        expected_output=(
            "A complete QA planning document containing the user story "
            "summary, requirements, features, scenarios, test scope, "
            "out-of-scope items, test strategy, test plan, test data, "
            "preconditions, and detailed test cases."
        ),
        agent=planner_agent,
        output_pydantic=PlannerOutput,
    )

    return planner_task

def revise_planner(
    user_story_path: str,
    feedback_path: str,
) -> PlannerOutput:
    """
    Revise the Planner output using human feedback.
    """

    user_story = read_user_story(
        user_story_path
    )

    feedback = Path(
        feedback_path
    ).read_text(
        encoding="utf-8"
    ).strip()

    if not feedback:
        raise ValueError(
            "Review feedback is empty."
        )

    planner_agent = create_planner_agent()

    revision_prompt = f"""
The previous Planner output was reviewed by a human
and was rejected.

You must revise the QA planning output.

Original user story:

{user_story}

Human review feedback:

{feedback}

Create a corrected Planner output.

Important:

- Keep valid information from the previous planning.
- Address every point in the human feedback.
- Do not invent requirements.
- Maintain positive and negative coverage.
- Update test scenarios when necessary.
- Update test cases when necessary.
- Return the complete PlannerOutput structure.
"""

    revision_task = Task(
        description=revision_prompt,
        expected_output=(
            "A revised and complete QA planning document "
            "addressing the human review feedback."
        ),
        agent=planner_agent,
        output_pydantic=PlannerOutput,
    )

    crew = Crew(
        agents=[planner_agent],
        tasks=[revision_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()

    if result.pydantic is None:
        raise ValueError(
            "Planner revision did not return "
            "the expected structured output."
        )

    return result.pydantic

def run_planner(
    user_story_path: str = "input/user_story.md",
) -> PlannerOutput:
    """
    Read the user story and execute the Planner Agent.
    """

    user_story = read_user_story(user_story_path)

    planner_agent = create_planner_agent()

    planner_task = create_planner_task(
        user_story=user_story,
        planner_agent=planner_agent,
    )

    crew = Crew(
        agents=[planner_agent],
        tasks=[planner_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()

    if result.pydantic is None:
        raise ValueError(
            "Planner did not return the expected structured output."
        )

    return result.pydantic