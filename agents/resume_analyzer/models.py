"""Pydantic models owned by the Resume Analyzer agent."""

from pydantic import BaseModel, Field


class TailoredExperience(BaseModel):
    """One job in the tailored resume."""

    job_title: str = Field(default="", description="Title in the position, copied from the resume.")
    company: str = Field(default="", description="Employer name, copied from the resume.")
    dates: str = Field(default="", description="Date range, e.g. 'Mar 2022 - Present'.")
    bullets: list[str] = Field(
        default_factory=list,
        description="Rewritten bullet points for this job, most relevant to the target job first.",
    )


class TailoredResume(BaseModel):
    """A resume rewritten to fit one specific job."""

    full_name: str = Field(default="", description="Candidate's full name.")
    email: str = Field(default="", description="Candidate's email address.")
    phone: str = Field(default="", description="Candidate's phone number.")
    location: str = Field(default="", description="Candidate's location.")
    summary: str = Field(default="", description="Short professional summary aimed at the target job.")
    skills: list[str] = Field(
        default_factory=list,
        description="The candidate's own skills, the ones the job asks for first.",
    )
    experience: list[TailoredExperience] = Field(
        default_factory=list, description="Work history, most recent first."
    )
    education: list[str] = Field(
        default_factory=list, description="One line per qualification, e.g. 'B.S. Computer Science - UT Austin (2020)'."
    )
    certifications: list[str] = Field(default_factory=list, description="Certifications, copied from the resume.")
    changes_made: list[str] = Field(
        default_factory=list, description="Short list of what was changed compared to the original resume and why."
    )
