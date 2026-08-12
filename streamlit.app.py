import datetime
import pandas as pd
import streamlit as st
from st_supabase_connection import SupabaseConnection

st.set_page_config(page_title="Tracker", page_icon="📉", layout="centered")

# Initialize Supabase connection
supabase_conn = st.connection("supabase", type=SupabaseConnection)


def fetch_history():
    try:
        # Fetch all rows from the 'tracker' table sorted by newest first
        response = (
            supabase_conn.table("tracker")
            .select("*")
            .order("date", desc=True)
            .execute()
        )
        return pd.DataFrame(response.data)
    except Exception:
        return pd.DataFrame()


st.title("A1C and Weight Tracker")
st.markdown("---")

# Logging form
st.subheader("Add New Entry")
with st.form("log_form", clear_on_submit=True, enter_to_submit=False):
    date = st.date_input("Date", datetime.date.today())
    weight_value = st.number_input(
        "Weight (lbs)", min_value=0.0, step=1.0, value=150.0
    )
    glucose_value = st.number_input(
        "Glucose (mg/dL)", min_value=0.0, step=1.0, value=100.0
    )
    notes = st.text_input(
        "Notes (optional)", placeholder="Fasting, post-meal, etc."
    )

    submitted = st.form_submit_button("Save Entry")

if submitted:
    a1c_value = round((glucose_value + 46.7) / 28.7, 1)

    new_entry = {
        "date": str(date),
        "weight": weight_value,
        "a1c": a1c_value,
        "glucose": glucose_value,
        "notes": notes,
    }

    # Insert row directly into Supabase database
    supabase_conn.table("tracker").insert(new_entry).execute()
    st.success("Saved successfully!")
    st.rerun()

st.markdown("---")

# History section
st.subheader("History")
df = fetch_history()

if df.empty:
    st.info("No entries yet. Add one above.")
else:
    # Rename columns for clean display
    display_df = df.rename(
        columns={
            "date": "Date",
            "weight": "Weight (lbs)",
            "a1c": "A1c (%)",
            "glucose": "Glucose (mg/dL)",
            "notes": "Notes",
        }
    )
    st.dataframe(display_df, use_container_width=True)

if st.button("Clear All Data"):
    # Delete all records from the tracker table
    supabase_conn.table("tracker").delete().neq("date", "").execute()
    st.success("Cleared all records!")
    st.rerun()
    st.session_state.data = pd.DataFrame(
    columns=["Date", "Weight (lbs)", "A1c (%)", "Notes"]
    )
    st.rerun()
