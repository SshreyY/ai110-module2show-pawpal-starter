from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional


@dataclass
class Task:
    name: str
    category: str        # e.g. "walk", "feed", "meds", "grooming"
    duration: int        # in minutes
    priority: str        # "high", "medium", or "low"
    frequency: str = "daily"        # e.g. "daily", "weekly", "as needed"
    completed: bool = False
    time_slot: str = "08:00"        # scheduled start time in "HH:MM" format
    due_date: date = field(default_factory=date.today)  # when this task is due

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def is_completed(self) -> bool:
        """Return True if the task has been completed."""
        return self.completed

    def next_occurrence(self) -> Optional["Task"]:
        """Return a new Task due on the next occurrence date, or None if frequency is 'as needed'."""
        if self.frequency == "daily":
            next_due = self.due_date + timedelta(days=1)
        elif self.frequency == "weekly":
            next_due = self.due_date + timedelta(weeks=1)
        else:
            return None  # "as needed" tasks don't auto-recur

        return Task(
            name=self.name,
            category=self.category,
            duration=self.duration,
            priority=self.priority,
            frequency=self.frequency,
            due_date=next_due,
        )


@dataclass
class Pet:
    name: str
    species: str
    age: int
    special_needs: Optional[str] = None
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet's task list if it exists."""
        if task in self.tasks:
            self.tasks.remove(task)

    def get_tasks(self) -> List[Task]:
        """Return all tasks assigned to this pet."""
        return self.tasks

    def get_info(self) -> str:
        """Return a readable summary of the pet's basic info."""
        info = f"{self.name} ({self.species}, {self.age} yr old)"
        if self.special_needs:
            info += f" — special needs: {self.special_needs}"
        return info


class Owner:
    def __init__(self, name: str, time_available: int):
        self.name = name
        self.time_available = time_available  # total free minutes in the day
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner's pet list if it exists."""
        if pet in self.pets:
            self.pets.remove(pet)

    def get_all_tasks(self) -> List[Task]:
        """Collect every task across all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks

    def get_tasks_for_pet(self, pet_name: str) -> List[Task]:
        """Return all tasks belonging to the pet with the given name."""
        for pet in self.pets:
            if pet.name == pet_name:
                return pet.get_tasks()
        return []

    def get_tasks_by_status(self, completed: bool) -> List[Task]:
        """Return tasks across all pets filtered by completion status."""
        return [t for t in self.get_all_tasks() if t.completed == completed]

    def get_info(self) -> str:
        """Return a readable summary of the owner's name, time, and pets."""
        pet_names = ", ".join(p.name for p in self.pets) if self.pets else "no pets yet"
        return (
            f"{self.name} has {self.time_available} min available today. "
            f"Pets: {pet_names}."
        )


class DailyPlan:
    def __init__(self):
        self.scheduled_tasks: List[Task] = []
        self.skipped_tasks: List[Task] = []
        self.total_time_used: int = 0
        self.reasoning: str = ""
        self.conflicts: List[str] = []   # warning messages for overlapping tasks

    def display(self) -> None:
        """Print the full plan summary to the terminal."""
        print(self.get_summary())

    def get_summary(self) -> str:
        """Build and return the full plan as a formatted string."""
        lines = ["=== Daily Plan ==="]
        if self.scheduled_tasks:
            lines.append("\nScheduled:")
            for task in self.scheduled_tasks:
                lines.append(f"  - {task.name} ({task.duration} min, {task.priority} priority)")
            lines.append(f"\nTotal time: {self.total_time_used} min")
        else:
            lines.append("No tasks scheduled.")

        if self.skipped_tasks:
            lines.append("\nSkipped:")
            for task in self.skipped_tasks:
                lines.append(f"  - {task.name} ({task.duration} min, {task.priority} priority)")

        if self.reasoning:
            lines.append(f"\nReasoning: {self.reasoning}")

        return "\n".join(lines)


class Scheduler:
    PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

    def __init__(self, owner: Owner):
        self.owner = owner
        self.time_available = owner.time_available
        self.plan: Optional[DailyPlan] = None

    @staticmethod
    def sort_by_time(tasks: List[Task]) -> List[Task]:
        """Return tasks sorted ascending by their time_slot string in HH:MM format."""
        return sorted(tasks, key=lambda t: t.time_slot)

    def prioritize_tasks(self) -> List[Task]:
        """Return incomplete tasks sorted high → medium → low, then by duration (shorter first)."""
        tasks = [t for t in self.owner.get_all_tasks() if not t.is_completed()]
        return sorted(tasks, key=lambda t: (self.PRIORITY_ORDER.get(t.priority, 99), t.duration))

    def fits_in_time(self, task: Task, time_remaining: int) -> bool:
        """Return True if the task's duration fits within the remaining time."""
        return task.duration <= time_remaining

    @staticmethod
    def _slot_to_minutes(time_slot: str) -> int:
        """Convert a 'HH:MM' string to total minutes since midnight."""
        h, m = time_slot.split(":")
        return int(h) * 60 + int(m)

    def detect_conflicts(self, tasks: List[Task]) -> List[str]:
        """Return warning strings for any two tasks whose time windows overlap."""
        warnings = []
        for i, a in enumerate(tasks):
            a_start = self._slot_to_minutes(a.time_slot)
            a_end = a_start + a.duration
            for b in tasks[i + 1:]:
                b_start = self._slot_to_minutes(b.time_slot)
                b_end = b_start + b.duration
                if a_start < b_end and b_start < a_end:
                    warnings.append(
                        f"CONFLICT: '{a.name}' ({a.time_slot}, {a.duration} min) "
                        f"overlaps '{b.name}' ({b.time_slot}, {b.duration} min)"
                    )
        return warnings

    def complete_and_reschedule(self, task: Task, pet: Pet) -> Optional[Task]:
        """Mark a task complete and add the next occurrence to the pet if the task recurs."""
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task:
            pet.add_task(next_task)
        return next_task

    def generate_plan(self) -> DailyPlan:
        """Build a DailyPlan by greedily scheduling tasks in priority order, assigning HH:MM start times."""
        plan = DailyPlan()
        time_remaining = self.time_available
        skipped_reasons = []
        current_minutes = 8 * 60  # day starts at 08:00

        for task in self.prioritize_tasks():
            if self.fits_in_time(task, time_remaining):
                task.time_slot = f"{current_minutes // 60:02d}:{current_minutes % 60:02d}"
                plan.scheduled_tasks.append(task)
                plan.total_time_used += task.duration
                time_remaining -= task.duration
                current_minutes += task.duration
            else:
                plan.skipped_tasks.append(task)
                skipped_reasons.append(
                    f"{task.name} needs {task.duration} min but only {time_remaining} min left"
                )

        if skipped_reasons:
            plan.reasoning = (
                "Scheduled all high-priority tasks first, then filled in lower-priority ones "
                "with whatever time was left. Skipped: " + "; ".join(skipped_reasons) + "."
            )
        else:
            plan.reasoning = "All tasks fit within the available time — nothing was skipped."

        plan.conflicts = self.detect_conflicts(plan.scheduled_tasks)
        self.plan = plan
        return plan
