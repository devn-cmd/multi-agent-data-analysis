import streamlit as st
import requests
import io

st.title("Multi-Agent Data Analyzer")
st.caption("Upload a CSV → 3 AI agents clean, analyze, and report automatically")

uploaded = st.file_uploader("Upload your CSV", type="csv")

if uploaded and st.button("Run Analysis"):
    with st.status("Running pipeline...", expanded=True) as status:
        st.write("Agent 1: Cleaning data...")
        st.write("Agent 2: Analyzing patterns...")
        st.write("Agent 3: Writing report...")

        response = requests.post(
            "http://localhost:8000/analyze",
            files={"file": (uploaded.name, uploaded.getvalue(), "text/csv")}
        )
        status.update(label="Done!", state="complete")

    if response.status_code == 200:
        data = response.json()
        st.subheader("Cleaning Summary")
        st.info(data["cleaning_summary"])
        st.subheader("Key Findings")
        st.write(data["findings"])
        st.subheader("Final Report")
        st.success(data["final_report"])
    else:
        st.error("Pipeline failed. Check the API logs.")