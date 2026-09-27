"""Structured output schema of the Candidate Match & Outreach Agent."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

FitLevel = Literal["Strong", "Medium", "Weak"]
Recommendation = Literal["Contact", "Skip"]
MustHaveStatus = Literal["met", "partial", "not_met", "unknown"]


class MustHaveCheck(BaseModel):
    requirement: str = Field(description="Must-have requirement taken from the job description")
    status: MustHaveStatus = Field(
        description="met / partial / not_met / unknown (no data in the profile)"
    )
    evidence: str = Field(description="Short evidence from the profile, or why it is unknown")


class Outreach(BaseModel):
    personalization_hook: str = Field(
        description="The single most specific, non-generic detail of the candidate to open with"
    )
    selling_point: str = Field(
        description="The strongest reason this particular role is attractive to this particular candidate"
    )
    tone_of_voice: str = Field(
        description="Recommended tone and why (e.g. 'peer-to-peer, technical, concise')"
    )
    subject: str = Field(description="Subject line / first line preview for email or InMail")
    message: str = Field(description="Ready-to-send outreach message, 60-120 words, with a clear soft CTA")
    follow_up: str = Field(description="Short follow-up message to send in 3-5 days if there is no reply")


class Assessment(BaseModel):
    candidate_name: Optional[str] = Field(description="Candidate name if present in the profile")
    role_title: str = Field(description="Role title from the job description")
    fit_score: int = Field(description="Overall fit score, integer 0-100")
    fit_level: FitLevel
    summary: str = Field(description="2-3 sentence verdict for the recruiter")
    must_have_match: list[MustHaveCheck]
    strengths: list[str]
    gaps: list[str]
    risks: list[str] = Field(
        description="Hiring risks: job hopping, overqualification, relocation, salary, notice period, etc."
    )
    missing_information: list[str] = Field(
        description="What is missing to decide confidently - questions to clarify at the first contact"
    )
    recommendation: Recommendation
    recommendation_reason: str
    outreach: Optional[Outreach] = Field(
        description="Filled only when recommendation is Contact, otherwise null"
    )
