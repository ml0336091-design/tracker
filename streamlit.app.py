import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Dad's Tracker", page_icon="📉", layout="centered")

# Simple storage in session
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(
        columns=["Date", "Weight (lbs)", "A1c (%)", "Notes"]
)

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
    weight_chart = df.set_index("Date")[["Weight (lbs)"]]
    st.line_chart(weight_chart)

    st.markdown("### A1c (%)")
    a1c_chart = df.set_index("Date")[["A1c (%)"]]
    st.line_chart(a1c_chart)

    st.markdown("### Glucose (mL/dL)")
    glucose_chart = df.set_index("Date")[["Glucose (mL/dL)"]]
    st.line_chart(glucose_chart)

if st.button("Clear All Data"):
    st.session_state.data = pd.DataFrame(
    columns=["Date", "Weight (lbs)", "A1c (%)", "Notes"]
    )
    st.rerun()