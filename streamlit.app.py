import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Tracker", page_icon="📉", layout="centered")

# Simple storage in session
try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    REPO_OWNER = st.secrets["REPO_OWNER"]
    REPO_NAME = st.secrets["REPO_NAME"]
except Exception:
    st.error("⚠️ GitHub Secrets are missing! Check the setup steps below.")
    st.stop()

FILE_PATH = "health_data.csv"
URL = f"https://github.com{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

def load_data_from_github():
    """Fetches the CSV file from your GitHub repository."""
    response = requests.get(URL, headers=HEADERS)
    if response.status_code == 200:
        # File exists, read its contents via the download URL
        download_url = response.json()["download_url"]
        return pd.read_csv(download_url)
    else:
        # File doesn't exist yet, return a blank dataframe
        return pd.DataFrame(columns=["Date", "Weight (lbs)", "A1c (%)", "Glucose (mL/dL)", "Notes"])

def save_data_to_github(dataframe):
    """Commits and pushes the updated CSV back to your GitHub repository."""
    csv_content = dataframe.to_csv(index=False)
    
    # Check if file already exists to get its unique 'sha' ID (required by GitHub API to update files)
    get_response = requests.get(URL, headers=HEADERS)
    sha = get_response.json().get("sha") if get_response.status_code == 200 else None
    
    payload = {
        "message": "Update health tracking data",
        "content": requests.utils.base64.b64encode(csv_content.encode("utf-8")).decode("utf-8")
    }
    if sha:
        payload["sha"] = sha
        
    put_response = requests.put(URL, headers=HEADERS, json=payload)
    return put_response.status_code in [200, 201]

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