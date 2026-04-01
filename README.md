# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

---

## Features

- **Owner & pet management** — register an owner and any number of pets (name, species, age).
- **Task scheduling** — add care tasks with time (HH:MM), duration, priority, frequency, and due date.
- **Sorting by time** — all tasks are displayed in chronological order using a `sort_by_time()` method that sorts HH:MM strings lexicographically.
- **Filtering** — filter the schedule by pet name and/or completion status (pending / completed / all).
- **Conflict warnings** — the scheduler detects when two tasks for the same pet are booked at the exact same time and surfaces a warning in the UI.
- **Daily recurrence** — marking a `daily` or `weekly` task complete automatically creates the next occurrence (using Python's `timedelta`) without any manual work.
- **Today's view** — a dedicated `get_todays_schedule()` method returns only incomplete tasks whose due date is today, sorted by time.

---

## Smarter Scheduling

The `Scheduler` class (in `pawpal_system.py`) adds four algorithmic features beyond basic CRUD:

| Feature | Method | How it works |
|---|---|---|
| Chronological sorting | `sort_by_time()` | `sorted()` with a lambda key on the HH:MM string |
| Flexible filtering | `filter_tasks(pet_name, completed)` | List comprehension with optional predicates |
| Recurring tasks | `mark_task_complete(pet, task)` | Calls `task.next_occurrence()` and appends the result to the pet |
| Conflict detection | `detect_conflicts()` | Iterates each pet's tasks, tracking seen times in a dict |

**Tradeoff:** Conflict detection checks for exact time matches only, not overlapping durations. This keeps the logic simple and fast while catching the most common scheduling mistake.

---

## Testing PawPal+

### Run the tests

```bash
python -m pytest
```

### What the tests cover

| Test | Behaviour verified |
|---|---|
| `test_mark_complete_changes_status` | `mark_complete()` flips `is_complete` |
| `test_add_task_increases_count` | `add_task()` grows the task list |
| `test_once_task_has_no_next_occurrence` | One-off tasks don't recur |
| `test_sort_by_time_returns_chronological_order` | Tasks sorted regardless of insertion order |
| `test_daily_task_creates_next_occurrence` | Daily recurrence adds task for tomorrow |
| `test_weekly_task_creates_next_occurrence_seven_days_later` | Weekly recurrence adds task in 7 days |
| `test_conflict_detection_flags_same_time` | Two tasks at same time → one warning |
| `test_no_conflict_when_times_differ` | Different times → no warnings |
| `test_filter_by_pet_name` | Filter returns only named pet's tasks |
| `test_filter_by_completion_status` | Filter excludes completed/pending correctly |
| `test_pet_with_no_tasks_has_empty_schedule` | Empty pet → empty results, no crash |

**Confidence level: ★★★★☆** — all 11 tests pass; duration-overlap and midnight-spanning edge cases are not yet covered.
