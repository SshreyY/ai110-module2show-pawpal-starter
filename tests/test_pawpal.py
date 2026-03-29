from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


def test_mark_complete_changes_status():
    task = Task("Morning walk", "walk", 30, "high")
    assert task.is_completed() == False
    task.mark_complete()
    assert task.is_completed() == True


def test_add_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog", 3)
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task("Breakfast", "feed", 10, "high"))
    pet.add_task(Task("Joint meds", "meds", 5, "high"))
    assert len(pet.get_tasks()) == 2


def test_scheduler_respects_time_limit():
    owner = Owner("Jordan", 30)
    mochi = Pet("Mochi", "dog", 3)
    mochi.add_task(Task("Long walk", "walk", 45, "high"))   # won't fit
    mochi.add_task(Task("Breakfast", "feed", 10, "high"))   # fits
    owner.add_pet(mochi)

    plan = Scheduler(owner).generate_plan()

    scheduled_names = [t.name for t in plan.scheduled_tasks]
    skipped_names   = [t.name for t in plan.skipped_tasks]

    assert "Breakfast" in scheduled_names
    assert "Long walk" in skipped_names
    assert plan.total_time_used <= 30


def test_high_priority_scheduled_before_low():
    owner = Owner("Jordan", 20)
    mochi = Pet("Mochi", "dog", 3)
    mochi.add_task(Task("Fetch",     "enrichment", 15, "low"))
    mochi.add_task(Task("Breakfast", "feed",        10, "high"))
    owner.add_pet(mochi)

    plan = Scheduler(owner).generate_plan()

    assert plan.scheduled_tasks[0].name == "Breakfast"


# --- Sorting ---

def test_sort_by_time_returns_ascending_order():
    tasks = [
        Task("Dinner",    "feed",  10, "low",    time_slot="18:00"),
        Task("Breakfast", "feed",  10, "high",   time_slot="08:00"),
        Task("Lunch",     "feed",  10, "medium", time_slot="12:30"),
    ]
    sorted_tasks = Scheduler.sort_by_time(tasks)
    assert [t.time_slot for t in sorted_tasks] == ["08:00", "12:30", "18:00"]


def test_generate_plan_assigns_sequential_time_slots():
    owner = Owner("Jordan", 60)
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Walk",  "walk", 20, "high"))
    pet.add_task(Task("Meds",  "meds",  5, "high"))
    owner.add_pet(pet)

    plan = Scheduler(owner).generate_plan()
    slots = [t.time_slot for t in plan.scheduled_tasks]

    # First task starts at 08:00; second starts after the first finishes
    assert slots[0] == "08:00"
    assert slots[1] == "08:05"


# --- Filtering ---

def test_get_tasks_for_pet_returns_only_that_pets_tasks():
    owner = Owner("Jordan", 60)
    mochi = Pet("Mochi", "dog", 3)
    luna  = Pet("Luna",  "cat", 5)
    mochi.add_task(Task("Walk",      "walk", 20, "high"))
    luna.add_task(Task("Litter box", "grooming", 10, "high"))
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi_tasks = owner.get_tasks_for_pet("Mochi")
    assert len(mochi_tasks) == 1
    assert mochi_tasks[0].name == "Walk"


def test_get_tasks_by_status_filters_correctly():
    owner = Owner("Jordan", 60)
    pet = Pet("Mochi", "dog", 3)
    done_task = Task("Walk", "walk", 20, "high")
    pending   = Task("Meds", "meds",  5, "high")
    done_task.mark_complete()
    pet.add_task(done_task)
    pet.add_task(pending)
    owner.add_pet(pet)

    assert len(owner.get_tasks_by_status(completed=True))  == 1
    assert len(owner.get_tasks_by_status(completed=False)) == 1


# --- Recurring Tasks ---

def test_daily_task_next_occurrence_is_tomorrow():
    today = date.today()
    task = Task("Walk", "walk", 20, "high", frequency="daily", due_date=today)
    next_task = task.next_occurrence()

    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.completed == False


def test_weekly_task_next_occurrence_is_seven_days_later():
    today = date.today()
    task = Task("Brush coat", "grooming", 15, "medium", frequency="weekly", due_date=today)
    next_task = task.next_occurrence()

    assert next_task is not None
    assert next_task.due_date == today + timedelta(weeks=1)


def test_as_needed_task_has_no_next_occurrence():
    task = Task("Vet visit", "meds", 60, "high", frequency="as needed")
    assert task.next_occurrence() is None


def test_complete_and_reschedule_adds_new_task_to_pet():
    owner = Owner("Jordan", 60)
    pet = Pet("Mochi", "dog", 3)
    task = Task("Walk", "walk", 20, "high", frequency="daily")
    pet.add_task(task)
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.complete_and_reschedule(task, pet)

    assert task.is_completed() == True
    assert len(pet.get_tasks()) == 2          # original + new recurrence
    assert pet.get_tasks()[1].completed == False


# --- Conflict Detection ---

def test_detect_conflicts_finds_overlapping_tasks():
    scheduler = Scheduler(Owner("Alex", 60))
    walk = Task("Walk", "walk", 30, "high", time_slot="09:00")
    meds = Task("Meds", "meds", 15, "high", time_slot="09:15")  # starts inside the walk window

    conflicts = scheduler.detect_conflicts([walk, meds])
    assert len(conflicts) == 1
    assert "Walk" in conflicts[0]
    assert "Meds" in conflicts[0]


def test_detect_conflicts_no_warning_for_back_to_back_tasks():
    scheduler = Scheduler(Owner("Alex", 60))
    bath  = Task("Bath",  "grooming", 20, "medium", time_slot="10:00")
    lunch = Task("Lunch", "feed",     10, "high",   time_slot="10:20")  # starts exactly when bath ends

    conflicts = scheduler.detect_conflicts([bath, lunch])
    assert conflicts == []
