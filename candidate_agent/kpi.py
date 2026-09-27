"""Local KPI tracking (SQLite).

Every assessment is logged; the recruiter later records the funnel outcome
(contacted -> responded -> positive -> HR screening). KPIs are computed from it.
"""

from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .schema import Assessment

DEFAULT_DB = Path(os.environ.get("CANDIDATE_AGENT_DB", Path.home() / ".candidate_agent" / "kpi.db"))

OUTCOME_FIELDS = ("contacted", "responded", "positive", "hr_screening")

SCHEMA = """
CREATE TABLE IF NOT EXISTS assessments (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at    TEXT NOT NULL,
    recruiter     TEXT,
    role_title    TEXT,
    candidate     TEXT,
    fit_score     INTEGER,
    fit_level     TEXT,
    recommendation TEXT,
    elapsed_sec   REAL,
    model         TEXT,
    contacted     INTEGER NOT NULL DEFAULT 0,
    responded     INTEGER NOT NULL DEFAULT 0,
    positive      INTEGER NOT NULL DEFAULT 0,
    hr_screening  INTEGER NOT NULL DEFAULT 0
);
"""


@dataclass
class KpiReport:
    assessments: int
    recommended_contact: int
    contacted: int
    responded: int
    positive: int
    hr_screening: int
    time_saved_hours: float
    avg_agent_sec: float
    response_rate: float | None
    positive_response_rate: float | None
    hr_screening_rate: float | None
    active_recruiters: int
    adoption_rate: float | None

    def to_markdown(self) -> str:
        def pct(v: float | None) -> str:
            return "n/a" if v is None else f"{v:.0%}"

        return "\n".join(
            [
                "# Candidate Match & Outreach Agent — KPI",
                "",
                "| KPI | Value |",
                "|---|---|",
                f"| Time saved on assessment & outreach | {self.time_saved_hours:.1f} h "
                f"({self.assessments} assessments, avg agent time {self.avg_agent_sec:.0f}s) |",
                f"| Candidate response rate | {pct(self.response_rate)} ({self.responded}/{self.contacted}) |",
                f"| Positive response rate | {pct(self.positive_response_rate)} ({self.positive}/{self.contacted}) |",
                f"| Contacted → HR screening | {pct(self.hr_screening_rate)} ({self.hr_screening}/{self.contacted}) |",
                f"| Recruiter adoption rate | {pct(self.adoption_rate)} ({self.active_recruiters} active recruiters) |",
                "",
                f"Recommended to contact: {self.recommended_contact}/{self.assessments}",
            ]
        ) + "\n"


class KpiTracker:
    def __init__(self, db_path: Path | str = DEFAULT_DB):
        self.db_path = Path(db_path)
        if str(self.db_path) != ":memory:":
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)

    def log_assessment(
        self, a: Assessment, *, elapsed_sec: float, model: str, recruiter: str | None
    ) -> int:
        cur = self.conn.execute(
            "INSERT INTO assessments (created_at, recruiter, role_title, candidate, fit_score, fit_level,"
            " recommendation, elapsed_sec, model) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
                recruiter,
                a.role_title,
                a.candidate_name,
                a.fit_score,
                a.fit_level,
                a.recommendation,
                elapsed_sec,
                model,
            ),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def record_outcome(self, record_id: int, **flags: bool) -> None:
        """Set funnel flags. Later stages imply earlier ones (positive => responded => contacted)."""
        unknown = set(flags) - set(OUTCOME_FIELDS)
        if unknown:
            raise ValueError(f"Unknown outcome fields: {sorted(unknown)}")
        if flags.get("hr_screening"):
            flags["positive"] = True
        if flags.get("positive"):
            flags["responded"] = True
        if flags.get("responded"):
            flags["contacted"] = True
        if not flags:
            return
        sets = ", ".join(f"{k} = ?" for k in flags)
        cur = self.conn.execute(
            f"UPDATE assessments SET {sets} WHERE id = ?", (*map(int, flags.values()), record_id)
        )
        if cur.rowcount == 0:
            raise KeyError(f"No assessment with id {record_id}")
        self.conn.commit()

    def report(
        self,
        *,
        manual_minutes: float = 20.0,
        review_minutes: float = 3.0,
        team_size: int | None = None,
        since: str | None = None,
    ) -> KpiReport:
        """
        manual_minutes - baseline time a recruiter spends to assess a profile and write outreach by hand;
        review_minutes - time the recruiter still spends reviewing the agent output;
        team_size      - number of recruiters in the team (for adoption rate).
        """
        where, params = ("WHERE created_at >= ?", (since,)) if since else ("", ())
        r = self.conn.execute(
            f"""SELECT COUNT(*) n,
                   COALESCE(SUM(recommendation = 'Contact'), 0) rec,
                   COALESCE(SUM(contacted), 0) c, COALESCE(SUM(responded), 0) r,
                   COALESCE(SUM(positive), 0) p, COALESCE(SUM(hr_screening), 0) h,
                   COALESCE(SUM(elapsed_sec), 0) t,
                   COUNT(DISTINCT recruiter) rc
                FROM assessments {where}""",
            params,
        ).fetchone()
        n, contacted = r["n"], r["c"]
        agent_minutes = r["t"] / 60
        saved = max(0.0, n * (manual_minutes - review_minutes) - agent_minutes)

        def rate(x: int) -> float | None:
            return x / contacted if contacted else None

        return KpiReport(
            assessments=n,
            recommended_contact=r["rec"],
            contacted=contacted,
            responded=r["r"],
            positive=r["p"],
            hr_screening=r["h"],
            time_saved_hours=saved / 60,
            avg_agent_sec=(r["t"] / n) if n else 0.0,
            response_rate=rate(r["r"]),
            positive_response_rate=rate(r["p"]),
            hr_screening_rate=rate(r["h"]),
            active_recruiters=r["rc"],
            adoption_rate=(r["rc"] / team_size) if team_size else None,
        )
