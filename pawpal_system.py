from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Pet:
    name: str
    species: str
    age: int
    special_needs: Optional[str] = None

    def get_info(self) -> str:
        pass


@dataclass
class Task:
    name: str
    category: str        # e.g. "walk", "feed", "meds", "grooming"
    duration: int        # in minutes
    priority: str        # "high", "medium", or "low"
    completed: bool = False

    def mark_complete(self) -> None:
        pass

    def is_completed(self) -> bool:
        pass


class Owner:
    def __init__(self, name: str, time_available: int):
        self.name = name
        self.time_available = time_available  # total free minutes in the day

    def get_info(self) -> str:
        pass


class DailyPlan:
    def __init__(self):
        self.scheduled_tasks: List[Task] = []
        self.skipped_tasks: List[Task] = []
        self.total_time_used: int = 0
        self.reasoning: str = ""

    def display(self) -> None:
        pass

    def get_summary(self) -> str:
        pass


class Scheduler:
    def __init__(self, tasks: List[Task], time_available: int):
        self.tasks = tasks
        self.time_available = time_available
        self.plan: Optional[DailyPlan] = None

    def prioritize_tasks(self) -> List[Task]:
        pass

    def fits_in_time(self, task: Task, time_remaining: int) -> bool:
        pass

    def generate_plan(self) -> DailyPlan:
        pass
