# UI Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the brown table-row UI with dark/light-switchable card layout and a 40-hour week marker.

**Architecture:** Three-task split: Task 1 rewrites CSS and base.html (theme variables, card styles, JS helpers); Task 2 converts all six partial templates from `<tr>` to `.task-card` divs with updated HTMX targets; Task 3 replaces `<table>` with flex containers in index.html and waiting.html and adds the week marker. No model, migration, view, or URL changes.

**Tech Stack:** Django 6.x, HTMX 2.0.3, Sortable.js 1.15.3, vanilla CSS custom properties, localStorage.

## Global Constraints

- Django test suite `python manage.py test tasks` must stay green (26 tests) after every task — run from `c:\GIT REPOS\Priority-list\priority_list\`
- Card class name: `task-card` (used by HTMX targets and week-marker JS)
- Task list container IDs: `task-list` (index) and `waiting-list` (waiting)
- Theme toggle button ID: `theme-btn`
- localStorage key: `"theme"`, values `"light"` or `"dark"`
- Week-marker threshold constant: `const WEEK_HOURS = 40;`
- data attributes on cards: `data-id`, `data-project`, `data-hours`, `data-minutes`
- CSS custom properties named exactly as in spec (see Task 1)
- No new URL routes; no changes to models.py, views.py, urls.py, tests.py

---

### Task 1: CSS and base.html

**Files:**
- Rewrite: `priority_list/tasks/static/tasks/style.css`
- Modify: `priority_list/tasks/templates/tasks/base.html`

**Interfaces:**
- Produces: CSS custom properties `--bg`, `--card`, `--card-dim`, `--text`, `--text-muted`, `--border`, `--btn-primary-bg`, `--btn-primary-text`, `--btn-secondary-bg`, `--btn-secondary-text`, `--btn-secondary-border`, `--marker-color`
- Produces: JS globals `projectColour(name: string): string`, `applyProjectColours(): void`, `toggleTheme(): void`
- Produces: CSS classes `.task-card`, `.task-card.task-dimmed`, `.task-list`, `.task-list-header`, `.week-marker`, `.week-marker-line`, `.week-marker-label`, `.project-name`, `.description`, `.duration-cell`, `.actions`, `.btn-secondary`, `.theme-toggle`

- [ ] **Step 1: Rewrite style.css**

Replace the full content of `priority_list/tasks/static/tasks/style.css` with:

```css
*, *::before, *::after { box-sizing: border-box; }

:root {
    --bg: #0f1117;
    --card: #1e293b;
    --card-dim: #1a1f2a;
    --text: #e2e8f0;
    --text-muted: #475569;
    --border: #334155;
    --btn-primary-bg: #2563eb;
    --btn-primary-text: #ffffff;
    --btn-secondary-bg: #1e293b;
    --btn-secondary-text: #94a3b8;
    --btn-secondary-border: #334155;
    --marker-color: #ef4444;
}

[data-theme="light"] {
    --bg: #f1f5f9;
    --card: #ffffff;
    --card-dim: #f9fafb;
    --text: #111827;
    --text-muted: #9ca3af;
    --border: #e5e7eb;
    --btn-primary-bg: #111827;
    --btn-primary-text: #ffffff;
    --btn-secondary-bg: #ffffff;
    --btn-secondary-text: #6b7280;
    --btn-secondary-border: #e5e7eb;
    --marker-color: #ef4444;
}

body {
    margin: 0;
    padding: 20px;
    background: var(--bg);
    font-family: Inter, Arial, sans-serif;
    min-height: 100vh;
    color: var(--text);
}

.container {
    max-width: 900px;
    margin: 0 auto;
}

/* Toolbar */
.toolbar {
    display: flex;
    gap: 8px;
    margin-bottom: 20px;
    align-items: center;
}

.toolbar button,
.toolbar a.btn {
    padding: 6px 16px;
    background: var(--btn-primary-bg);
    color: var(--btn-primary-text);
    border: none;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
}

.toolbar .btn-secondary {
    background: var(--btn-secondary-bg);
    color: var(--btn-secondary-text);
    border: 1px solid var(--btn-secondary-border);
}

.toolbar button:hover,
.toolbar a.btn:hover {
    opacity: 0.85;
}

.theme-toggle {
    margin-left: auto;
}

/* Column header row */
.task-list-header {
    display: grid;
    grid-template-columns: 20% 55% 15% 10%;
    padding: 0 14px 8px 18px;
}

.task-list-header span {
    color: var(--text-muted);
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Task list container */
.task-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

/* Task card */
.task-card {
    display: grid;
    grid-template-columns: 20% 55% 15% 10%;
    align-items: center;
    background: var(--card);
    border-radius: 14px;
    padding: 10px 14px;
    border-left: 4px solid var(--border);
    cursor: grab;
    transition: opacity 0.2s;
}

.task-card:active { cursor: grabbing; }

.task-card.task-dimmed {
    opacity: 0.5;
}

.task-card.task-dimmed .actions button {
    pointer-events: none;
}

.project-name {
    font-size: 14px;
    font-weight: 700;
    color: #2563eb;
}

.task-card .description {
    font-size: 14px;
    color: var(--text);
    font-weight: 600;
}

.task-card .duration-cell {
    font-size: 13px;
    color: var(--text-muted);
}

.task-card .actions {
    text-align: right;
}

.task-card .actions button {
    background: transparent;
    border: none;
    cursor: pointer;
    font-size: 16px;
    padding: 4px 6px;
    border-radius: 4px;
    color: var(--text-muted);
}

.task-card .actions button:hover {
    background: rgba(255, 255, 255, 0.12);
    color: var(--text);
}

[data-theme="light"] .task-card .actions button:hover {
    background: rgba(0, 0, 0, 0.07);
}

/* Textarea inside card */
textarea {
    width: 100%;
    background: transparent;
    color: var(--text);
    border: none;
    outline: none;
    font-family: Inter, Arial, sans-serif;
    font-size: 14px;
    font-weight: 600;
    resize: none;
    min-height: 36px;
}

/* Number inputs */
input[type="number"] {
    background: transparent;
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 4px;
    font-size: 13px;
    font-weight: 600;
    padding: 2px 4px;
    width: 3em;
}

/* Week marker */
.week-marker {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px 0;
    pointer-events: none;
}

.week-marker-line {
    flex: 1;
    height: 1px;
    background: var(--marker-color);
    opacity: 0.7;
}

.week-marker-label {
    color: var(--marker-color);
    font-size: 11px;
    font-weight: 700;
    white-space: nowrap;
    letter-spacing: 0.3px;
}
```

- [ ] **Step 2: Update base.html**

Replace the full content of `priority_list/tasks/templates/tasks/base.html` with:

```html
{% load static %}
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}PrioList{% endblock %}</title>
    <script>
        (function () {
            const t = localStorage.getItem('theme');
            if (t === 'light') document.documentElement.dataset.theme = 'light';
        })();
    </script>
    <link rel="stylesheet" href="{% static 'tasks/style.css' %}">
    <script src="https://unpkg.com/htmx.org@2.0.3" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.3/Sortable.min.js"></script>
</head>
<body>
    {% block content %}{% endblock %}
    <script>
        document.addEventListener('htmx:configRequest', function (e) {
            e.detail.headers['X-CSRFToken'] =
                document.cookie.match(/csrftoken=([^;]+)/)?.[1] ?? '';
        });

        function getCsrfToken() {
            return document.cookie.match(/csrftoken=([^;]+)/)?.[1] ?? '';
        }

        const PROJECT_COLOURS_DARK  = ['#2563eb','#0ea5e9','#6366f1','#8b5cf6','#10b981','#f59e0b','#ef4444','#ec4899'];
        const PROJECT_COLOURS_LIGHT = ['#2563eb','#0ea5e9','#6366f1','#7c3aed','#059669','#d97706','#dc2626','#db2777'];

        function projectColour(name) {
            let hash = 0;
            for (let i = 0; i < name.length; i++) hash = (hash * 31 + name.charCodeAt(i)) & 0xffff;
            const palette = document.documentElement.dataset.theme === 'light'
                ? PROJECT_COLOURS_LIGHT : PROJECT_COLOURS_DARK;
            return palette[hash % palette.length];
        }

        function applyProjectColours() {
            document.querySelectorAll('.task-card[data-project]').forEach(function (card) {
                const colour = projectColour(card.dataset.project);
                card.style.borderLeftColor = colour;
                const nameEl = card.querySelector('.project-name');
                if (nameEl) nameEl.style.color = colour;
            });
        }

        function toggleTheme() {
            const html = document.documentElement;
            const goingLight = html.dataset.theme !== 'light';
            if (goingLight) {
                html.dataset.theme = 'light';
                localStorage.setItem('theme', 'light');
            } else {
                delete html.dataset.theme;
                localStorage.setItem('theme', 'dark');
            }
            const btn = document.getElementById('theme-btn');
            if (btn) btn.textContent = html.dataset.theme === 'light' ? '🌙 Тёмная' : '☀ Светлая';
            applyProjectColours();
        }

        document.addEventListener('DOMContentLoaded', function () {
            const btn = document.getElementById('theme-btn');
            if (btn) btn.textContent = document.documentElement.dataset.theme === 'light' ? '🌙 Тёмная' : '☀ Светлая';
            applyProjectColours();
        });

        document.addEventListener('htmx:afterSwap', applyProjectColours);
    </script>
</body>
</html>
```

- [ ] **Step 3: Run tests**

```
cd "c:\GIT REPOS\Priority-list\priority_list" && python manage.py test tasks
```
Expected: `Ran 26 tests in ...s OK`

- [ ] **Step 4: Commit**

```
git -C "c:\GIT REPOS\Priority-list" add priority_list/tasks/static/tasks/style.css priority_list/tasks/templates/tasks/base.html
git -C "c:\GIT REPOS\Priority-list" commit -m "feat: add dark/light theme system and card CSS"
```

---

### Task 2: Partial Templates

**Files:**
- Rewrite: `priority_list/tasks/templates/tasks/partials/_task_row.html`
- Rewrite: `priority_list/tasks/templates/tasks/partials/_task_edit_row.html`
- Rewrite: `priority_list/tasks/templates/tasks/partials/_task_add_row.html`
- Rewrite: `priority_list/tasks/templates/tasks/partials/_waiting_row.html`
- Rewrite: `priority_list/tasks/templates/tasks/partials/_waiting_edit_row.html`
- Rewrite: `priority_list/tasks/templates/tasks/partials/_waiting_add_row.html`

**Interfaces:**
- Consumes: `.task-card`, `.project-name`, `.description`, `.duration-cell`, `.actions` from Task 1
- Produces: `<div class="task-card" data-id="…" data-project="…" data-hours="…" data-minutes="…">` — used by Sortable and week-marker JS in Task 3

- [ ] **Step 1: Rewrite _task_row.html**

Replace full content of `priority_list/tasks/templates/tasks/partials/_task_row.html`:

```html
<div class="task-card" data-id="{{ task.id }}" data-project="{{ task.project }}" data-hours="{{ task.duration_hours }}" data-minutes="{{ task.duration_minutes }}">
    <span class="project-name">{{ task.project }}</span>
    <span class="description">{{ task.description }}</span>
    <span class="duration-cell">{{ task.duration_hours }}ч {{ task.duration_minutes }}м</span>
    <div class="actions">
        <button hx-post="{% url 'task_delete' task.id %}"
                hx-target="closest .task-card"
                hx-swap="outerHTML"
                hx-confirm="Закрыть проект?">✓</button>
        <button hx-get="{% url 'task_edit_form' task.id %}"
                hx-target="closest .task-card"
                hx-swap="outerHTML">✎</button>
    </div>
</div>
```

- [ ] **Step 2: Rewrite _task_edit_row.html**

Replace full content of `priority_list/tasks/templates/tasks/partials/_task_edit_row.html`:

```html
<div class="task-card" data-id="{{ task.id }}" data-project="{{ task.project }}" data-hours="{{ task.duration_hours }}" data-minutes="{{ task.duration_minutes }}">
    <div><textarea name="project">{{ task.project }}</textarea></div>
    <div><textarea name="description">{{ task.description }}</textarea></div>
    <div class="duration-cell">
        <input type="number" name="duration_hours" value="{{ task.duration_hours }}" min="0"> ч
        <input type="number" name="duration_minutes" value="{{ task.duration_minutes }}" min="0"> м
    </div>
    <div class="actions">
        <button hx-post="{% url 'task_edit' task.id %}"
                hx-include="closest .task-card"
                hx-target="closest .task-card"
                hx-swap="outerHTML">✓</button>
        <button hx-get="{% url 'task_row' task.id %}"
                hx-target="closest .task-card"
                hx-swap="outerHTML">✗</button>
    </div>
</div>
```

- [ ] **Step 3: Rewrite _task_add_row.html**

Replace full content of `priority_list/tasks/templates/tasks/partials/_task_add_row.html`:

```html
<div class="task-card" id="task-add-row" data-hours="0" data-minutes="0">
    <div><textarea name="project" placeholder="Проект"></textarea></div>
    <div><textarea name="description" placeholder="Описание задачи"></textarea></div>
    <div class="duration-cell">
        <input type="number" name="duration_hours" value="0" min="0"> ч
        <input type="number" name="duration_minutes" value="0" min="0"> м
    </div>
    <div class="actions">
        <button hx-post="{% url 'task_add' %}"
                hx-include="#task-add-row"
                hx-target="#task-add-row"
                hx-swap="outerHTML">✓</button>
        <button type="button" onclick="this.closest('.task-card').remove()">✗</button>
    </div>
</div>
```

- [ ] **Step 4: Rewrite _waiting_row.html**

Replace full content of `priority_list/tasks/templates/tasks/partials/_waiting_row.html`:

```html
<div class="task-card" data-id="{{ task.id }}" data-project="{{ task.project }}" data-hours="{{ task.duration_hours }}" data-minutes="{{ task.duration_minutes }}">
    <span class="project-name">{{ task.project }}</span>
    <span class="description">{{ task.reason }}</span>
    <span class="duration-cell">{{ task.duration_hours }}ч {{ task.duration_minutes }}м</span>
    <div class="actions">
        <button hx-post="{% url 'waiting_delete' task.id %}"
                hx-target="closest .task-card"
                hx-swap="outerHTML"
                hx-confirm="Удалить из ожидания?">✓</button>
        <button hx-get="{% url 'waiting_edit_form' task.id %}"
                hx-target="closest .task-card"
                hx-swap="outerHTML">✎</button>
    </div>
</div>
```

- [ ] **Step 5: Rewrite _waiting_edit_row.html**

Replace full content of `priority_list/tasks/templates/tasks/partials/_waiting_edit_row.html`:

```html
<div class="task-card" data-id="{{ task.id }}" data-project="{{ task.project }}" data-hours="{{ task.duration_hours }}" data-minutes="{{ task.duration_minutes }}">
    <div><textarea name="project">{{ task.project }}</textarea></div>
    <div><textarea name="reason">{{ task.reason }}</textarea></div>
    <div class="duration-cell">
        <input type="number" name="duration_hours" value="{{ task.duration_hours }}" min="0"> ч
        <input type="number" name="duration_minutes" value="{{ task.duration_minutes }}" min="0"> м
    </div>
    <div class="actions">
        <button hx-post="{% url 'waiting_edit' task.id %}"
                hx-include="closest .task-card"
                hx-target="closest .task-card"
                hx-swap="outerHTML">✓</button>
        <button hx-get="{% url 'waiting_row' task.id %}"
                hx-target="closest .task-card"
                hx-swap="outerHTML">✗</button>
    </div>
</div>
```

- [ ] **Step 6: Rewrite _waiting_add_row.html**

Replace full content of `priority_list/tasks/templates/tasks/partials/_waiting_add_row.html`:

```html
<div class="task-card" id="waiting-add-row" data-hours="0" data-minutes="0">
    <div><textarea name="project" placeholder="Проект"></textarea></div>
    <div><textarea name="reason" placeholder="Причина ожидания"></textarea></div>
    <div class="duration-cell">
        <input type="number" name="duration_hours" value="0" min="0"> ч
        <input type="number" name="duration_minutes" value="0" min="0"> м
    </div>
    <div class="actions">
        <button hx-post="{% url 'waiting_add' %}"
                hx-include="#waiting-add-row"
                hx-target="#waiting-add-row"
                hx-swap="outerHTML">✓</button>
        <button type="button" onclick="this.closest('.task-card').remove()">✗</button>
    </div>
</div>
```

- [ ] **Step 7: Run tests**

```
cd "c:\GIT REPOS\Priority-list\priority_list" && python manage.py test tasks
```
Expected: `Ran 26 tests in ...s OK`

- [ ] **Step 8: Commit**

```
git -C "c:\GIT REPOS\Priority-list" add priority_list/tasks/templates/tasks/partials/
git -C "c:\GIT REPOS\Priority-list" commit -m "feat: convert task and waiting partials to card layout"
```

---

### Task 3: index.html, waiting.html, and Week Marker

**Files:**
- Rewrite: `priority_list/tasks/templates/tasks/index.html`
- Rewrite: `priority_list/tasks/templates/tasks/waiting.html`

**Interfaces:**
- Consumes: `.task-card[data-id][data-hours][data-minutes]` from Task 2
- Consumes: `getCsrfToken()`, `applyProjectColours()`, `toggleTheme()` from Task 1
- Produces: `#task-list` container (Sortable target), `#waiting-list` container, `updateWeekMarker()` global on index page

- [ ] **Step 1: Rewrite index.html**

Replace full content of `priority_list/tasks/templates/tasks/index.html`:

```html
{% extends 'tasks/base.html' %}
{% block title %}PrioList{% endblock %}
{% block content %}
<div class="container">
    <div class="toolbar">
        <button hx-get="{% url 'task_add_form' %}"
                hx-target="#task-list"
                hx-swap="beforeend">+ Добавить</button>
        <a href="{% url 'waiting_index' %}" class="btn btn-secondary">Ожидание</a>
        <button id="theme-btn" class="btn-secondary theme-toggle" onclick="toggleTheme()">☀ Светлая</button>
    </div>
    <div class="task-list-header">
        <span>Проект</span>
        <span>Описание задачи</span>
        <span>Время</span>
        <span></span>
    </div>
    <div class="task-list" id="task-list">
        {% for task in tasks %}
            {% include 'tasks/partials/_task_row.html' %}
        {% endfor %}
    </div>
</div>
<script>
    const WEEK_HOURS = 40;

    function updateWeekMarker() {
        const existing = document.querySelector('.week-marker');
        if (existing) existing.remove();
        document.querySelectorAll('.task-card.task-dimmed').forEach(function (c) {
            c.classList.remove('task-dimmed');
        });

        const cards = Array.from(document.querySelectorAll('#task-list .task-card[data-id]'));
        let total = 0;
        let marked = false;

        for (const card of cards) {
            if (marked) { card.classList.add('task-dimmed'); continue; }
            const h = parseInt(card.dataset.hours || '0', 10);
            const m = parseInt(card.dataset.minutes || '0', 10);
            if (total + h + m / 60 > WEEK_HOURS) {
                const marker = document.createElement('div');
                marker.className = 'week-marker';
                marker.innerHTML =
                    '<div class="week-marker-line"></div>' +
                    '<span class="week-marker-label">⏱ 40ч — конец недели</span>' +
                    '<div class="week-marker-line"></div>';
                card.parentNode.insertBefore(marker, card);
                card.classList.add('task-dimmed');
                marked = true;
            } else {
                total += h + m / 60;
            }
        }
    }

    document.addEventListener('DOMContentLoaded', function () {
        updateWeekMarker();
    });

    document.addEventListener('htmx:afterSwap', function () {
        updateWeekMarker();
    });

    Sortable.create(document.getElementById('task-list'), {
        animation: 150,
        filter: 'input, textarea, button',
        preventOnFilter: false,
        onEnd: function () {
            const cards = document.querySelectorAll('#task-list .task-card[data-id]');
            const formData = new FormData();
            cards.forEach(function (card) { formData.append('ids', card.dataset.id); });
            fetch("{% url 'task_reorder' %}", {
                method: 'POST',
                headers: {'X-CSRFToken': getCsrfToken()},
                body: formData,
            }).then(function () { updateWeekMarker(); }).catch(console.error);
        },
    });
</script>
{% endblock %}
```

- [ ] **Step 2: Rewrite waiting.html**

Replace full content of `priority_list/tasks/templates/tasks/waiting.html`:

```html
{% extends 'tasks/base.html' %}
{% block title %}Ожидание{% endblock %}
{% block content %}
<div class="container">
    <div class="toolbar">
        <button hx-get="{% url 'waiting_add_form' %}"
                hx-target="#waiting-list"
                hx-swap="beforeend">+ Добавить</button>
        <a href="{% url 'index' %}" class="btn btn-secondary">← Назад</a>
        <button id="theme-btn" class="btn-secondary theme-toggle" onclick="toggleTheme()">☀ Светлая</button>
    </div>
    <div class="task-list-header">
        <span>Проект</span>
        <span>Причина ожидания</span>
        <span>Время</span>
        <span></span>
    </div>
    <div class="task-list" id="waiting-list">
        {% for task in tasks %}
            {% include 'tasks/partials/_waiting_row.html' %}
        {% endfor %}
    </div>
</div>
<script>
    Sortable.create(document.getElementById('waiting-list'), {
        animation: 150,
        filter: 'input, textarea, button',
        preventOnFilter: false,
        onEnd: function () {
            const cards = document.querySelectorAll('#waiting-list .task-card[data-id]');
            const formData = new FormData();
            cards.forEach(function (card) { formData.append('ids', card.dataset.id); });
            fetch("{% url 'waiting_reorder' %}", {
                method: 'POST',
                headers: {'X-CSRFToken': getCsrfToken()},
                body: formData,
            }).catch(console.error);
        },
    });
</script>
{% endblock %}
```

- [ ] **Step 3: Run tests**

```
cd "c:\GIT REPOS\Priority-list\priority_list" && python manage.py test tasks
```
Expected: `Ran 26 tests in ...s OK`

- [ ] **Step 4: Smoke test in browser**

```
cd "c:\GIT REPOS\Priority-list\priority_list" && python manage.py runserver
```

Open `http://localhost:8000` and verify:

1. Cards render with rounded corners, coloured left border per project
2. Click "☀ Светлая" → page switches to light theme; click "🌙 Тёмная" → back to dark; refresh → theme persists
3. If total task hours exceed 40h, red marker line appears with correct label; tasks below it are dimmed
4. Click "+ Добавить" → add card appears inline; fill and confirm → saved card appears with correct colour
5. Click ✎ on a card → edit form appears; change values and confirm → card updates
6. Click ✓ to delete → card removed
7. Drag to reorder → order saved; week marker repositions correctly
8. Open `/waiting/` — same card layout and theme toggle; no week marker

- [ ] **Step 5: Commit**

```
git -C "c:\GIT REPOS\Priority-list" add priority_list/tasks/templates/tasks/index.html priority_list/tasks/templates/tasks/waiting.html
git -C "c:\GIT REPOS\Priority-list" commit -m "feat: replace table with card list and add 40h week marker"
```
