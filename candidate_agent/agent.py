"""Core agent: one structured Claude call per (job, candidate) pair + consistency guardrails."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass

import anthropic

from .prompts import SYSTEM_PROMPT, build_user_message
from .schema import Assessment

DEFAULT_MODEL = os.environ.get("CANDIDATE_AGENT_MODEL", "claude-opus-5")
DEFAULT_EFFORT = os.environ.get("CANDIDATE_AGENT_EFFORT", "high")

STRONG_THRESHOLD = 75
MEDIUM_THRESHOLD = 55


class AgentError(RuntimeError):
    pass


@dataclass
class AnalysisResult:
    assessment: Assessment
    elapsed_sec: float
    model: str
    input_tokens: int
    output_tokens: int


def fit_level_for(score: int) -> str:
    if score >= STRONG_THRESHOLD:
        return "Strong"
    if score >= MEDIUM_THRESHOLD:
        return "Medium"
    return "Weak"


def apply_guardrails(a: Assessment) -> Assessment:
    """Make the output internally consistent regardless of model drift.

    - score is clamped to 0..100 and the fit level is always derived from it;
    - Weak candidates are never recommended for contact;
    - outreach exists only for Contact.
    """
    a = a.model_copy(deep=True)
    a.fit_score = max(0, min(100, int(a.fit_score)))
    a.fit_level = fit_level_for(a.fit_score)
    if a.fit_level == "Weak" and a.recommendation == "Contact":
        a.recommendation = "Skip"
        a.recommendation_reason = f"[auto: score < {MEDIUM_THRESHOLD}] {a.recommendation_reason}"
    if a.recommendation == "Skip":
        a.outreach = None
    elif a.outreach is None:
        raise AgentError("Model recommended Contact but returned no outreach")
    return a


class CandidateMatchAgent:
    def __init__(
        self,
        client: anthropic.Anthropic | None = None,
        model: str = DEFAULT_MODEL,
        effort: str = DEFAULT_EFFORT,
    ):
        self.client = client or anthropic.Anthropic()
        self.model = model
        self.effort = effort

    def analyze(
        self,
        job_description: str,
        candidate_profile: str,
        *,
        company_context: str | None = None,
        recruiter_name: str | None = None,
        language: str = "Russian",
        outreach_language: str | None = None,
        channel: str = "LinkedIn InMail",
    ) -> AnalysisResult:
        if not job_description.strip():
            raise AgentError("Job description is empty")
        if not candidate_profile.strip():
            raise AgentError("Candidate profile is empty")

        user_message = build_user_message(
            job_description,
            candidate_profile,
            company_context=company_context,
            recruiter_name=recruiter_name,
            language=language,
            outreach_language=outreach_language,
            channel=channel,
        )

        started = time.monotonic()
        response = self.client.messages.parse(
            model=self.model,
            max_tokens=16000,
            thinking={"type": "adaptive"},
            output_config={"effort": self.effort},
            system=[
                {"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}
            ],
            messages=[{"role": "user", "content": user_message}],
            output_format=Assessment,
        )
        elapsed = time.monotonic() - started

        if response.stop_reason == "refusal":
            raise AgentError("The model declined to process this request")
        if response.stop_reason == "max_tokens":
            raise AgentError("Response was truncated (max_tokens reached)")
        if response.parsed_output is None:
            raise AgentError("Model returned no structured output")

        return AnalysisResult(
            assessment=apply_guardrails(response.parsed_output),
            elapsed_sec=elapsed,
            model=self.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )
