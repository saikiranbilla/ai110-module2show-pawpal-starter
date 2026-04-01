"""
PawPal+ logic layer.

Four main classes:
  Task      – a single care activity for a pet
  Pet       – stores pet info and its list of tasks
  Owner     – manages one or more pets
  Scheduler – retrieves, sorts, filters, and analyses tasks across all pets
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """Represents a single pet care activity."""

    description: str
    time: str              # "HH:MM" (24-hour)
    duration_minutes: int
    priority: str          # "low" | "medium" | "high"
    frequency: str = "once"  # "once" | "daily" | "weekly"
    is_complete: bool = False
    due_date: Optional[date] = None

    def __post_init__(self):
        """Default due_date to today when not provided."""
        if self.due_date is None:
            self.due_date = date.today()

    def mark_complete(self) -> None:
        """Mark this task as complete."""
        self.is_complete = True

    def next_occurrence(self) -> Optional["Task"]:
        """Return a new Task for the next recurrence, or None if non-recurring."""
        if self.frequency == "daily":
            return Task(
                description=self.description,
                time=self.time,
                duration_minutes=self.duration_minutes,
                priority=self.priority,
                frequency=self.frequency,
                due_date=self.due_date + timedelta(days=1),
            )
        if self.frequency == "weekly":
            return Task(
                description=self.description,
                time=self.time,
                duration_minutes=self.duration_minutes,
                priority=self.priority,
                frequency=self.frequency,
                due_date=self.due_date + timedelta(weeks=1),
            )
        return None


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    """Stores pet details and the list of care tasks assigned to it."""

    name: str
    species: str
    age: int
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        self.tasks.remove(task)

    def get_tasks(self) -> list:
        """Return all tasks assigned to this pet."""
        return list(self.tasks)


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

class Owner:
    """Manages a pet owner's profile and their collection of pets."""

    def __init__(self, name: str) -> None:
        self.name: str = name
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's profile."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner's profile."""
        self.pets.remove(pet)

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every (pet, task) pair across all owned pets."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """The 'brain' that retrieves, organises, and analyses tasks for an owner."""

    def __init__(self, owner: Owner) -> None:
        self.owner: Owner = owner

    # -- retrieval -----------------------------------------------------------

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Retrieve all (pet, task) pairs from the owner."""
        return self.owner.get_all_tasks()

    def get_todays_schedule(self) -> list[tuple[Pet, Task]]:
        """Return incomplete tasks due today, sorted by time."""
        today = date.today()
        filtered = [
            (p, t) for p, t in self.get_all_tasks()
            if not t.is_complete and t.due_date == today
        ]
        return sorted(filtered, key=lambda pt: pt[1].time)

    # -- sorting -------------------------------------------------------------

    def sort_by_time(self) -> list[tuple[Pet, Task]]:
        """Return all tasks sorted chronologically by their HH:MM time."""
        return sorted(self.get_all_tasks(), key=lambda pt: pt[1].time)

    # -- filtering -----------------------------------------------------------

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> list[tuple[Pet, Task]]:
        """
        Filter tasks by pet name and/or completion status.

        Parameters
        ----------
        pet_name  : case-insensitive pet name, or None to include all pets
        completed : True/False to filter by status, or None to include all
        """
        result = self.get_all_tasks()
        if pet_name is not None:
            result = [(p, t) for p, t in result if p.name.lower() == pet_name.lower()]
        if completed is not None:
            result = [(p, t) for p, t in result if t.is_complete == completed]
        return result

    # -- recurring tasks -----------------------------------------------------

    def mark_task_complete(self, pet: Pet, task: Task) -> None:
        """
        Mark a task complete and, for recurring tasks, add the next occurrence
        to the same pet's task list.
        """
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is not None:
            pet.add_task(next_task)

    # -- conflict detection --------------------------------------------------

    def detect_conflicts(self) -> list[str]:
        """
        Detect tasks scheduled at the exact same time for the same pet.

        Returns a list of human-readable warning strings (empty if no conflicts).
        Note: this only checks for exact-time matches, not overlapping durations.
        """
        warnings: list[str] = []
        for pet in self.owner.pets:
            seen: dict[str, str] = {}  # time -> first task description
            for task in pet.tasks:
                if task.time in seen:
                    warnings.append(
                        f"Conflict for {pet.name}: '{task.description}' and "
                        f"'{seen[task.time]}' are both scheduled at {task.time}"
                    )
                else:
                    seen[task.time] = task.description
        return warnings
