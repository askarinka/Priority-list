# Task Duration Fields Design

**Date:** 2026-07-19  
**Status:** Approved

## Overview

Add optional duration fields (hours and minutes) to both `Task` and `WaitingTask` models. Display as a new "Время" column in both task list tables.

---

## Models

Add two fields to both `Task` and `WaitingTask`:

```python
duration_hours = models.IntegerField(default=0)
duration_minutes = models.IntegerField(default=0)
```

- Both fields default to `0` — existing rows will show `0ч 0м` after migration
- Fields are not required (forms may submit `0` if left empty)
- No validation that `minutes < 60` — acceptable for a personal tool

One new migration covers both model changes.

---

## URL Routes and Views

No new endpoints needed. Existing edit/add views already pass all POST fields to the model. The view code for `task_add`, `task_edit`, `waiting_add`, `waiting_edit` must be updated to read and save `duration_hours` and `duration_minutes` from `request.POST`.

---

## UI

### Table layout (updated column widths)

| Column | Width |
|--------|-------|
| Проект | 20% |
| Описание задачи / Причина ожидания | 55% |
| Время | 15% |
| Кнопки | 10% |

### Read row (`_task_row.html`, `_waiting_row.html`)

New `<td>` after description: `{{ task.duration_hours }}ч {{ task.duration_minutes }}м`

### Edit row (`_task_edit_row.html`, `_waiting_edit_row.html`)

New `<td>` with two small number inputs:
```html
<input type="number" name="duration_hours" value="{{ task.duration_hours }}" min="0" style="width:3em"> ч
<input type="number" name="duration_minutes" value="{{ task.duration_minutes }}" min="0" style="width:3em"> м
```

### Add row (`_task_add_row.html`, `_waiting_add_row.html`)

Same two inputs as edit row, both defaulting to `0`.

### Table header (`index.html`, `waiting.html`)

Add `<th>Время</th>` after the description header.

### CSS

Update column width for `td:nth-child(2)` from `70%` to `55%`.  
Add `td:nth-child(3)` (Время cell) styled same as description cell, width `15%`.  
The actions cell shifts to `td:nth-child(4)`.

---

## Scope

- Changes: `models.py`, one migration, `views.py` (4 view functions), 6 partial templates, 2 index templates, `style.css`
- No new URL routes
- No changes to `WaitingTask` waiting list views beyond duration field handling (identical pattern to Task)
