"""Pydantic models for structured resume extraction.

The `description` on each Field is sent to the LLM, so write it as an
instruction: it tells the model what to put in that field.
"""

from pydantic import BaseModel, Field


class WorkExperience(BaseModel):
    """A single position held by the candidate."""

    job_title: str = Field(default="", description="Candidate's title in the position.")
    company: str = Field(default="", description="Employer name.")
    start_date: str = Field(default="", description="When the job started, as written (e.g. 'Jan 2021').")
    end_date: str = Field(default="", description="When the job ended, or 'Present' for the current job.")
    responsibilities: list[str] = Field(
        default_factory=list, description="Responsibilities explicitly stated for the position."
    )
    achievements: list[str] = Field(
        default_factory=list, description="Measurable or notable achievements explicitly stated."
    )


class Education(BaseModel):
    """A single academic qualification."""

    institution: str = Field(default="", description="School or university name.")
    degree: str = Field(default="", description="Degree or qualification earned.")
    field_of_study: str = Field(default="", description="Major or area of study.")
    end_date: str = Field(default="", description="Graduation or completion date, as written.")


class Resume(BaseModel):
    """Structured candidate information extracted from a resume."""

    full_name: str = Field(default="", description="Candidate's full name.")
    email: str = Field(default="", description="Candidate's email address.")
    phone: str = Field(default="", description="Candidate's phone number.")
    location: str = Field(default="", description="Candidate's city, state, or country.")
    summary: str = Field(default="", description="Professional summary or objective.")
    skills: list[str] = Field(
        default_factory=list, description="Technical and professional skills, one skill per item."
    )
    total_years_experience: float | None = Field(
        default=None, description="Total years of professional experience, or null if unclear."
    )
    work_experience: list[WorkExperience] = Field(
        default_factory=list, description="Employment history, most recent first."
    )
    education: list[Education] = Field(
        default_factory=list, description="Academic qualifications, most recent first."
    )
    certifications: list[str] = Field(
        default_factory=list, description="Professional certifications and licenses."
    )
