from pydantic import BaseModel, Field
from typing import List


class TestCase(BaseModel):
    test_case_id: str = Field(
        description="Unique test case identifier"
    )

    title: str = Field(
        description="Short and clear title of the test case"
    )

    objective: str = Field(
        description="What this test case validates"
    )

    preconditions: List[str] = Field(
        description="Conditions that must be satisfied before execution"
    )

    test_data: List[str] = Field(
        description="Test data required for execution"
    )

    steps: List[str] = Field(
        description="Detailed steps to execute the test"
    )

    expected_result: str = Field(
        description="Expected result after executing the test"
    )

    priority: str = Field(
        description="Test priority such as High, Medium, or Low"
    )


class PlannerOutput(BaseModel):
    user_story_summary: str = Field(
        description="Clear summary of the user story"
    )

    requirements: List[str] = Field(
        description="Functional and business requirements identified from the user story"
    )

    features: List[str] = Field(
        description="Features identified from the user story"
    )

    scenarios: List[str] = Field(
        description="Important test scenarios identified from the requirements"
    )

    test_scope: List[str] = Field(
        description="What should be included in testing"
    )

    out_of_scope: List[str] = Field(
        description="What should not be included in testing"
    )

    test_strategy: str = Field(
        description="Overall strategy for testing the user story"
    )

    test_plan: str = Field(
        description="Detailed plan describing how testing should be performed"
    )

    test_data: List[str] = Field(
        description="Test data required for the identified scenarios"
    )

    preconditions: List[str] = Field(
        description="Preconditions required before testing"
    )

    test_cases: List[TestCase] = Field(
        description="Detailed test cases derived from the user story"
    )