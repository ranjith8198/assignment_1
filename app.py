import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="SecureCheck Dashboard", layout="wide")

# ---------------- DATABASE CONNECTION ----------------
engine = create_engine(
    "postgresql://postgres:ranjith@localhost:5432/securecheck"
)

# ---------------- LOAD DATA ----------------
df = pd.read_sql("SELECT * FROM traffic_stops", engine)

# ---------------- DATA CLEANING ----------------
df["hour"] = df["stop_time"].astype(str).str[:2].astype(int)
df["stop_date"] = pd.to_datetime(df["stop_date"])

df["age_group"] = pd.cut(
    df["driver_age"],
    bins=[15,25,40,60,100],
    labels=["<25","25-40","40-60","60+"]
)

# ---------------- TITLE ----------------
st.title("🚓 SecureCheck: Police Traffic Stop Dashboard")

# ---------------- KEY METRICS ----------------
c1, c2, c3 = st.columns(3)

c1.metric("Total Stops", len(df))
c2.metric("Drug Related Stops", int(df["drugs_related_stop"].sum()))
c3.metric("Total Arrests", int(df["is_arrested"].sum()))

# ---------------- ADD NEW STOP & PREDICT ----------------
st.subheader("🚓 Add New Traffic Stop & Predict Outcome")

with st.form("new_stop_form"):

    driver_gender = st.selectbox(
        "Driver Gender",
        df["driver_gender"].dropna().unique()
    )

    driver_age = st.number_input(
        "Driver Age",
        min_value=16,
        max_value=100,
        value=25
    )

    search_conducted = st.selectbox(
        "Search Conducted",
        [True, False]
    )

    drugs_related_stop = st.selectbox(
        "Drugs Related Stop",
        [True, False]
    )

    stop_duration = st.selectbox(
        "Stop Duration",
        df["stop_duration"].dropna().unique()
    )

    submitted = st.form_submit_button("Predict Stop Outcome & Violation")

# ---------------- PREDICTION ----------------
if submitted:

    filtered = df[
        (df["driver_gender"] == driver_gender) &
        (df["driver_age"] == driver_age) &
        (df["search_conducted"] == search_conducted) &
        (df["stop_duration"] == stop_duration) &
        (df["drugs_related_stop"] == drugs_related_stop)
    ]

    if not filtered.empty:
        predicted_outcome = filtered["stop_outcome"].mode()[0]
        predicted_violation = filtered["violation"].mode()[0]
    else:
        predicted_outcome = "No matching record"
        predicted_violation = "No matching record"

    st.success(f"Predicted Stop Outcome: {predicted_outcome}")
    st.success(f"Predicted Violation: {predicted_violation}")

# ---------------- VEHICLE SEARCH ----------------
st.subheader("🔍 Search by Vehicle Number")

vehicle_no = st.text_input("Enter Vehicle Number")

if vehicle_no:
    result = df[df["vehicle_number"].str.contains(vehicle_no, case=False, na=False)]
    st.dataframe(result)

    st.subheader("Traffic Stop Summary Generator")

record_id = st.number_input("Enter Record ID", min_value=0, step=1)

if st.button("Generate Stop Summary"):

    record = df.iloc[int(record_id)]

    age = record["driver_age"]
    gender = record["driver_gender"]
    violation = record["violation"]
    time = record["stop_time"]
    search = record["search_conducted"]
    outcome = record["stop_outcome"]
    duration = record["stop_duration"]
    drugs = record["drugs_related_stop"]

    search_text = "A search was conducted" if search else "No search was conducted"
    drugs_text = "drug-related" if drugs else "not drug-related"

    sentence = f"""
    A {age}-year-old {gender} driver was stopped for {violation} at {time}.
    {search_text}, and the driver received {outcome}.
    The stop lasted {duration} and was {drugs_text}.
    """

    st.success(sentence)

# ---------------- VEHICLE BASED ANALYSIS ----------------
st.header("🚗 Vehicle Based Insights")

st.subheader("Top 10 Vehicles in Drug Related Stops")

drug_vehicle = (
    df[df["drugs_related_stop"] == True]["vehicle_number"]
    .value_counts()
    .head(10)
)

st.dataframe(drug_vehicle)

st.subheader("Vehicles Most Frequently Searched")

searched_vehicle = (
    df[df["search_conducted"] == True]["vehicle_number"]
    .value_counts()
    .head(10)
)

st.dataframe(searched_vehicle)

# ---------------- DEMOGRAPHIC ANALYSIS ----------------
st.header("🧍 Driver Demographics")

st.subheader("Arrest Rate by Age Group")

age_arrest = df.groupby("age_group", observed=False)["is_arrested"].mean()
st.bar_chart(age_arrest)

st.subheader("Gender Distribution by Country")

gender_country = (
    df.groupby(["country_name","driver_gender"])
    .size()
    .unstack()
)

st.dataframe(gender_country)

st.subheader("Race and Gender with Highest Search Rate")

race_gender_search = (
    df.groupby(["driver_race","driver_gender"])["search_conducted"]
    .mean()
    .sort_values(ascending=False)
)

st.dataframe(race_gender_search)

# ---------------- TIME ANALYSIS ----------------
st.header("🕒 Time Based Analysis")

st.subheader("Stops by Hour of Day")

hour_stops = df["hour"].value_counts().sort_index()
st.line_chart(hour_stops)

st.subheader("Night Stops vs Arrests")

df["time_period"] = df["hour"].apply(
    lambda x: "Night" if x >= 18 or x <= 6 else "Day"
)

night_arrest = df.groupby("time_period")["is_arrested"].mean()

st.bar_chart(night_arrest)

# ---------------- VIOLATION ANALYSIS ----------------
st.header("⚖️ Violation Insights")

st.subheader("Violations Associated with Searches")

violation_search = (
    df.groupby("violation")["search_conducted"]
    .mean()
    .sort_values(ascending=False)
)

st.dataframe(violation_search)

st.subheader("Violations Common Among Drivers <25")

young_violation = (
    df[df["driver_age"] < 25]["violation"]
    .value_counts()
)

st.dataframe(young_violation)

st.subheader("Violations Rarely Leading to Search or Arrest")

rare_violation = (
    df.groupby("violation")[["search_conducted","is_arrested"]]
    .mean()
)

st.dataframe(rare_violation)

# ---------------- LOCATION ANALYSIS ----------------
st.header("🌍 Location Based Analysis")

st.subheader("Countries with Highest Drug Stops")

country_drug = (
    df.groupby("country_name")["drugs_related_stop"]
    .sum()
    .sort_values(ascending=False)
)

st.bar_chart(country_drug)

st.subheader("Arrest Rate by Country and Violation")

country_violation = (
    df.groupby(["country_name","violation"])["is_arrested"]
    .mean()
    .unstack()
)

st.dataframe(country_violation)

st.subheader("Countries with Most Searches")

country_search = (
    df.groupby("country_name")["search_conducted"]
    .sum()
    .sort_values(ascending=False)
)

st.bar_chart(country_search)

# ---------------- YEAR / MONTH / HOUR ANALYSIS ----------------
st.header("📊 Time Period Analysis")

st.subheader("Stops by Year")

year_stop = df["stop_date"].dt.year.value_counts().sort_index()
st.line_chart(year_stop)

st.subheader("Stops by Month")

month_stop = df["stop_date"].dt.month.value_counts().sort_index()
st.line_chart(month_stop)

st.subheader("Stops by Hour")

hour_stop = df["hour"].value_counts().sort_index()
st.line_chart(hour_stop)