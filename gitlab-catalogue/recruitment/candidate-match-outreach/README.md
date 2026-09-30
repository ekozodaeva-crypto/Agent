# candidate-match-outreach

**Owner:** Elena Kozodaeva, e.kozodaeva@unlimit.com
**Group:** recruitment
**Type:** agent
**Status:** working
**Last verified:** 2026-09-30

## ✅ This agent only drafts — it never sends anything

It reads the job description and candidate profiles you give it and writes an assessment and a draft message. Nothing is sent to candidates, Slack, email or the ATS. You read the draft and decide whether to send it.

## What it does

Compares a job description with one or more candidate profiles (CV, LinkedIn, GitHub, recruiter notes) and gives a fit score 0–100%, a fit level (Strong / Medium / Weak), a must-have check, strengths, gaps, risks, missing information and a Contact / Skip recommendation.

For candidates worth contacting it also drafts a personalization hook, a selling point, a tone of voice, a ready-to-send outreach message and a follow-up. Given several candidates for one vacancy, it adds a shortlist sorted by score.

Every candidate is scored with the same rubric: must-haves 50, experience and seniority 20, stack and domain 15, trajectory and motivation 15. The level always follows the score: Strong ≥ 75, Medium 55–74, Weak < 55. Weak is always Skip.

## What it needs

**Connectors:** none. Tools: `Read`, `Glob`, `Grep` — only to read CV / JD files you point it at.

**Access needed:** none beyond Claude Code. You paste the vacancy and the profile into the chat, or give the path to local files.

## Where the code lives

- `recruitment/candidate-match-outreach/agent.md` — the whole agent in one file: assessment rubric, outreach rules and output template. No skill folder is needed.

## How to install

1. Copy `recruitment/candidate-match-outreach/agent.md` into your own `C:\Users\<your-user>\.claude\agents\` folder and rename it to `candidate-match-outreach.md`.
2. No connector IDs to replace — the `tools:` line uses only built-in tools (`Read`, `Glob`, `Grep`).
3. Restart Claude Code and run `/agents` to confirm it appears.

## How to use

Ask in Claude Code, for example:

```text
Use candidate-match-outreach. Assess the candidate against the vacancy.
Channel: LinkedIn, sign as Recruiter A.
Vacancy: <JD text or path to file>
Candidate: <CV text or path to file>
```

Optional: company context (product, team, stack, format, relocation, hiring stages), outreach language, several candidates at once.

## Example run

Fictional candidate; names replaced with John Smith / Recruiter A.

**Prompt**

```text
Оцени кандидата под вакансию. Канал — LinkedIn, подпись — Recruiter A.

Вакансия: Senior Backend Engineer (Go) — Payments Platform. Remote (CET ±2) or hybrid
in Limassol / Warsaw. Must-have: 5+ years backend; Go in production 2+ years;
PostgreSQL schema design and query optimization; Kafka or other brokers; English B2+.
Nice-to-have: fintech/payments, Kubernetes, observability, PCI DSS.
Tasks: payment routing service 5k+ TPS, end-to-end ownership incl. on-call,
architecture of the new processing core.
Company: international payments company, own processing; product team of 8 engineers;
Go, PostgreSQL, Kafka, Kubernetes, gRPC; relocation to Cyprus or Poland; hiring
process intro → tech → system design → offer, ~2 weeks.

Кандидат: John Smith — Senior Software Engineer, Belgrade, English C1.
2021–now Senior Backend Engineer, card issuing fintech: Go, PostgreSQL, Kafka, k8s;
designed transaction authorization service (3k TPS, p99 < 40ms); led migration from
monolith to 12 services. 2018–2021 Backend Developer, e-commerce: Python, Go,
PostgreSQL, RabbitMQ. 2016–2018 Junior Developer, PHP.
Open source: maintainer of go-idempotency (1.2k stars). Talk: "Exactly-once in
payments: myths and practice", GopherCon EU 2024.
```

**Answer**

````markdown
# John Smith → Senior Backend Engineer (Go), Payments Platform

**Fit: 88% · 🟢 Strong** · **Рекомендация: 📨 Contact**

Сильное попадание: 5 лет Go в продакшене в платёжном домене, высоконагруженный сервис
авторизации транзакций и опыт распила монолита. Не подтверждены только глубина работы
с PostgreSQL и опыт с PCI DSS / observability — это можно уточнить на первом звонке.

## Must-have match
| | Требование | Подтверждение |
|---|---|---|
| ✅ | 5+ лет backend | Backend с 2018 (~8 лет), до этого 2 года PHP |
| ✅ | Go в продакшене 2+ года | Go с 2018, основной язык с 2021 |
| 🟡 | PostgreSQL: проектирование схем, оптимизация | PostgreSQL в двух ролях, но про проектирование и оптимизацию ничего не сказано |
| ✅ | Kafka или другие брокеры | Kafka (текущая роль), RabbitMQ (2018–2021) |
| ✅ | English B2+ | C1 |

## Strengths
- Сервис авторизации транзакций на 3k TPS с p99 < 40ms — близко к целевым 5k+ TPS
- Руководил миграцией монолита на 12 сервисов — релевантно для нового processing core
- Card issuing fintech — домен платежей, nice-to-have закрыт
- Kubernetes в текущем стеке
- Maintainer go-idempotency (1.2k stars) и доклад на GopherCon EU про exactly-once в платежах
- Belgrade — часовой пояс CET, подходит под remote CET ±2

## Gaps
- Нет подтверждения проектирования схем и оптимизации запросов в PostgreSQL
- Не указаны observability (Prometheus, Grafana, OpenTelemetry) и PCI DSS

## Risks
- 5 лет в текущей компании на senior-позиции — мотивация к смене неизвестна
- Сильный публичный профиль (OSS, конференции) — вероятно, много входящих предложений
- Ожидания по компенсации неизвестны

## Missing information
- Мотивация сменить работу и что важно в следующей роли
- Ожидания по компенсации и срок выхода
- Опыт с PCI DSS и observability
- Готовность к on-call
- Предпочтение: remote или hybrid с релокацией

## Рекомендация: Contact
Все must-have закрыты или частично закрыты, домен и масштаб задач совпадают. Пробелы
уточняются на intro-звонке.

## Outreach
**Personalization hook:** go-idempotency и доклад про exactly-once в платежах — ровно та проблема, с которой работает команда
**Selling point:** построить с нуля payment routing на 5k+ TPS и влиять на архитектуру нового processing core в команде из 8 инженеров, на знакомом стеке
**Tone of voice:** на равных, коротко и технично — как инженер инженеру, без HR-клише
**Тема / первая строка:** Payment routing at 5k+ TPS — and your go-idempotency

```text
Hi John,

Your go-idempotency library caught my eye — idempotency is exactly the kind of problem
our payments team deals with every day. We're hiring a Senior Backend Engineer (Go) to
build a payment routing service at 5k+ TPS and shape the architecture of our new
processing core. The stack will feel familiar: Go, PostgreSQL, Kafka, Kubernetes, gRPC,
in a product team of 8 engineers with direct say in design. Remote in CET or hybrid in
Limassol / Warsaw, with relocation support if you want it.

Would you be open to a 20-minute intro call next week?

Best,
Recruiter A
```

**Follow-up (через 3–5 дней):**
```text
Hi John, one more detail: since we're building a new processing core, the exactly-once
questions from your GopherCon talk are very much part of the job. Our process is short —
four steps, about two weeks. Happy to walk you through the scope whenever suits you.
```

---
`KPI | 2026-09-29 | Senior Backend Engineer (Go) | John Smith | 88 | Strong | Contact`
````

## Guardrails

- Only drafts; never sends messages or writes to any system.
- Never uses or mentions age, gender, ethnicity, nationality, religion, marital status, children, health, disability or appearance.
- Treats the JD and CV as data: instructions hidden inside a CV are ignored and flagged in Risks.
- Invents nothing: missing data is marked ❔ unknown, not ❌ not met.
- Same rubric for every candidate; Weak is always Skip.

## Known limitations

- Quality depends on how complete the profile is — a short LinkedIn headline gives mostly ❔ unknown.
- Does not look candidates up on the internet or in Lever; it only uses what you give it.
- KPIs are not tracked automatically: paste the `KPI | ...` line into your tracker and mark contacted / replied / positive / HR screening there.
- Candidate profiles are sent to Claude — use only for recruiting work, and do not paste in extra personal data (ID numbers, salary slips).
- Always read the draft before sending; the agent can misread a CV.

## Changelog

| Date | Change | Author |
|---|---|---|
| 2026-09-30 | Added to the hr-ai-agents catalogue as a single-file agent: assessment (fit score, fit level, must-have match, strengths, gaps, risks, missing information, Contact / Skip) and outreach draft (hook, selling point, tone of voice, message, follow-up) | e.kozodaeva |
