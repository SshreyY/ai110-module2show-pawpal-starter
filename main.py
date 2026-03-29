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
print("  SCHEDULED TASKS")
print("-" * 45)
for i, task in enumerate(plan.scheduled_tasks, 1):
    status = "[done]" if task.is_completed() else "[ ]"
    print(f"  {i}. {status} {task.name:<20} {task.duration:>3} min   {task.priority} priority")

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
