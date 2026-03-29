from pawpal_system import Task, Pet, Owner, Scheduler


# --- Setup ---
owner = Owner("Jordan", 75)

mochi = Pet("Mochi", "dog", 3, special_needs="hip dysplasia — no long runs")
luna = Pet("Luna", "cat", 5)

owner.add_pet(mochi)
owner.add_pet(luna)

# --- Tasks for Mochi ---
mochi.add_task(Task("Morning walk",   "walk",     20, "high",   "daily"))
mochi.add_task(Task("Joint meds",     "meds",      5, "high",   "daily"))
mochi.add_task(Task("Brush coat",     "grooming", 15, "medium", "weekly"))
mochi.add_task(Task("Fetch session",  "enrichment",25, "low",   "daily"))

# --- Tasks for Luna ---
luna.add_task(Task("Breakfast",       "feed",     10, "high",   "daily"))
luna.add_task(Task("Litter box",      "grooming", 10, "high",   "daily"))
luna.add_task(Task("Laser play",      "enrichment",15, "medium","daily"))


# --- Generate the plan ---
scheduler = Scheduler(owner)
plan = scheduler.generate_plan()


# --- Print Today's Schedule ---
print("=" * 45)
print(f"  Today's Schedule — {owner.name}'s Pets")
print("=" * 45)

print(f"\nOwner : {owner.name}")
print(f"Pets  : {', '.join(p.name for p in owner.pets)}")
print(f"Time  : {owner.time_available} min available\n")

print("-" * 45)
print("  SCHEDULED TASKS (sorted by start time)")
print("-" * 45)
for i, task in enumerate(Scheduler.sort_by_time(plan.scheduled_tasks), 1):
    status = "[done]" if task.is_completed() else "[ ]"
    print(f"  {i}. {status} {task.time_slot}  {task.name:<20} {task.duration:>3} min   {task.priority} priority")

print(f"\n  Total time used: {plan.total_time_used} / {owner.time_available} min")

if plan.skipped_tasks:
    print("\n" + "-" * 45)
    print("  SKIPPED TASKS")
    print("-" * 45)
    for task in plan.skipped_tasks:
        print(f"  - {task.name:<20} {task.duration:>3} min   {task.priority} priority")

print("\n" + "-" * 45)
print("  REASONING")
print("-" * 45)
print(f"  {plan.reasoning}")
print("=" * 45)

# --- Demo: Filter by pet ---
print("\n" + "=" * 45)
print("  FILTER DEMO")
print("=" * 45)

print("\n  Mochi's tasks only:")
for t in owner.get_tasks_for_pet("Mochi"):
    print(f"    - {t.name} ({t.priority})")

print("\n  Incomplete tasks across all pets:")
for t in owner.get_tasks_by_status(completed=False):
    print(f"    - {t.name} ({t.priority})")

# Mark one task done to show status filter working
mochi_tasks = owner.get_tasks_for_pet("Mochi")
mochi_tasks[0].mark_complete()
print(f"\n  Marked '{mochi_tasks[0].name}' as done.")
print("  Now completed tasks:")
for t in owner.get_tasks_by_status(completed=True):
    print(f"    - {t.name}")
print("=" * 45)

# --- Demo: Recurring Tasks ---
print("\n" + "=" * 45)
print("  RECURRING TASK DEMO")
print("=" * 45)

# Pick a daily task and a weekly task to complete
daily_task = next(t for t in owner.get_tasks_for_pet("Mochi") if t.name == "Joint meds")
weekly_task = next(t for t in owner.get_tasks_for_pet("Mochi") if t.name == "Brush coat")

print(f"\n  Completing '{daily_task.name}' (frequency: {daily_task.frequency}, due: {daily_task.due_date})")
next_daily = scheduler.complete_and_reschedule(daily_task, mochi)
if next_daily:
    print(f"  -> Next occurrence auto-added: due {next_daily.due_date}  (+1 day via timedelta)")

print(f"\n  Completing '{weekly_task.name}' (frequency: {weekly_task.frequency}, due: {weekly_task.due_date})")
next_weekly = scheduler.complete_and_reschedule(weekly_task, mochi)
if next_weekly:
    print(f"  -> Next occurrence auto-added: due {next_weekly.due_date}  (+7 days via timedelta)")

print(f"\n  Mochi now has {len(owner.get_tasks_for_pet('Mochi'))} tasks (2 new recurrences added):")
for t in owner.get_tasks_for_pet("Mochi"):
    status = "done" if t.is_completed() else f"due {t.due_date}"
    print(f"    - {t.name:<20} ({t.frequency:<9})  {status}")
print("=" * 45)

# --- Demo: Conflict Detection ---
print("\n" + "=" * 45)
print("  CONFLICT DETECTION DEMO")
print("=" * 45)

# Two tasks with overlapping time windows:
# Walk starts at 09:00, runs 30 min → occupies 09:00–09:30
# Meds start at 09:15 → overlaps the last 15 min of the walk
walk = Task("Morning walk", "walk", 30, "high", time_slot="09:00")
meds = Task("Joint meds",   "meds", 15, "high", time_slot="09:15")

conflict_scheduler = Scheduler(Owner("Alex", 60))
conflicts = conflict_scheduler.detect_conflicts([walk, meds])

if conflicts:
    print("\n  Overlapping tasks detected:")
    for warning in conflicts:
        print(f"  !! {warning}")
else:
    print("  No conflicts found.")

# Also show a clean pair — no overlap
print()
bath  = Task("Bath time",  "grooming", 20, "medium", time_slot="10:00")
lunch = Task("Lunch feed", "feed",     10, "high",   time_slot="10:30")
no_conflicts = conflict_scheduler.detect_conflicts([bath, lunch])
print(f"  Bath (10:00–10:20) vs Lunch (10:30–10:40): "
      f"{'conflict!' if no_conflicts else 'no conflict — clean schedule'}")
print("=" * 45)
