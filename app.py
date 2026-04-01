"""
PawPal+ Streamlit UI.

Connects the Owner / Pet / Task / Scheduler logic layer to an interactive
web interface.  All state lives in st.session_state so data persists across
page interactions.
"""

import streamlit as st
from datetime import date

from pawpal_system import Task, Pet, Owner, Scheduler

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# ---------------------------------------------------------------------------
# Session-state bootstrap
# Streamlit reruns the whole script on every interaction, so we keep the
# Owner object in session_state so it isn't reset on each click.
# ---------------------------------------------------------------------------

if "owner" not in st.session_state:
    st.session_state.owner = None   # set once the owner name is submitted

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.title("🐾 PawPal+")
st.caption("A smart pet care planning assistant")

# ---------------------------------------------------------------------------
# Step 1: Owner setup
# ---------------------------------------------------------------------------

st.header("1. Owner Profile")

with st.form("owner_form"):
    owner_name = st.text_input("Your name", value="Jordan")
    submitted = st.form_submit_button("Set / update owner")
    if submitted and owner_name.strip():
        if st.session_state.owner is None:
            st.session_state.owner = Owner(owner_name.strip())
        else:
            st.session_state.owner.name = owner_name.strip()
        st.success(f"Owner set to **{st.session_state.owner.name}**")

if st.session_state.owner is None:
    st.info("Please set an owner name above to get started.")
    st.stop()

owner: Owner = st.session_state.owner

# ---------------------------------------------------------------------------
# Step 2: Add a pet
# ---------------------------------------------------------------------------

st.header("2. Pets")

with st.form("add_pet_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name", value="Mochi")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "bird", "rabbit", "other"])
    with col3:
        age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)
    add_pet = st.form_submit_button("Add pet")
    if add_pet and pet_name.strip():
        existing_names = [p.name.lower() for p in owner.pets]
        if pet_name.strip().lower() in existing_names:
            st.warning(f"A pet named '{pet_name.strip()}' already exists.")
        else:
            owner.add_pet(Pet(pet_name.strip(), species, int(age)))
            st.success(f"Added **{pet_name.strip()}** the {species}!")

if owner.pets:
    pet_names = [p.name for p in owner.pets]
    st.write(f"**{owner.name}'s pets:** " + ", ".join(pet_names))
else:
    st.info("No pets yet — add one above.")

# ---------------------------------------------------------------------------
# Step 3: Add a task to a pet
# ---------------------------------------------------------------------------

st.header("3. Schedule a Task")

if not owner.pets:
    st.info("Add at least one pet before scheduling tasks.")
else:
    with st.form("add_task_form"):
        pet_choice = st.selectbox("Pet", [p.name for p in owner.pets])
        col1, col2 = st.columns(2)
        with col1:
            task_desc = st.text_input("Task description", value="Morning walk")
            task_time = st.text_input("Time (HH:MM, 24-hr)", value="08:00")
            duration  = st.number_input("Duration (minutes)", min_value=1, max_value=480, value=30)
        with col2:
            priority  = st.selectbox("Priority", ["low", "medium", "high"], index=2)
            frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
            due_str   = st.date_input("Due date", value=date.today())

        add_task = st.form_submit_button("Add task")
        if add_task and task_desc.strip():
            # Basic time format validation
            parts = task_time.strip().split(":")
            if len(parts) != 2 or not all(p.isdigit() for p in parts):
                st.error("Please enter time in HH:MM format (e.g. 08:30).")
            else:
                target_pet = next(p for p in owner.pets if p.name == pet_choice)
                target_pet.add_task(
                    Task(
                        description=task_desc.strip(),
                        time=task_time.strip(),
                        duration_minutes=int(duration),
                        priority=priority,
                        frequency=frequency,
                        due_date=due_str,
                    )
                )
                st.success(f"Task '{task_desc.strip()}' added to {pet_choice}!")

# ---------------------------------------------------------------------------
# Step 4: Today's Schedule
# ---------------------------------------------------------------------------

st.header("4. Today's Schedule")

scheduler = Scheduler(owner)

# Conflict detection
conflicts = scheduler.detect_conflicts()
if conflicts:
    for w in conflicts:
        st.warning(f"⚠ {w}")

# Build sorted schedule
schedule = scheduler.sort_by_time()

if not schedule:
    st.info("No tasks scheduled. Add pets and tasks above.")
else:
    # Filter controls
    col1, col2 = st.columns(2)
    with col1:
        filter_pet = st.selectbox(
            "Filter by pet",
            ["All"] + [p.name for p in owner.pets],
        )
    with col2:
        filter_status = st.selectbox(
            "Filter by status",
            ["All", "Pending", "Completed"],
        )

    # Apply filters
    filtered = schedule
    if filter_pet != "All":
        filtered = [(p, t) for p, t in filtered if p.name == filter_pet]
    if filter_status == "Pending":
        filtered = [(p, t) for p, t in filtered if not t.is_complete]
    elif filter_status == "Completed":
        filtered = [(p, t) for p, t in filtered if t.is_complete]

    if not filtered:
        st.info("No tasks match the selected filters.")
    else:
        rows = []
        for pet, task in filtered:
            rows.append(
                {
                    "Time": task.time,
                    "Pet": pet.name,
                    "Task": task.description,
                    "Duration": f"{task.duration_minutes} min",
                    "Priority": task.priority,
                    "Frequency": task.frequency,
                    "Due": str(task.due_date),
                    "Done": "✓" if task.is_complete else "○",
                }
            )
        st.table(rows)

    # Mark complete controls
    st.subheader("Mark a task complete")
    pending = [(p, t) for p, t in schedule if not t.is_complete]
    if not pending:
        st.success("All tasks are complete for today!")
    else:
        task_labels = [f"{p.name}: {t.description} @ {t.time}" for p, t in pending]
        chosen_label = st.selectbox("Select task", task_labels)
        if st.button("Mark complete"):
            idx = task_labels.index(chosen_label)
            chosen_pet, chosen_task = pending[idx]
            scheduler.mark_task_complete(chosen_pet, chosen_task)
            if chosen_task.frequency != "once":
                st.success(
                    f"'{chosen_task.description}' marked complete. "
                    f"Next {chosen_task.frequency} occurrence added automatically."
                )
            else:
                st.success(f"'{chosen_task.description}' marked complete.")
            st.rerun()

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.divider()
st.caption("PawPal+ — built with Streamlit and Python dataclasses")
