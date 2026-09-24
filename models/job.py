"""Pydantic models for structured job-description extraction.

The `description` on each Field is sent to the LLM, so write it as an
instruction: it tells the model what to put in that field.
"""

from pydantic import BaseModel, Field


class Job(BaseModel):
    """Structured job information extracted from a job description."""

    title: str = Field(default="", description="Job title.")
    company: str = Field(default="", description="Hiring organization name.")
    location: str = Field(default="", description="Job location or remote arrangement.")
    employment_type: str = Field(
        default="", description="Employment arrangement, such as full-time or contract."
    )
    summary: str = Field(default="", description="Short overview of the role.")
    responsibilities: list[str] = Field(
        default_factory=list, description="Primary responsibilities of the role."
    )
    required_skills: list[str] = Field(
        default_factory=list, description="Skills explicitly required, one skill per item."
    )
    preferred_skills: list[str] = Field(
        default_factory=list, description="Skills listed as preferred or nice to have, one per item."
    )
    required_qualifications: list[str] = Field(
        default_factory=list, description="Required education, certifications, or qualifications."
    )
    minimum_years_experience: int | None = Field(
        default=None, description="Minimum years of experience, or null when not specified."
    )
