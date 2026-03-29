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

    # high-priority task should appear first in the scheduled list
    assert plan.scheduled_tasks[0].name == "Breakfast"
