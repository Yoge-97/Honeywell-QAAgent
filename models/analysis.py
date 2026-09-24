"""Pydantic models for the resume-vs-job analysis result."""

from typing import Literal

from pydantic import BaseModel, Field


class SkillGap(BaseModel):
    """A skill the job asks for that the resume does not show."""

    skill: str = Field(default="", description="The missing or weak skill.")
    importance: Literal["required", "preferred"] = Field(
        default="required", description="Whether the job lists it as required or preferred."
    )
    suggestion: str = Field(
        default="", description="A concrete way the candidate can close this gap."
    )


class Analysis(BaseModel):
    """How well a resume matches a job, with scores and advice."""

    overall_score: int = Field(default=0, ge=0, le=100, description="Overall match from 0 to 100.")
    skills_score: int = Field(default=0, ge=0, le=100, description="Skills match from 0 to 100.")
    experience_score: int = Field(
        default=0, ge=0, le=100, description="Experience match from 0 to 100."
    )
    education_score: int = Field(
        default=0, ge=0, le=100, description="Education and qualifications match from 0 to 100."
    )
    matched_skills: list[str] = Field(
        default_factory=list, description="Job skills that the resume clearly shows."
    )
    skill_gaps: list[SkillGap] = Field(
        default_factory=list, description="Job skills that are missing or weak in the resume."
    )
    strengths: list[str] = Field(
        default_factory=list, description="Where the candidate is a strong fit for this job."
    )
    improvements: list[str] = Field(
        default_factory=list, description="Specific changes to make the resume fit this job better."
    )
    summary: str = Field(default="", description="Two or three sentence verdict on the match.")
