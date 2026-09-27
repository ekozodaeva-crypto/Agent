"""Command line interface.

    candidate-agent analyze --jd jd.md --profile cv1.md [--profile cv2.md ...]
    candidate-agent outcome 12 --contacted --responded
    candidate-agent kpi --team-size 8
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import anthropic

from .agent import DEFAULT_EFFORT, DEFAULT_MODEL, AgentError, CandidateMatchAgent
from .kpi import DEFAULT_DB, KpiTracker
from .render import render_markdown, render_ranking


def _read(path: str) -> str:
    return sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")


def cmd_analyze(args: argparse.Namespace) -> int:
    agent = CandidateMatchAgent(model=args.model, effort=args.effort)
    tracker = None if args.no_log else KpiTracker(args.db)
    jd = _read(args.jd)
    company = _read(args.company) if args.company else None

    results = []
    for profile_path in args.profile:
        try:
            res = agent.analyze(
                jd,
                _read(profile_path),
                company_context=company,
                recruiter_name=args.recruiter,
                language=args.lang,
                outreach_language=args.outreach_lang,
                channel=args.channel,
            )
        except (AgentError, anthropic.APIError) as e:
            print(f"[{profile_path}] error: {e}", file=sys.stderr)
            continue
        record_id = (
            tracker.log_assessment(
                res.assessment, elapsed_sec=res.elapsed_sec, model=res.model, recruiter=args.recruiter
            )
            if tracker
            else None
        )
        results.append((profile_path, res, record_id))

        if args.json:
            print(json.dumps({"record_id": record_id, **res.assessment.model_dump()}, ensure_ascii=False, indent=2))
        else:
            print(render_markdown(res.assessment, record_id))
            print(f"_{res.model} · {res.elapsed_sec:.1f}s · {res.input_tokens}→{res.output_tokens} tokens_\n")

    if len(results) > 1 and not args.json:
        print(render_ranking([(p, r.assessment) for p, r, _ in results]))
    return 0 if results else 1


def cmd_outcome(args: argparse.Namespace) -> int:
    flags = {k: True for k in ("contacted", "responded", "positive", "hr_screening") if getattr(args, k)}
    if not flags:
        print("Nothing to record: pass --contacted / --responded / --positive / --hr-screening", file=sys.stderr)
        return 2
    try:
        KpiTracker(args.db).record_outcome(args.record_id, **flags)
    except KeyError as e:
        print(e.args[0], file=sys.stderr)
        return 1
    print(f"Record {args.record_id} updated: {', '.join(flags)}")
    return 0


def cmd_kpi(args: argparse.Namespace) -> int:
    report = KpiTracker(args.db).report(
        manual_minutes=args.manual_min,
        review_minutes=args.review_min,
        team_size=args.team_size,
        since=args.since,
    )
    print(json.dumps(report.__dict__, indent=2) if args.json else report.to_markdown())
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="candidate-agent", description="Candidate Match & Outreach Agent")
    p.add_argument("--db", default=str(DEFAULT_DB), help="SQLite file for KPI tracking")
    sub = p.add_subparsers(dest="command", required=True)

    a = sub.add_parser("analyze", help="Assess candidate(s) against a job and draft outreach")
    a.add_argument("--jd", required=True, help="Job description file ('-' for stdin)")
    a.add_argument("--profile", required=True, action="append", help="Candidate profile file (repeatable)")
    a.add_argument("--company", help="Company / team context file (selling points, benefits, format)")
    a.add_argument("--recruiter", help="Recruiter name (signature + adoption KPI)")
    a.add_argument("--lang", default="Russian", help="Analysis language (default: Russian)")
    a.add_argument("--outreach-lang", help="Outreach language (default: same as --lang)")
    a.add_argument("--channel", default="LinkedIn InMail", help="Outreach channel (LinkedIn InMail, Telegram, email)")
    a.add_argument("--model", default=DEFAULT_MODEL)
    a.add_argument("--effort", default=DEFAULT_EFFORT, choices=["low", "medium", "high", "xhigh", "max"])
    a.add_argument("--json", action="store_true", help="Print raw JSON")
    a.add_argument("--no-log", action="store_true", help="Do not log to the KPI database")
    a.set_defaults(func=cmd_analyze)

    o = sub.add_parser("outcome", help="Record funnel outcome for an assessment")
    o.add_argument("record_id", type=int)
    o.add_argument("--contacted", action="store_true")
    o.add_argument("--responded", action="store_true")
    o.add_argument("--positive", action="store_true")
    o.add_argument("--hr-screening", dest="hr_screening", action="store_true")
    o.set_defaults(func=cmd_outcome)

    k = sub.add_parser("kpi", help="Show KPI report")
    k.add_argument("--manual-min", type=float, default=20.0, help="Baseline manual minutes per candidate")
    k.add_argument("--review-min", type=float, default=3.0, help="Recruiter review minutes per agent output")
    k.add_argument("--team-size", type=int, help="Recruiters in the team (for adoption rate)")
    k.add_argument("--since", help="ISO date, e.g. 2026-09-01")
    k.add_argument("--json", action="store_true")
    k.set_defaults(func=cmd_kpi)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
