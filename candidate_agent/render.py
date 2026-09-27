"""Human-readable (Markdown) rendering of an assessment."""

from __future__ import annotations

from .schema import Assessment

STATUS_ICON = {"met": "✅", "partial": "🟡", "not_met": "❌", "unknown": "❔"}
LEVEL_ICON = {"Strong": "🟢", "Medium": "🟡", "Weak": "🔴"}


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {i}" for i in items) if items else "- —"


def render_markdown(a: Assessment, record_id: int | None = None) -> str:
    name = a.candidate_name or "Candidate"
    lines = [
        f"# {name} → {a.role_title}",
        "",
        f"**Fit: {a.fit_score}% · {LEVEL_ICON[a.fit_level]} {a.fit_level}** · "
        f"**Recommendation: {'📨 Contact' if a.recommendation == 'Contact' else '⏭️ Skip'}**",
    ]
    if record_id is not None:
        lines.append(f"_Record ID: {record_id}_")
    lines += [
        "",
        a.summary,
        "",
        "## Must-have match",
        "| | Requirement | Evidence |",
        "|---|---|---|",
    ]
    for m in a.must_have_match:
        lines.append(f"| {STATUS_ICON[m.status]} | {m.requirement} | {m.evidence} |")
    lines += [
        "",
        "## Strengths",
        _bullets(a.strengths),
        "",
        "## Gaps",
        _bullets(a.gaps),
        "",
        "## Risks",
        _bullets(a.risks),
        "",
        "## Missing information",
        _bullets(a.missing_information),
        "",
        f"## Recommendation: {a.recommendation}",
        a.recommendation_reason,
    ]
    if a.outreach:
        o = a.outreach
        lines += [
            "",
            "## Outreach",
            f"**Personalization hook:** {o.personalization_hook}",
            "",
            f"**Selling point:** {o.selling_point}",
            "",
            f"**Tone of voice:** {o.tone_of_voice}",
            "",
            f"**Subject:** {o.subject}",
            "",
            "```text",
            o.message,
            "```",
            "",
            "**Follow-up (3–5 days):**",
            "```text",
            o.follow_up,
            "```",
        ]
    return "\n".join(lines) + "\n"


def render_ranking(rows: list[tuple[str, Assessment]]) -> str:
    rows = sorted(rows, key=lambda r: r[1].fit_score, reverse=True)
    out = ["# Shortlist", "", "| # | Candidate | Score | Level | Recommendation |", "|---|---|---|---|---|"]
    for i, (src, a) in enumerate(rows, 1):
        out.append(
            f"| {i} | {a.candidate_name or src} | {a.fit_score}% | {a.fit_level} | {a.recommendation} |"
        )
    return "\n".join(out) + "\n"
