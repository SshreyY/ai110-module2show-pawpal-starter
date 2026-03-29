import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Your daily pet care planner — add your pets, build a task list, and generate a schedule.")

st.divider()

# --- Session State Initialization ---
# Streamlit re-runs the whole script on every interaction.
# We check before creating so we don't wipe the owner on every click.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", 75)

owner = st.session_state.owner

# --- Owner Setup ---
st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value=owner.name)
with col2:
    time_available = st.number_input("Minutes available today", min_value=1, max_value=480, value=owner.time_available)

if st.button("Set owner"):
    # Preserve existing pets when updating owner info
    existing_pets = owner.pets[:]
    st.session_state.owner = Owner(owner_name, int(time_available))
    for pet in existing_pets:
        st.session_state.owner.add_pet(pet)
    owner = st.session_state.owner
    st.success(owner.get_info())

st.divider()

# --- Pets ---
st.subheader("Pets")

with st.expander("Add a pet", expanded=not owner.pets):
    pet_name    = st.text_input("Pet name", value="Mochi")
    species     = st.selectbox("Species", ["dog", "cat", "other"])
    pet_age     = st.number_input("Age (years)", min_value=0, max_value=30, value=3)
    special_needs = st.text_input("Special needs (optional)", value="")

    if st.button("Add pet"):
        if not pet_name.strip():
            st.warning("Pet name can't be blank.")
        else:
            new_pet = Pet(pet_name.strip(), species, int(pet_age), special_needs or None)
            owner.add_pet(new_pet)
            st.success(f"Added: {new_pet.get_info()}")

if owner.pets:
    for i, pet in enumerate(owner.pets):
        col_info, col_btn = st.columns([5, 1])
        with col_info:
            st.write(f"**{pet.name}** — {pet.get_info()}")
        with col_btn:
            if st.button("Remove", key=f"remove_pet_{i}"):
                owner.remove_pet(pet)
                st.rerun()
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Tasks ---
st.subheader("Tasks")

pet_names = [p.name for p in owner.pets]
if not pet_names:
    st.info("Add a pet first before adding tasks.")
else:
    with st.expander("Add a task", expanded=True):
        target_pet_name = st.selectbox("Assign to pet", pet_names)
        col1, col2, col3 = st.columns(3)
        with col1:
            task_title = st.text_input("Task title", value="Morning walk")
            category   = st.selectbox("Category", ["walk", "feed", "meds", "grooming", "enrichment", "other"])
        with col2:
            duration  = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
            frequency = st.selectbox("Frequency", ["daily", "weekly", "as needed"])
        with col3:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

        # Live time budget check
        current_total = sum(t.duration for t in owner.get_tasks_by_status(completed=False))
        time_left = owner.time_available - current_total
        over_limit = int(duration) > time_left

        if over_limit:
            st.error(
                f"Not enough time — this task needs {int(duration)} min but only {time_left} min "
                f"remaining ({current_total} / {owner.time_available} min used). "
                f"Shorten the task, remove another task, or increase your available minutes."
            )

        if st.button("Add task", disabled=over_limit):
            if not task_title.strip():
                st.warning("Task title can't be blank.")
            else:
                target_pet = next(p for p in owner.pets if p.name == target_pet_name)
                target_pet.add_task(Task(task_title.strip(), category, int(duration), priority, frequency))
                st.success(f"Added '{task_title}' to {target_pet_name}.")

    # --- Task list with filter, mark-complete, and remove ---
    all_tasks = owner.get_all_tasks()
    if all_tasks:
        status_filter = st.radio("Show", ["Pending", "Completed", "All"], horizontal=True)

        if status_filter == "Pending":
            filtered = owner.get_tasks_by_status(completed=False)
        elif status_filter == "Completed":
            filtered = owner.get_tasks_by_status(completed=True)
        else:
            filtered = all_tasks

        if not filtered:
            st.info(f"No {status_filter.lower()} tasks.")
        else:
            scheduler = Scheduler(owner)
            for pet in owner.pets:
                pet_filtered = [t for t in pet.get_tasks() if t in filtered]
                if not pet_filtered:
                    continue
                st.markdown(f"**{pet.name}**")
                for i, task in enumerate(pet_filtered):
                    col_status, col_info, col_done, col_remove = st.columns([1, 5, 1.5, 1.5])
                    with col_status:
                        st.write("✅" if task.is_completed() else "🔲")
                    with col_info:
                        st.write(f"{task.name} — {task.duration} min · {task.priority} · {task.frequency}")
                    with col_done:
                        if not task.is_completed():
                            if st.button("Done", key=f"done_{pet.name}_{i}"):
                                next_task = scheduler.complete_and_reschedule(task, pet)
                                if next_task:
                                    st.success(f"Marked done. Next '{task.name}' due {next_task.due_date}.")
                                else:
                                    st.success(f"Marked '{task.name}' complete.")
                                st.rerun()
                    with col_remove:
                        if st.button("Remove", key=f"remove_task_{pet.name}_{i}"):
                            pet.remove_task(task)
                            st.rerun()
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# --- Generate Schedule ---
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    all_tasks = owner.get_all_tasks()
    if not all_tasks:
        st.warning("No tasks to schedule — add some tasks first.")
    else:
        plan = Scheduler(owner).generate_plan()

        # Conflict warnings: shown first so they're impossible to miss
        if plan.conflicts:
            st.error("**Scheduling conflicts detected.** Two or more tasks overlap. "
                     "Adjust durations or remove a task before following this schedule.")
            for warning in plan.conflicts:
                st.error(warning)

        # Scheduled tasks table
        st.markdown("### Scheduled Tasks")
        if plan.scheduled_tasks:
            sorted_tasks = Scheduler.sort_by_time(plan.scheduled_tasks)
            st.dataframe(
                [
                    {
                        "Start": t.time_slot,
                        "Task": t.name,
                        "Pet": next((p.name for p in owner.pets if t in p.get_tasks()), "—"),
                        "Duration (min)": t.duration,
                        "Priority": t.priority,
                        "Frequency": t.frequency,
                    }
                    for t in sorted_tasks
                ],
                use_container_width=True,
                hide_index=True,
            )
            pct = plan.total_time_used / owner.time_available
            st.caption(f"Time used: {plan.total_time_used} / {owner.time_available} min")
            st.progress(min(pct, 1.0))
        else:
            st.warning("No tasks fit within the available time. Try increasing your available minutes or shortening task durations.")

        # Skipped tasks
        if plan.skipped_tasks:
            with st.expander(f"Skipped tasks ({len(plan.skipped_tasks)})", expanded=True):
                st.dataframe(
                    [{"Task": t.name, "Duration (min)": t.duration, "Priority": t.priority}
                     for t in plan.skipped_tasks],
                    use_container_width=True,
                    hide_index=True,
                )

        # Per-pet breakdown using get_tasks_for_pet()
        if owner.pets:
            with st.expander("Per-pet breakdown", expanded=False):
                for pet in owner.pets:
                    pet_tasks = owner.get_tasks_for_pet(pet.name)
                    scheduled_names = {t.name for t in plan.scheduled_tasks}
                    st.markdown(f"**{pet.name}**")
                    for t in pet_tasks:
                        status = "✅" if t.name in scheduled_names else "skipped"
                        st.write(f"  {status}  {t.name} — {t.duration} min, {t.priority}")

        with st.expander("Why this schedule?", expanded=False):
            st.write(plan.reasoning)
