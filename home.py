import streamlit as st
import requests

# Set layout and title
st.set_page_config(page_title="Agentic HR", layout="wide")
st.title("Agentic HR")
st.markdown("You AI assistant for hiring problems.")

response = requests.get("http://127.0.0.1:8080/AgenticHR/load-all-jobs")
jobs = response.json()

# -------- Sidebar Filters --------
st.sidebar.header("Filters")
experience_options = ["All"] + sorted(list(set(job["experience_level"] for job in jobs)))
location_options = ["All"] + sorted(list(set(job["location"] for job in jobs)))

selected_level = st.sidebar.selectbox("Experience Level", experience_options)
selected_location = st.sidebar.selectbox("Location", location_options)

# -------- Filter Logic --------
filtered_jobs = [
    job for job in jobs
    if (selected_level == "All" or job["experience_level"] == selected_level)
    and (selected_location == "All" or job["location"] == selected_location)
]

# -------- Show Job Cards --------
st.markdown("### Active Jobs")
cols = st.columns(3)

for i, job in enumerate(filtered_jobs):
    with cols[i % 3]:
        with st.container(border=True):
            st.subheader(job["title"])
            st.text(f"Level: {job['experience_level']}")
            st.text(f"Location: {job['location']}")
            st.text("Skills: " + ", ".join(job["skills"][:3]) + ("..." if len(job["skills"]) > 3 else ""))
            if st.button("View Details", key=f"btn_{job['job_id']}"):
                st.session_state["selected_job"] = job["job_id"]


# -------- Job Detail Viewer --------
if "selected_job" in st.session_state:
    selected = next((j for j in jobs if j["job_id"] == st.session_state["selected_job"]), None)
    if selected:
        st.markdown("---")
        st.subheader(f"{selected['title']} ({selected['experience_level']} - {selected['location']})")
        st.markdown("**Description**")
        st.markdown(selected["description"])
        st.markdown("**Required Skills**")
        st.markdown(", ".join(selected["skills"]))
        if st.button("Close"):
            del st.session_state["selected_job"]

st.markdown("---")

if "selected_job" in st.session_state:
    selected_job_id = st.session_state["selected_job"]
    if st.button("View Candidates for Selected Job"):
        st.session_state["selected_job_id"] = selected_job_id
        st.session_state["selected_job_details"] = selected
        st.switch_page("pages/viewCandidates.py")
else:
    st.info("Select a job to enable candidate viewing.")
