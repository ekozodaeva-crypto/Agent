# Как добавить candidate-match-outreach в каталог hr-ai-agents

Все шаги выполняются в браузере: `gitlab.cardpay-test.com / hrprojects / hr-ai-agents`.

| Что | Значение |
|---|---|
| Группа | `recruitment` |
| Имя агента / папки | `candidate-match-outreach` |
| Branch | `add-candidate-match-outreach` |
| Type | `agent + skill` |
| Скилл в репозитории | `.claude/skills/candidate-match-outreach/SKILL.md` |

## Перед началом
- [ ] Принять приглашение в GitLab из письма.
- [ ] Включить VPN. Если GitLab показывает 403, значит, VPN выключен.
- [ ] **Проверить агента самой** (правило каталога: только рабочие агенты). Скопируйте `agent.md` в `C:\Users\<вы>\.claude\agents\candidate-match-outreach.md`, а папку `.claude/skills/candidate-match-outreach` целиком в `C:\Users\<вы>\.claude\skills\`. Перезапустите Claude Code и выполните `/agents`. Затем прогоните агента на одной настоящей вакансии. Если результат полезен, можно добавлять агента в каталог.
- [ ] Если проверка прошла не сегодня, замените дату `2026-09-29` в карточке и в строке каталога на дату проверки.

## Шаги 1–3. Branch
- [ ] **Code → Branches → New branch**
- [ ] Branch name: `add-candidate-match-outreach`, Create from: `main` → **Create branch**
- [ ] Вернитесь на главную страницу репозитория (`hr-ai-agents` в хлебных крошках) и в селекторе веток выберите `add-candidate-match-outreach`, а не `main`.

## Шаги 4–9. Файл агента
- [ ] Откройте папку `recruitment`
- [ ] **+ → New file**
- [ ] Путь (без пробелов в начале): `candidate-match-outreach/agent.md`
- [ ] Вставьте **всё** содержимое файла `recruitment/candidate-match-outreach/agent.md`. Первые строки должны быть `---`, `name:`, `description:`, `tools:`, `---`.
- [ ] Commit message: `add candidate-match-outreach agent`
- [ ] Target branch: `add-candidate-match-outreach`
- [ ] Снимите галочку «Start a new merge request» → **Commit changes**

## Шаги 10–11. Карточка
- [ ] **+ → New file**, путь: `candidate-match-outreach/README.md` (обязательно с папкой!)
- [ ] Проверьте хлебные крошки: `hr-ai-agents / recruitment / candidate-match-outreach /`
- [ ] Откройте в соседней вкладке `_template/README.md` и сверьте заголовки разделов. Если в шаблоне есть раздел, которого нет в карточке, добавьте его. Если разделы названы иначе, переименуйте по шаблону.
- [ ] Вставьте содержимое файла `recruitment/candidate-match-outreach/README.md`
- [ ] Commit message: `add candidate-match-outreach card`, Target branch: ваша ветка → **Commit changes**

## Шаги 12–13. Строка в каталоге
- [ ] В хлебных крошках нажмите `hr-ai-agents` и откройте **корневой** `README.md` (внизу списка файлов)
- [ ] **Edit → Edit single file**
- [ ] Найдите раздел `recruitment` и вставьте строку из файла `catalogue-row.md`: весь блок, если там написано «No agents yet», или только последнюю строку, если таблица уже есть
- [ ] Commit message: `add candidate-match-outreach to catalogue`, Target branch: ваша ветка → **Commit changes**

## Шаги 14–21. Skill
- [ ] Проверьте, что вы в своей ветке: в селекторе должно быть `add-candidate-match-outreach`, а не `main`
- [ ] На главной странице проекта нажмите **Edit → Web IDE**
- [ ] Рядом откройте Проводник с распакованным архивом: папка `.claude\skills\candidate-match-outreach`
- [ ] Перетащите папку `candidate-match-outreach` в дереве Web IDE **на строку `.claude/skills`**. Не на корень репозитория и не внутрь другого скилла.
- [ ] Раскройте папку и проверьте содержимое: там только `SKILL.md`. Никаких выгрузок и данных кандидатов.
- [ ] Откройте панель **Source Control** (иконка с веткой). Должен быть **1 файл** с пометкой A: `.claude/skills/candidate-match-outreach/SKILL.md`
- [ ] Commit message: `add candidate-match-outreach skill`
- [ ] На кнопке должно быть написано `Commit to 'add-candidate-match-outreach'`. Если там `main`, остановитесь. Если всё верно, нажмите кнопку.
- [ ] Нажимайте «Назад» в браузере, пока не вернётесь на страницу проекта. Второй merge request для скилла не создавайте.

## Шаги 22–24. Merge request
- [ ] **Code → Merge requests → New merge request** (или кнопка в зелёном баннере)
- [ ] From `add-candidate-match-outreach` into `main`
- [ ] Title: `Add candidate-match-outreach to the catalogue`
- [ ] Assignees: **Assign to me**
- [ ] Delete source branch: оставить галочку. Squash commits: без галочки.
- [ ] **Create merge request**
- [ ] Во вкладке **Changes** должно быть 4 файла: `agent.md`, `README.md` (карточка), корневой `README.md` и `.claude/skills/candidate-match-outreach/SKILL.md`. Проверьте, что там нет реальных имён, токенов и ключей, а также оставшихся `<placeholder>`.
- [ ] Merge делает владелец репозитория (Olena Sencha).

## Если что-то пошло не так
| Что видно | Что делать |
|---|---|
| 403 Forbidden | Включить VPN |
| «A branch already exists» | Вы были в `main`. Переключитесь на свою ветку и повторите |
| Commit refused | В Target branch указан `main`. Поменяйте на свою ветку |
| Агент запускается, но скилл не находится | Папка скилла лежит не в `.claude/skills/` |
| Ссылка в таблице не открывается | Карточка лежит не в папке агента, или в имени папки есть пробелы |
