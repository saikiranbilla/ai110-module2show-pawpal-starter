"""
main.py – CLI demo script for PawPal+.

Creates an owner, two pets, and several tasks, then prints a sorted schedule
and any detected scheduling conflicts.

Run with:  python main.py
"""

from datetime import date
from pawpal_system import Task, Pet, Owner, Scheduler


def print_schedule(schedule: list) -> None:
    """Pretty-print a list of (pet, task) pairs."""
    if not schedule:
        print("  (no tasks)")
        return
    for pet, task in schedule:
        status = "x" if task.is_complete else " "
        recur = f" [{task.frequency}]" if task.frequency != "once" else ""
        print(
            f"  [{status}] {task.time}  {pet.name:<10}  "
            f"{task.description:<25}  "
            f"{task.duration_minutes:>3} min  "
            f"priority={task.priority}{recur}"
        )


def main() -> None:
    # -----------------------------------------------------------------------
    # Setup: owner + pets
    # -----------------------------------------------------------------------
    owner = Owner("Jordan")

    mochi = Pet("Mochi", "dog", 3)
    whiskers = Pet("Whiskers", "cat", 5)

    # Tasks for Mochi (intentionally out of time order to test sorting)
    mochi.add_task(Task("Evening walk",    "18:00", 30, "high",   "daily"))
    mochi.add_task(Task("Morning feeding", "07:30", 10, "high",   "daily"))
    mochi.add_task(Task("Flea treatment",  "09:00",  5, "medium", "once"))

    # Tasks for Whiskers
    whiskers.add_task(Task("Morning feeding", "07:30", 10, "high",   "daily"))
    whiskers.add_task(Task("Playtime",        "15:00", 20, "medium", "daily"))
    whiskers.add_task(Task("Vet checkup",     "10:00", 60, "high",   "once"))

    owner.add_pet(mochi)
    owner.add_pet(whiskers)

    scheduler = Scheduler(owner)

    # -----------------------------------------------------------------------
    # Today's full schedule (sorted)
    # -----------------------------------------------------------------------
    print("=" * 65)
    print(f"  PawPal+  -  Today's Schedule  ({date.today()})")
    print("=" * 65)
    print_schedule(scheduler.sort_by_time())

    # -----------------------------------------------------------------------
    # Conflict detection
    # -----------------------------------------------------------------------
    print()
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        print("WARNING: Scheduling conflicts detected:")
        for w in conflicts:
            print(f"   - {w}")
    else:
        print("OK: No scheduling conflicts.")

    # -----------------------------------------------------------------------
    # Demo: mark a daily task complete → recurrence auto-created
    # -----------------------------------------------------------------------
    print()
    print("--- Marking 'Morning feeding' complete for Mochi ---")
    feeding = mochi.tasks[1]   # "Morning feeding" added second
    scheduler.mark_task_complete(mochi, feeding)
    print(f"  Task '{feeding.description}' is_complete = {feeding.is_complete}")
    if len(mochi.tasks) > 3:
        new_task = mochi.tasks[-1]
        print(f"  Next occurrence scheduled: '{new_task.description}' on {new_task.due_date}")

    # -----------------------------------------------------------------------
    # Demo: add a conflict and verify detection
    # -----------------------------------------------------------------------
    print()
    print("--- Adding a duplicate-time task to show conflict detection ---")
    mochi.add_task(Task("Grooming", "18:00", 45, "low", "once"))
    new_conflicts = scheduler.detect_conflicts()
    for w in new_conflicts:
        print(f"  WARNING: {w}")

    # -----------------------------------------------------------------------
    # Filtering demo
    # -----------------------------------------------------------------------
    print()
    print("--- Filtering: only Whiskers' tasks ---")
    whiskers_tasks = scheduler.filter_tasks(pet_name="Whiskers")
    print_schedule(whiskers_tasks)


if __name__ == "__main__":
    main()
