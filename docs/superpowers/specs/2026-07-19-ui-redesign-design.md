# UI Redesign Design

**Date:** 2026-07-19  
**Status:** Approved

## Overview

Replace the current brown table-row UI with a card-based layout, two switchable themes (dark/light), project accent colours, and a 40-hour week marker on the main task list.

No changes to models, migrations, URLs, or views. Frontend only.

---

## Visual Style

### Cards

Each task row becomes a card:

- `border-radius: 14px`
- `border-left: 4px solid <project-colour>`
- `padding: 10px 14px`
- `gap: 6px` between cards (flex column, no table)
- Column proportions preserved: project 20%, description 55%, duration 15%, actions 10%

Column headers remain above the card list as a plain row (no background, uppercase, muted colour).

### Project accent colours

A fixed palette of 8 colours. Colour assigned by `projectName.charCodeAt(0) % 8` — same project always gets the same colour in both themes.

Palette (same hues, different lightness per theme):

| Index | Dark | Light |
|-------|------|-------|
| 0 | `#2563eb` | `#2563eb` |
| 1 | `#0ea5e9` | `#0ea5e9` |
| 2 | `#6366f1` | `#6366f1` |
| 3 | `#8b5cf6` | `#7c3aed` |
| 4 | `#10b981` | `#059669` |
| 5 | `#f59e0b` | `#d97706` |
| 6 | `#ef4444` | `#dc2626` |
| 7 | `#ec4899` | `#db2777` |

Project colour is applied as an inline `style` attribute on the card's `border-left` and on the project name `<span>`. Computed in a `<script>` block in `base.html` via a helper function `projectColour(name)`.

---

## Themes

Two themes implemented as CSS custom properties on `:root` and `[data-theme="light"]`:

| Variable | Dark | Light |
|----------|------|-------|
| `--bg` | `#0f1117` | `#f1f5f9` |
| `--card` | `#1e293b` | `#ffffff` |
| `--card-dim` | `#1a1f2a` | `#f9fafb` |
| `--text` | `#e2e8f0` | `#111827` |
| `--text-muted` | `#475569` | `#9ca3af` |
| `--border` | `#334155` | `#e5e7eb` |
| `--header-bg` | `#0f172a` | `#f9fafb` |
| `--btn-primary` | `#2563eb` | `#111827` |
| `--btn-secondary-bg` | `#1e293b` | `#ffffff` |
| `--btn-secondary-text` | `#94a3b8` | `#6b7280` |
| `--btn-secondary-border` | `#334155` | `#e5e7eb` |

Default theme: dark (no attribute on `<html>`).

### Theme toggle

Button in the toolbar, right-aligned: shows "☀ Светлая" in dark mode, "🌙 Тёмная" in light mode. On click:

1. Toggle `data-theme` attribute on `<html>`
2. Save to `localStorage` key `"theme"`
3. Update button label

On page load, read `localStorage["theme"]` and apply before first paint (inline `<script>` in `<head>`, before CSS).

---

## Week Marker (task list only)

### Behaviour

After rendering the task list, a JavaScript function `updateWeekMarker()` inserts a separator row between the last task whose cumulative `duration_hours + duration_minutes/60` stays ≤ 40 and the first task that would exceed it.

- If all tasks fit in 40h: no marker shown.
- If first task alone exceeds 40h: marker appears before it (all tasks dimmed).
- Tasks below the marker get class `task-dimmed` (`opacity: 0.6`, `pointer-events: none` on action buttons only — drag still works).

### Marker HTML (inserted by JS)

```html
<div class="week-marker">
  <div class="week-marker-line"></div>
  <span class="week-marker-label">⏱ 40ч — конец недели</span>
  <div class="week-marker-line"></div>
</div>
```

### When `updateWeekMarker()` runs

- On `DOMContentLoaded`
- After `htmx:afterSwap` on `#task-tbody` (add/edit/delete)
- After Sortable's `onEnd` callback (reorder)

### Threshold

`const WEEK_HOURS = 40;` — top of the script block in `index.html`. Ready to be replaced by an API value.

### Data attributes

Each task card reads `data-hours` and `data-minutes` attributes (set in `_task_row.html` and `_task_add_row.html`) so JS doesn't parse text content.

---

## Files Changed

| File | Change |
|------|--------|
| `static/tasks/style.css` | Full rewrite: CSS variables, card styles, marker, dimmed state, theme, buttons |
| `templates/tasks/base.html` | Theme init script in `<head>`, theme toggle button in toolbar area, `projectColour()` helper |
| `templates/tasks/index.html` | Remove `<table>/<thead>`, add flex container, add `updateWeekMarker()` script |
| `templates/tasks/waiting.html` | Remove `<table>/<thead>`, add flex container (no marker) |
| `templates/tasks/partials/_task_row.html` | Card markup, `data-hours`/`data-minutes` attributes |
| `templates/tasks/partials/_task_edit_row.html` | Card markup for edit state |
| `templates/tasks/partials/_task_add_row.html` | Card markup for add state, `data-hours="0" data-minutes="0"` |
| `templates/tasks/partials/_waiting_row.html` | Card markup |
| `templates/tasks/partials/_waiting_edit_row.html` | Card markup for edit state |
| `templates/tasks/partials/_waiting_add_row.html` | Card markup for add state |

No changes to: `models.py`, migrations, `views.py`, `urls.py`, `tests.py`.

---

## HTMX and Sortable Migration Notes

The current templates use `<table>/<tbody id="task-tbody">` and `hx-target="closest tr"`. After the redesign:

- `<tbody id="task-tbody">` → `<div id="task-list">` (flex container)
- `hx-target="closest tr"` → `hx-target="closest .task-card"` on all task partials
- `hx-swap="beforeend"` on the add button targets `#task-list`
- Sortable.js `document.getElementById('task-tbody')` → `document.getElementById('task-list')`
- `document.querySelectorAll('#task-tbody tr[data-id]')` → `document.querySelectorAll('#task-list .task-card[data-id]')`

Same changes apply to waiting list: `#waiting-tbody` → `#waiting-list`, `closest tr` → `closest .task-card`.

---

## Scope

- No new URL routes
- No Django test changes (template output tests check for content strings that remain unchanged)
- Sortable.js drag handle and HTMX attributes preserved on all cards
- `data-id` attribute preserved for Sortable reorder
