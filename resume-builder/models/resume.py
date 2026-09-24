"""Pydantic models for structured resume extraction."""

from datetime import date

from pydantic import BaseModel, Field


class WorkExperience(BaseModel):
    """A single position held by the candidate."""

    job_title: str = Field(description="Candidate's title in the position.")
    company: str = Field(description="Employer name.")
    location: str = Field(description="City, state, or remote location.")
    start_date: date = Field(description="Date employment began.")
    end_date: date | None = Field(
        description="Date employment ended, or null for the current position."
    )
    responsibilities: list[str] = Field(
        description="Responsibilities explicitly stated for the position."
    )
    achievements: list[str] = Field(
        description="Measurable or notable achievements explicitly stated."
    )


class Education(BaseModel):
    """A single academic qualification."""

    institution: str = Field(description="School or university name.")
    degree: str = Field(description="Degree or qualification earned.")
    field_of_study: str = Field(description="Major or area of study.")
    start_date: date | None = Field(description="Date the program began.")
    end_date: date | None = Field(description="Graduation or completion date.")


class Resume(BaseModel):
    """Structured candidate information extracted from a resume."""

    full_name: str = Field(description="Candidate's full name.")
    email: str = Field(description="Candidate's professional email address.")
    phone: str = Field(description="Candidate's phone number.")
    location: str = Field(description="Candidate's city, state, or country.")
    summary: str = Field(description="Professional summary or objective.")
    skills: list[str] = Field(description="Technical and professional skills.")
    work_experience: list[WorkExperience] = Field(
        description="Employment history, ordered from most recent to oldest."
    )
    education: list[Education] = Field(
        description="Academic qualifications, ordered from most recent to oldest."
    )
    certifications: list[str] = Field(
        description="Professional certifications and licenses."
    )
    languages: list[str] = Field(description="Languages the candidate can use.")