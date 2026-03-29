# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling

Phase 4 extended the core scheduler with four algorithmic improvements:

**Time-of-day sorting**: Every scheduled task gets an actual `HH:MM` start time, calculated by chaining durations forward from 8:00 AM. `Scheduler.sort_by_time()` uses a lambda on the time string to sort tasks in chronological order, which works because zero-padded `"HH:MM"` strings sort correctly without converting to numbers.

**Task filtering**: `Owner.get_tasks_for_pet(name)` returns only the tasks belonging to a specific pet. `Owner.get_tasks_by_status(completed)` filters across all pets by completion state. Both methods make it easy to answer questions like "what does Mochi still have left today?" without touching unrelated data.

**Recurring tasks**: `Task.next_occurrence()` uses Python's `timedelta` to compute the next due date: `+1 day` for `"daily"` tasks and `+7 days` for `"weekly"` ones. `"as needed"` tasks return `None` and don't auto-recur. `Scheduler.complete_and_reschedule()` wraps this and it marks the task done and immediately adds the next copy to the pet's task list so the owner never has to re-enter it manually.

**Conflict detection**: `Scheduler.detect_conflicts()` checks every pair of scheduled tasks for overlapping time windows using the standard interval overlap test (`a_start < b_end and b_start < a_end`). It returns plain-language warning strings instead of raising exceptions, so the app can surface the issue to the user without crashing.
