"""
Automated test suite for PawPal+ core logic.

Run with:  python -m pytest
"""

import pytest
from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


# ---------------------------------------------------------------------------
# Task tests
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    """Calling mark_complete() should flip is_complete to True."""
    task = Task("Walk", "08:00", 30, "high")
    assert not task.is_complete
    task.mark_complete()
    assert task.is_complete


def test_add_task_increases_count():
    """Adding a task to a Pet should increase its task count by 1."""
    pet = Pet("Mochi", "dog", 3)
    assert len(pet.tasks) == 0
    pet.add_task(Task("Walk", "08:00", 30, "high"))
    assert len(pet.tasks) == 1


def test_once_task_has_no_next_occurrence():
    """A one-off task should return None from next_occurrence()."""
    task = Task("Vet visit", "10:00", 60, "high", frequency="once")
    assert task.next_occurrence() is None


# ---------------------------------------------------------------------------
# Sorting tests
# ---------------------------------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    """Tasks added out of order should be returned sorted by HH:MM time."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Evening walk",    "18:00", 30, "high"))
    pet.add_task(Task("Morning feeding", "07:30", 10, "high"))
    pet.add_task(Task("Midday meds",     "12:00",  5, "medium"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    times = [t.time for _, t in scheduler.sort_by_time()]
    assert times == sorted(times)


# ---------------------------------------------------------------------------
# Recurring task tests
# ---------------------------------------------------------------------------

def test_daily_task_creates_next_occurrence():
    """Completing a daily task should add a new task due tomorrow."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", 3)
    today = date.today()
    task = Task("Daily walk", "08:00", 30, "high", "daily", due_date=today)
    pet.add_task(task)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    scheduler.mark_task_complete(pet, task)

    assert task.is_complete
    assert len(pet.tasks) == 2
    new_task = pet.tasks[1]
    assert new_task.due_date == today + timedelta(days=1)
    assert not new_task.is_complete


def test_weekly_task_creates_next_occurrence_seven_days_later():
    """Completing a weekly task should add a new task due in 7 days."""
    owner = Owner("Jordan")
    pet = Pet("Whiskers", "cat", 5)
    today = date.today()
    task = Task("Flea treatment", "09:00", 10, "medium", "weekly", due_date=today)
    pet.add_task(task)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    scheduler.mark_task_complete(pet, task)

    assert len(pet.tasks) == 2
    assert pet.tasks[1].due_date == today + timedelta(weeks=1)


# ---------------------------------------------------------------------------
# Conflict detection tests
# ---------------------------------------------------------------------------

def test_conflict_detection_flags_same_time():
    """Two tasks for the same pet at the same time should produce one warning."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Walk",      "09:00", 30, "high"))
    pet.add_task(Task("Vet visit", "09:00", 60, "high"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    assert "09:00" in conflicts[0]
    assert "Mochi" in conflicts[0]


def test_no_conflict_when_times_differ():
    """Tasks at different times should not produce any conflicts."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Walk",     "08:00", 30, "high"))
    pet.add_task(Task("Feeding",  "07:00", 10, "high"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    assert scheduler.detect_conflicts() == []


# ---------------------------------------------------------------------------
# Filtering tests
# ---------------------------------------------------------------------------

def test_filter_by_pet_name():
    """Filtering by pet name should return only that pet's tasks."""
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog", 3)
    whiskers = Pet("Whiskers", "cat", 5)
    mochi.add_task(Task("Walk",    "08:00", 30, "high"))
    whiskers.add_task(Task("Play", "08:00", 20, "medium"))
    owner.add_pet(mochi)
    owner.add_pet(whiskers)
    scheduler = Scheduler(owner)

    result = scheduler.filter_tasks(pet_name="Mochi")
    assert len(result) == 1
    assert result[0][0].name == "Mochi"


def test_filter_by_completion_status():
    """Filtering completed=False should exclude finished tasks."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", 3)
    done = Task("Walk", "08:00", 30, "high")
    done.mark_complete()
    pending = Task("Feeding", "07:00", 10, "high")
    pet.add_task(done)
    pet.add_task(pending)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    incomplete = scheduler.filter_tasks(completed=False)
    assert len(incomplete) == 1
    assert incomplete[0][1].description == "Feeding"


def test_pet_with_no_tasks_has_empty_schedule():
    """An owner with a pet that has no tasks should return an empty schedule."""
    owner = Owner("Jordan")
    owner.add_pet(Pet("Mochi", "dog", 3))
    scheduler = Scheduler(owner)

    assert scheduler.get_all_tasks() == []
    assert scheduler.detect_conflicts() == []
