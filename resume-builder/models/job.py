"""Pydantic models for structured job-description extraction."""

from pydantic import BaseModel, Field


class Job(BaseModel):
    """Structured job information extracted from a job description."""

    title: str = Field(description="Job title.")
    company: str = Field(description="Hiring organization name.")
    location: str = Field(description="Job location or remote arrangement.")
    employment_type: str = Field(
        description="Employment arrangement, such as full-time or contract."
    )
    summary: str = Field(description="Short overview of the role.")
    responsibilities: list[str] = Field(
        description="Primary responsibilities of the role."
    )
    required_skills: list[str] = Field(
        description="Skills explicitly required for the role."
    )
    preferred_skills: list[str] = Field(
        description="Skills explicitly listed as preferred or nice to have."
    )
    required_qualifications: list[str] = Field(
        description="Required education, certifications, or qualifications."
    )
    preferred_qualifications: list[str] = Field(
        description="Preferred education, certifications, or qualifications."
    )
    minimum_years_experience: int | None = Field(
        description="Minimum years of experience, or null when not specified."
    )