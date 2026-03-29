from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Task:
    name: str
    category: str        # e.g. "walk", "feed", "meds", "grooming"
    duration: int        # in minutes
    priority: str        # "high", "medium", or "low"
    frequency: str = "daily"   # e.g. "daily", "weekly", "as needed"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def is_completed(self) -> bool:
        """Return True if the task has been completed."""
        return self.completed


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

    def prioritize_tasks(self) -> List[Task]:
        """Return incomplete tasks sorted high → medium → low, then by duration (shorter first)."""
        tasks = [t for t in self.owner.get_all_tasks() if not t.is_completed()]
        return sorted(tasks, key=lambda t: (self.PRIORITY_ORDER.get(t.priority, 99), t.duration))

    def fits_in_time(self, task: Task, time_remaining: int) -> bool:
        """Return True if the task's duration fits within the remaining time."""
        return task.duration <= time_remaining

    def generate_plan(self) -> DailyPlan:
        """Build a DailyPlan by greedily scheduling tasks in priority order."""
        plan = DailyPlan()
        time_remaining = self.time_available
        skipped_reasons = []

        for task in self.prioritize_tasks():
            if self.fits_in_time(task, time_remaining):
                plan.scheduled_tasks.append(task)
                plan.total_time_used += task.duration
                time_remaining -= task.duration
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

        self.plan = plan
        return plan
