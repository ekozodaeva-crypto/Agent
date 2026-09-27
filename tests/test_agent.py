from types import SimpleNamespace

import pytest

from candidate_agent import AgentError, CandidateMatchAgent, KpiTracker
from candidate_agent.agent import apply_guardrails, fit_level_for
from candidate_agent.render import render_markdown, render_ranking
from candidate_agent.schema import Assessment, MustHaveCheck, Outreach


def make_assessment(**kw) -> Assessment:
    base = dict(
        candidate_name="Alexey",
        role_title="Senior Backend Engineer",
        fit_score=82,
        fit_level="Strong",
        summary="Good fit.",
        must_have_match=[MustHaveCheck(requirement="Go 2+ years", status="met", evidence="Go since 2018")],
        strengths=["Payments"],
        gaps=[],
        risks=[],
        missing_information=["Salary expectations"],
        recommendation="Contact",
        recommendation_reason="Strong must-have coverage",
        outreach=Outreach(
            personalization_hook="go-idempotency",
            selling_point="New processing core",
            tone_of_voice="peer-to-peer",
            subject="Payment routing at 5k TPS",
            message="Hi Alexey...",
            follow_up="Sharing our architecture post...",
        ),
    )
    base.update(kw)
    return Assessment(**base)


class FakeMessages:
    def __init__(self, parsed, stop_reason="end_turn"):
        self.parsed, self.stop_reason, self.calls = parsed, stop_reason, []

    def parse(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            parsed_output=self.parsed,
            stop_reason=self.stop_reason,
            usage=SimpleNamespace(input_tokens=100, output_tokens=50),
        )


def fake_client(parsed, stop_reason="end_turn"):
    return SimpleNamespace(messages=FakeMessages(parsed, stop_reason))


@pytest.mark.parametrize("score,level", [(100, "Strong"), (75, "Strong"), (74, "Medium"), (55, "Medium"), (54, "Weak"), (0, "Weak")])
def test_fit_level_thresholds(score, level):
    assert fit_level_for(score) == level


def test_guardrails_derive_level_and_clamp():
    a = apply_guardrails(make_assessment(fit_score=140, fit_level="Weak"))
    assert a.fit_score == 100 and a.fit_level == "Strong"


def test_guardrails_weak_is_skipped_and_outreach_removed():
    a = apply_guardrails(make_assessment(fit_score=40))
    assert a.fit_level == "Weak"
    assert a.recommendation == "Skip"
    assert a.outreach is None


def test_guardrails_contact_without_outreach_fails():
    with pytest.raises(AgentError):
        apply_guardrails(make_assessment(outreach=None))


def test_analyze_sends_expected_request():
    client = fake_client(make_assessment())
    res = CandidateMatchAgent(client=client, model="claude-opus-5").analyze(
        "JD text", "CV text", recruiter_name="Elena", language="English"
    )
    call = client.messages.calls[0]
    assert call["output_format"] is Assessment
    assert call["thinking"] == {"type": "adaptive"}
    assert call["system"][0]["cache_control"] == {"type": "ephemeral"}
    content = call["messages"][0]["content"]
    assert "<job_description>\nJD text" in content and "<candidate_profile>\nCV text" in content
    assert "Elena" in content
    assert res.assessment.recommendation == "Contact"


@pytest.mark.parametrize("stop", ["refusal", "max_tokens"])
def test_analyze_bad_stop_reason(stop):
    with pytest.raises(AgentError):
        CandidateMatchAgent(client=fake_client(make_assessment(), stop)).analyze("JD", "CV")


def test_analyze_rejects_empty_input():
    with pytest.raises(AgentError):
        CandidateMatchAgent(client=fake_client(None)).analyze("JD", "   ")


def test_render():
    md = render_markdown(make_assessment(), record_id=7)
    assert "82%" in md and "Contact" in md and "Hi Alexey" in md and "Record ID: 7" in md
    ranking = render_ranking([("a", make_assessment(fit_score=60)), ("b", make_assessment(fit_score=90))])
    assert ranking.index("90%") < ranking.index("60%")


def test_kpi_funnel():
    t = KpiTracker(":memory:")
    ids = [
        t.log_assessment(make_assessment(), elapsed_sec=30, model="m", recruiter=r)
        for r in ("anna", "anna", "boris", "boris")
    ]
    t.record_outcome(ids[0], hr_screening=True)  # implies contacted/responded/positive
    t.record_outcome(ids[1], responded=True)
    t.record_outcome(ids[2], contacted=True)
    rep = t.report(manual_minutes=20, review_minutes=3, team_size=4)
    assert rep.assessments == 4 and rep.contacted == 3
    assert rep.response_rate == pytest.approx(2 / 3)
    assert rep.positive_response_rate == pytest.approx(1 / 3)
    assert rep.hr_screening_rate == pytest.approx(1 / 3)
    assert rep.adoption_rate == pytest.approx(0.5)
    assert rep.time_saved_hours == pytest.approx((4 * 17 - 2) / 60)
    assert "KPI" in rep.to_markdown()


def test_kpi_unknown_record():
    with pytest.raises(KeyError):
        KpiTracker(":memory:").record_outcome(999, contacted=True)
