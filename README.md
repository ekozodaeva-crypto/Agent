# Candidate Match & Outreach Agent

AI-агент для IT-рекрутеров на базе Claude. Сравнивает вакансию (JD) с профилем кандидата и за один вызов возвращает:

- **Fit score 0–100%** и **fit level** (Strong ≥ 75 / Medium 55–74 / Weak < 55)
- **Must-have match** — каждое обязательное требование: ✅ met / 🟡 partial / ❌ not met / ❔ unknown + подтверждение из профиля
- **Strengths, Gaps, Risks, Missing information** (что уточнить при первом контакте)
- **Рекомендацию Contact / Skip** с обоснованием
- Для Contact — **personalization hook, selling point, tone of voice, готовое сообщение** (60–120 слов) и follow-up

## Как это работает

- Один вызов Claude API со **structured outputs** (Pydantic-схема `Assessment`), поэтому формат ответа всегда одинаковый.
- Единая рубрика оценки в системном промпте (must-have 50 · опыт/сеньорность 20 · стек/домен 15 · траектория/мотивация 15) — оценки согласованы между кандидатами и рекрутерами.
- Guardrails в коде: fit level всегда вычисляется из score, Weak → всегда Skip, outreach только для Contact.
- Правила fairness: агент не использует и не упоминает возраст, пол, национальность, семейное положение, здоровье, фото и т.п. Текст JD и профиля считается данными, а не инструкциями.
- Системный промпт кешируется (prompt caching) — дешевле при пакетной обработке.

## Установка

```bash
pip install -e ".[dev]"
export ANTHROPIC_API_KEY=sk-ant-...
```

## Использование

```bash
# Один кандидат
candidate-agent analyze --jd examples/jd_senior_backend.md \
  --profile examples/candidate_strong.md \
  --company examples/company_context.md --recruiter "Elena"

# Несколько кандидатов → карточки + shortlist, отсортированный по score
candidate-agent analyze --jd examples/jd_senior_backend.md \
  --profile examples/candidate_strong.md --profile examples/candidate_weak.md

# Аутрич на английском, анализ на русском, канал Telegram
candidate-agent analyze --jd jd.md --profile cv.md --outreach-lang English --channel Telegram

# JSON для интеграции с ATS
candidate-agent analyze --jd jd.md --profile cv.md --json
```

Опции: `--lang` (язык анализа, по умолчанию Russian), `--model` (по умолчанию `claude-opus-5`, env `CANDIDATE_AGENT_MODEL`), `--effort low|medium|high|xhigh|max` (по умолчанию `high`), `--no-log`.

Из Python:

```python
from candidate_agent import CandidateMatchAgent

res = CandidateMatchAgent().analyze(jd_text, cv_text, recruiter_name="Elena")
print(res.assessment.fit_score, res.assessment.recommendation)
print(res.assessment.outreach.message if res.assessment.outreach else "Skip")
```

## KPI

Каждая оценка логируется в SQLite (`~/.candidate_agent/kpi.db`, env `CANDIDATE_AGENT_DB`) с ID записи. Рекрутер отмечает результат воронки:

```bash
candidate-agent outcome 12 --contacted
candidate-agent outcome 12 --responded
candidate-agent outcome 12 --positive
candidate-agent outcome 12 --hr-screening   # более поздний этап автоматически отмечает предыдущие

candidate-agent kpi --team-size 8 --manual-min 20 --review-min 3 --since 2026-09-01
```

| KPI | Как считается |
|---|---|
| Time saved on assessment & outreach | `оценок × (ручное время − время ревью) − время работы агента` (baseline и ревью настраиваются) |
| Candidate response rate | ответили / написали |
| Positive response rate | позитивно ответили / написали |
| % contacted → HR screening | дошли до HR-скрининга / написали |
| Recruiter adoption rate | рекрутеры, использовавшие агента / размер команды |

## Структура

```
candidate_agent/
  schema.py   # Pydantic-схема результата
  prompts.py  # системный промпт с рубрикой, fairness и правилами аутрича
  agent.py    # вызов Claude + guardrails
  render.py   # Markdown-карточка и shortlist
  kpi.py      # SQLite-трекер воронки и KPI
  cli.py      # CLI: analyze / outcome / kpi
examples/     # пример вакансии, контекста компании и двух кандидатов
tests/        # unit-тесты (без обращения к API)
```

```bash
pytest -q
```
