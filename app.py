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

if "tasks" not in st.session_state:
    st.session_state.tasks = []

# --- Owner Setup ---
st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")
time_available = st.number_input("Minutes available today", min_value=1, max_value=480, value=75)

if st.button("Set owner"):
    st.session_state.owner = Owner(owner_name, int(time_available))
    st.session_state.tasks = []  # reset tasks when owner changes
    st.success(f"Owner set: {st.session_state.owner.get_info()}")

st.divider()

# --- Add a Pet ---
st.subheader("Add a Pet")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
pet_age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)
special_needs = st.text_input("Special needs (optional)", value="")

if st.button("Add pet"):
    new_pet = Pet(pet_name, species, int(pet_age), special_needs or None)
    st.session_state.owner.add_pet(new_pet)
    st.success(f"Added: {new_pet.get_info()}")

if st.session_state.owner.pets:
    st.write("**Pets on file:**", ", ".join(p.name for p in st.session_state.owner.pets))

st.divider()

# --- Add a Task ---
st.subheader("Add a Task")
st.caption("Pick which pet gets this task, then fill in the details.")

pet_names = [p.name for p in st.session_state.owner.pets]
if pet_names:
    target_pet_name = st.selectbox("Assign to pet", pet_names)
    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
        category = st.selectbox("Category", ["walk", "feed", "meds", "grooming", "enrichment", "other"])
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        frequency = st.selectbox("Frequency", ["daily", "weekly", "as needed"])
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    if st.button("Add task"):
        # Find the matching Pet object and call add_task() on it
        target_pet = next(p for p in st.session_state.owner.pets if p.name == target_pet_name)
        new_task = Task(task_title, category, int(duration), priority, frequency)
        target_pet.add_task(new_task)
        st.session_state.tasks.append(
            {"pet": target_pet_name, "task": task_title, "category": category,
             "duration (min)": int(duration), "priority": priority, "frequency": frequency}
        )
        st.success(f"Added '{task_title}' to {target_pet_name}.")

    if st.session_state.tasks:
        st.write("**Tasks added so far:**")
        st.table(st.session_state.tasks)
    else:
        st.info("No tasks yet. Add one above.")
else:
    st.info("Add a pet first before adding tasks.")

st.divider()

# --- Generate Schedule ---
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    all_tasks = st.session_state.owner.get_all_tasks()
    if not all_tasks:
        st.warning("No tasks to schedule — add some tasks first.")
    else:
        plan = Scheduler(st.session_state.owner).generate_plan()

        st.markdown("### Scheduled Tasks")
        if plan.scheduled_tasks:
            for task in Scheduler.sort_by_time(plan.scheduled_tasks):
                st.write(f"- `{task.time_slot}` **{task.name}** — {task.duration} min · {task.priority} priority · {task.frequency}")
            st.info(f"Total time used: {plan.total_time_used} / {st.session_state.owner.time_available} min")
        else:
            st.write("Nothing fit in the available time.")

        if plan.skipped_tasks:
            st.markdown("### Skipped Tasks")
            for task in plan.skipped_tasks:
                st.write(f"- {task.name} ({task.duration} min, {task.priority} priority)")

        if plan.conflicts:
            st.markdown("### ⚠️ Conflicts Detected")
            for warning in plan.conflicts:
                st.warning(warning)

        st.markdown("### Reasoning")
        st.write(plan.reasoning)
