import datetime
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection  # <-- Make sure this line is present!

st.set_page_config(page_title="Tracker", page_icon="📉", layout="centered")

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(
        columns=["Date", "Weight (lbs)", "A1c (%)", "Glucose (mg/dL)", "Notes"]
    )
conn = st.connection("gsheets", type=GSheetsConnection)

# Helper function to read current sheet data cleanly
def fetch_data():
    try:
        data = conn.read(ttl=0)
        data = data.dropna(how="all")
        # Reverse the order so the newest dates show up first
        return data.iloc[::-1]
    except Exception:
        return pd.DataFrame(
            columns=["Date", "Weight (lbs)", "A1c (%)", "Glucose (mg/dL)", "Notes"]
        )

# Fetch latest saved data from the cloud
df = fetch_data()

st.title("A1C and Weight Tracker")
st.markdown("---")

# Quick logging form
st.subheader("Add New Entry")
with st.form("log_form" , clear_on_submit=True, enter_to_submit=False):
    date = st.date_input("Date", datetime.date.today())
    weight_value = st.number_input("Weight (lbs)", min_value=0.0, step=5.0, value=150.0)
    glucose_value = st.number_input("Glucose (mL/dL)", min_value=0.0, step=1.0, value=100.0)
    notes = st.text_input("Notes (optional)", placeholder="Fasting, post-meal, etc.")

    submitted = st.form_submit_button("Save Entry")

if submitted:

    a1c_value = round((glucose_value + 46.7) / 28.7, 1 )

    new_row = pd.DataFrame({
        "Date": [date],
        "Weight (lbs)": [weight_value],
        "A1c (%)": [a1c_value],
        "Glucose (mL/dL)": [glucose_value],
        "Notes": [notes],
    })
    st.session_state.data = pd.concat(
    [st.session_state.data, new_row], ignore_index=True
    )
    st.success("Saved!")

st.markdown("---")

# View history
st.subheader("History")
df = st.session_state.data

if df.empty:
    st.info("No entries yet. Add one above.")
else:
    # Show weights table and chart
    st.markdown("---")
    st.subheader("Trends")

    st.markdown("### Weight History")
    weight_table = df.set_index("Date")[["Weight (lbs)"]]
    st.table(weight_table)

    st.markdown("### A1c (%)")
    a1c_table = df.set_index("Date")[["A1c (%)"]]
    st.table(a1c_table)

    st.markdown("### Glucose (mL/dL)")
    glucose_table = df.set_index("Date")[["Glucose (mL/dL)"]]
    st.table(glucose_table)

if st.button("Clear All Data"):
    st.session_state.data = pd.DataFrame(
    columns=["Date", "Weight (lbs)", "A1c (%)", "Notes"]
    )
    st.rerun()
