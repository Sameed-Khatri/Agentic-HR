import streamlit as st
import requests
import uuid

# ---------- PAGE SETUP ----------
st.set_page_config(page_title="View Candidates", layout="wide")
st.title("Top Candidates + AI Assistant")

st.sidebar.header("Agent Thread")

# Generate thread_id if not set
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

st.sidebar.code(st.session_state.thread_id, language="text")

# Button to regenerate thread_id
if st.sidebar.button("Generate New Thread ID"):
    st.session_state.thread_id = str(uuid.uuid4())

# ---------- JOB CONTEXT ----------
if "selected_job_id" not in st.session_state:
    st.error("No job selected. Go back and select a job.")
    st.stop()

job_id = st.session_state["selected_job_id"]

# ---------- TOP-N CONTROL ----------
st.sidebar.header("Candidate Controls")
top_n = st.sidebar.slider("How many candidates to show?", min_value=1, max_value=20, value=5)

# ---------- FETCH CANDIDATES ----------
@st.cache_data(show_spinner=False)
def fetch_candidates(job_id, n):
    response = requests.get(f"http://127.0.0.1:8080/AgenticHR/get-candidates/{job_id}/{n}")
    if response.status_code == 200:
        return response.json()
    return []

candidates = fetch_candidates(job_id, top_n)

if "candidates_details" not in st.session_state:
    st.session_state.candidates_details = {cand["application_id"]: cand for cand in candidates}

# ---------- INIT SELECTED STATE ----------
if "selected_candidate_ids" not in st.session_state:
    st.session_state.selected_candidate_ids = set()

# ---------- SELECT ALL / DESELECT BUTTONS ----------
col1, col2, col3 = st.columns([6, 1, 1])

with col1:
    st.markdown(f"### Top {top_n} Candidates for Job ID: `{job_id}`")

with col2:
    if st.button("✅ Select All"):
        for cand in candidates:
            st.session_state[f"cand_checkbox_{cand['application_id']}"] = True
        st.session_state.selected_candidate_ids = {c["application_id"] for c in candidates}

with col3:
    if st.button("❌ Deselect All"):
        for cand in candidates:
            st.session_state[f"cand_checkbox_{cand['application_id']}"] = False
        st.session_state.selected_candidate_ids = set()
        

# ---------- DISPLAY CANDIDATES ----------
cols = st.columns(3)
for i, candidate in enumerate(candidates):
    key = f"cand_checkbox_{candidate['application_id']}"

    with cols[i % 3]:
        with st.container(border=True):
            st.subheader(candidate["name"])
            st.text(f"Application No: {candidate['application_id']}")
            st.text(f"Experience: {candidate['years_experience']} years")
            st.text(f"Experience Level: {candidate['experience_level']}")
            st.text(f"Skills: {', '.join(candidate['skills'])}")
            st.text(f"Score: {candidate['score']}")
            
            checked = st.checkbox("Select for Analysis", key=key)

            if checked:
                st.session_state.selected_candidate_ids.add(candidate["application_id"])
                if candidate["application_id"] not in st.session_state.candidates_details:
                    st.session_state.candidates_details[candidate["application_id"]] = candidate
            else:
                st.session_state.selected_candidate_ids.discard(candidate["application_id"])
                if candidate["application_id"] in st.session_state.candidates_details:
                    del st.session_state.candidates_details[candidate["application_id"]]

# ---------- SIDEBAR: SELECTED CANDIDATES ----------
st.sidebar.markdown("### Selected Candidates")
selected_cands = [
    cand for cand in candidates if cand["application_id"] in st.session_state.selected_candidate_ids
]

if selected_cands:
    for cand in selected_cands:
        st.sidebar.markdown(f"- **{cand['name']}** (`{cand['application_id']}`)")
else:
    st.sidebar.info("No candidates selected.")

# ---------- AI CHATBOT ----------
st.markdown("---")
st.markdown("### AI Assistant")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.chat_input("Ask the AI about selected candidates for this job...")

# Show chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    ai_placeholder = st.chat_message("ai")
    with ai_placeholder:
        spinner_area = st.empty()
        spinner_area.markdown("🤔 Thinking...")

    selected_candidates = [
        st.session_state.candidates_details[candidate_id]
        for candidate_id in st.session_state.selected_candidate_ids
    ]

    payload = {
        "query": user_input,
        "job_id": job_id,
        "job_details": [st.session_state["selected_job_details"]],
        "candidates": selected_candidates,
        "thread_id": st.session_state.thread_id,
        "mode": "BEGIN"
    }

    try:
        # Make the API call to the FastAPI backend
        response = requests.post("http://127.0.0.1:8080/AgenticHR/invoke-agents", json=payload)

        if response.status_code == 200:
            ai_response = response.json()
        else:
            ai_response = "Error: Unable to fetch response from the agent."

    except Exception as e:
        ai_response = f"Error: {str(e)}"

    spinner_area.markdown(ai_response if isinstance(ai_response, str) else str(ai_response))
    # Append AI's response to the chat history
    st.session_state.chat_history.append({"role": "ai", "content": ai_response})
