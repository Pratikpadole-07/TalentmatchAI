import streamlit as st
import requests
import pandas as pd


# ============================================================
# CONFIG
# ============================================================

import os

API_URL = st.secrets.get(
    "API_URL",
    os.getenv("API_URL", "http://127.0.0.1:8000")
)

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="TalentMatch AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.stApp {
    background: #0f1117;
}

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

h1, h2, h3, h4 {
    color: #ffffff !important;
}


/* SIDEBAR */

section[data-testid="stSidebar"] {
    background: #151821;
    border-right: 1px solid #292d38;
}


/* METRICS */

div[data-testid="metric-container"] {
    background: #181b24;
    border: 1px solid #292d38;
    border-radius: 14px;
    padding: 18px;
}


/* BUTTONS */

.stButton > button {
    width: 100%;
    min-height: 44px;
    border-radius: 9px;
    font-weight: 600;
}


/* FILE UPLOADER */

section[data-testid="stFileUploaderDropzone"] {
    background: #181b24;
    border: 1px dashed #454b5a;
    border-radius: 12px;
}


/* CARDS */

.upload-card {
    background: #181b24;
    border: 1px solid #292d38;
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 10px;
}

.candidate-card {
    background: #181b24;
    border: 1px solid #292d38;
    border-radius: 16px;
    padding: 22px;
    margin-top: 15px;
    margin-bottom: 15px;
}


/* TEXT */

.muted {
    color: #8b92a3;
}

.section-label {
    color: #8b92a3;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1.5px;
    margin-bottom: 5px;
}


/* SCORE */

.score {
    font-size: 30px;
    font-weight: 800;
    color: #6ee7b7;
}

.rank {
    color: #8b92a3;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 1px;
}


/* SKILLS */

.skill {
    display: inline-block;
    padding: 6px 11px;
    margin: 3px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 500;
}

.skill-matched {
    background: #123b2d;
    color: #6ee7b7;
}

.skill-missing {
    background: #422024;
    color: #ff8c94;
}

.skill-extra {
    background: #252d42;
    color: #9db7ff;
}


/* STATUS */

.status-online {
    background: #123b2d;
    border: 1px solid #1f6048;
    color: #6ee7b7;
    padding: 12px;
    border-radius: 10px;
    text-align: center;
    font-weight: 600;
}

.status-offline {
    background: #422024;
    border: 1px solid #67343b;
    color: #ff8c94;
    padding: 12px;
    border-radius: 10px;
    text-align: center;
    font-weight: 600;
}


/* HERO */

.hero {
    padding: 10px 0 30px 0;
}

.hero-label {
    color: #8b92a3;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 2px;
    margin-bottom: 8px;
}

.hero-title {
    color: #ffffff;
    font-size: 46px;
    font-weight: 800;
    line-height: 1.1;
    margin: 0;
}

.hero-description {
    color: #8b92a3;
    font-size: 16px;
    margin-top: 10px;
}


/* EMPTY STATE */

.empty-state {
    text-align: center;
    padding: 70px 20px;
    background: #181b24;
    border: 1px solid #292d38;
    border-radius: 18px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

if "results" not in st.session_state:
    st.session_state.results = None


# ============================================================
# API FUNCTIONS
# ============================================================

def check_backend():

    try:

        response = requests.get(
            f"{API_URL}/",
            timeout=5
        )

        return response.status_code == 200

    except requests.exceptions.RequestException:

        return False


def upload_jd(file):

    try:

        response = requests.post(
            f"{API_URL}/upload_jd",
            files={
                "file": (
                    file.name,
                    file.getvalue(),
                    "application/pdf"
                )
            },
            timeout=60
        )

        return response

    except requests.exceptions.RequestException as e:

        return None


def upload_resumes(files):

    try:

        multipart_files = []

        for file in files:

            multipart_files.append(
                (
                    "files",
                    (
                        file.name,
                        file.getvalue(),
                        "application/pdf"
                    )
                )
            )

        response = requests.post(
            f"{API_URL}/upload_resumes",
            files=multipart_files,
            timeout=120
        )

        return response

    except requests.exceptions.RequestException:

        return None


def get_rankings():

    try:

        response = requests.get(
            f"{API_URL}/rank_candidates",
            timeout=180
        )

        return response

    except requests.exceptions.RequestException:

        return None


# ============================================================
# DATA HELPERS
# ============================================================

def get_value(candidate, keys, default=None):

    for key in keys:

        if key in candidate:
            return candidate[key]

    return default


def get_score(candidate):

    value = get_value(
        candidate,
        [
            "score",
            "match_score",
            "match_percentage",
            "skill_match_score",
            "similarity_score"
        ],
        0
    )

    try:

        return float(value)

    except:

        return 0.0


def get_candidate_name(candidate, index):

    return get_value(
        candidate,
        [
            "candidate_name",
            "name",
            "filename",
            "resume",
            "resume_name",
            "file_name"
        ],
        f"Candidate {index + 1}"
    )


def get_skills(candidate, keys):

    value = get_value(
        candidate,
        keys,
        []
    )

    if value is None:
        return []

    if isinstance(value, str):

        return [
            item.strip()
            for item in value.split(",")
            if item.strip()
        ]

    return value


def render_skills(skills, css_class):

    if not skills:

        st.caption("None")

        return

    html = ""

    for skill in skills:

        html += (
            f'<span class="skill {css_class}">'
            f'{skill}'
            f'</span>'
        )

    st.html(html)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "## 🤖 TalentMatch AI"
    )

    st.caption(
        "AI Powered Resume Screening"
    )

    st.divider()

    st.markdown("### Backend")

    if check_backend():

        st.markdown(
            """
            <div class="status-online">
                ● Backend Online
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            """
            <div class="status-offline">
                ● Backend Offline
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    st.markdown("### Workflow")

    st.caption("① Select Job Description")
    st.caption("② Select Candidate Resumes")
    st.caption("③ Analyze Candidates")
    st.caption("④ Review Ranking")

    st.divider()

    if st.session_state.results:

        st.success("✓ Analysis Complete")

    else:

        st.caption("○ Analysis Pending")

    st.divider()

    if st.button("🔄 Reset"):

        st.session_state.results = None

        st.rerun()


# ============================================================
# HERO
# ============================================================

st.html("""
<div class="hero">

    <div class="hero-label">
        AI RECRUITMENT PLATFORM
    </div>

    <div class="hero-title">
        TalentMatch AI
    </div>

    <div class="hero-description">
        Screen, compare and rank candidates using AI-powered
        resume matching.
    </div>

</div>
""")


# ============================================================
# UPLOAD WORKSPACE
# ============================================================

st.markdown(
    '<div class="section-label">RECRUITMENT WORKSPACE</div>',
    unsafe_allow_html=True
)

st.header("Upload Candidate Data")


col1, col2 = st.columns(
    2,
    gap="large"
)


# ============================================================
# JOB DESCRIPTION
# ============================================================

with col1:

    st.html("""
    <div class="upload-card">

        <h3>📄 Job Description</h3>

        <p class="muted">
            Upload the job description used to evaluate candidates.
        </p>

    </div>
    """)

    jd_file = st.file_uploader(
        "Upload Job Description PDF",
        type=["pdf"],
        key="jd_upload"
    )

    if jd_file:

        st.success(
            f"✓ {jd_file.name} selected"
        )

    else:

        st.caption(
            "Select one PDF job description."
        )


# ============================================================
# RESUMES
# ============================================================

with col2:

    st.html("""
    <div class="upload-card">

        <h3>👥 Candidate Resumes</h3>

        <p class="muted">
            Upload one or more candidate resumes.
        </p>

    </div>
    """)

    resume_files = st.file_uploader(
        "Upload Candidate Resumes",
        type=["pdf"],
        accept_multiple_files=True,
        key="resume_upload"
    )

    if resume_files:

        st.success(
            f"✓ {len(resume_files)} resume(s) selected"
        )

    else:

        st.caption(
            "Select at least one resume."
        )


# ============================================================
# READY CHECK
# ============================================================

st.divider()


files_ready = (
    jd_file is not None
    and
    resume_files is not None
    and
    len(resume_files) > 0
)


if files_ready:

    st.success(
        f"✓ Ready: 1 Job Description + "
        f"{len(resume_files)} Resume(s)"
    )

else:

    st.warning(
        "Select a job description and at least one resume."
    )


# ============================================================
# ANALYZE BUTTON
# ============================================================

if st.button(
    "🚀 Analyze & Rank Candidates",
    type="primary",
    disabled=not files_ready,
    use_container_width=True
):

    # ========================================================
    # ANALYSIS PROCESS
    # ========================================================

    with st.status(
        "Running TalentMatch AI...",
        expanded=True
    ) as status:

        # ----------------------------------------------------
        # Upload JD
        # ----------------------------------------------------

        st.write(
            "📄 Uploading Job Description..."
        )

        jd_response = upload_jd(
            jd_file
        )


        if jd_response is None:

            status.update(
                label="Backend connection failed",
                state="error"
            )

            st.error(
                "Cannot connect to FastAPI. "
                "Make sure Uvicorn is running."
            )

            st.stop()


        if jd_response.status_code != 200:

            status.update(
                label="Job Description upload failed",
                state="error"
            )

            st.error(
                jd_response.text
            )

            st.stop()


        st.write(
            "✓ Job Description uploaded"
        )


        # ----------------------------------------------------
        # Upload Resumes
        # ----------------------------------------------------

        st.write(
            f"👥 Uploading {len(resume_files)} resume(s)..."
        )

        resume_response = upload_resumes(
            resume_files
        )


        if resume_response is None:

            status.update(
                label="Resume upload failed",
                state="error"
            )

            st.error(
                "Cannot connect to FastAPI."
            )

            st.stop()


        if resume_response.status_code != 200:

            status.update(
                label="Resume upload failed",
                state="error"
            )

            st.error(
                resume_response.text
            )

            st.stop()


        resume_data = resume_response.json()

        uploaded_files = resume_data.get(
            "uploaded_files",
            []
        )


        st.write(
            f"✓ {len(uploaded_files)} resume(s) uploaded"
        )


        # ----------------------------------------------------
        # Run Ranking
        # ----------------------------------------------------

        st.write(
            "🤖 Running AI candidate matching..."
        )

        ranking_response = get_rankings()


        if ranking_response is None:

            status.update(
                label="Analysis failed",
                state="error"
            )

            st.error(
                "Cannot connect to FastAPI."
            )

            st.stop()


        if ranking_response.status_code != 200:

            status.update(
                label="Candidate analysis failed",
                state="error"
            )

            st.error(
                ranking_response.text
            )

            st.stop()


        # ----------------------------------------------------
        # Store Results
        # ----------------------------------------------------

        st.session_state.results = (
            ranking_response.json()
        )


        status.update(
            label="Analysis completed successfully",
            state="complete"
        )


    st.rerun()


# ============================================================
# RESULTS
# ============================================================

if st.session_state.results:

    data = st.session_state.results

    ranking = data.get(
        "ranking",
        []
    )

    total_candidates = data.get(
        "total_candidates",
        len(ranking)
    )


    st.divider()

    st.markdown(
        '<div class="section-label">AI ANALYSIS</div>',
        unsafe_allow_html=True
    )

    st.header(
        "Candidate Intelligence"
    )


    # ========================================================
    # METRICS
    # ========================================================

    scores = [
        get_score(candidate)
        for candidate in ranking
    ]


    average_score = (
        sum(scores) / len(scores)
        if scores
        else 0
    )


    top_score = (
        max(scores)
        if scores
        else 0
    )


    strong_matches = sum(
        1
        for score in scores
        if score >= 70
    )


    m1, m2, m3, m4 = st.columns(4)


    with m1:

        st.metric(
            "Candidates",
            total_candidates
        )


    with m2:

        st.metric(
            "Top Match",
            f"{top_score:.1f}%"
        )


    with m3:

        st.metric(
            "Average Match",
            f"{average_score:.1f}%"
        )


    with m4:

        st.metric(
            "Strong Matches",
            strong_matches
        )


    # ========================================================
    # SEARCH / FILTER
    # ========================================================

    st.divider()

    st.subheader(
        "Candidate Ranking"
    )


    filter_col1, filter_col2 = st.columns(
        [2, 1]
    )


    with filter_col1:

        search = st.text_input(
            "Search Candidate",
            placeholder="🔎 Search by candidate name..."
        )


    with filter_col2:

        minimum_score = st.slider(
            "Minimum Match Score",
            min_value=0,
            max_value=100,
            value=0
        )


    # ========================================================
    # FILTER RESULTS
    # ========================================================

    filtered_candidates = []


    for index, candidate in enumerate(
        ranking
    ):

        name = get_candidate_name(
            candidate,
            index
        )

        score = get_score(
            candidate
        )


        if score < minimum_score:

            continue


        if search:

            if search.lower() not in str(
                name
            ).lower():

                continue


        filtered_candidates.append(
            (index, candidate)
        )


    # ========================================================
    # RANKING TABLE
    # ========================================================

    table_rows = []


    for index, candidate in filtered_candidates:

        name = get_candidate_name(
            candidate,
            index
        )

        score = get_score(
            candidate
        )


        matched = get_skills(
            candidate,
            [
                "matched_skills",
                "matched"
            ]
        )


        missing = get_skills(
            candidate,
            [
                "missing_skills",
                "missing"
            ]
        )


        table_rows.append(
            {
                "Rank": index + 1,
                "Candidate": name,
                "Match": f"{score:.1f}%",
                "Matched Skills": len(matched),
                "Missing Skills": len(missing)
            }
        )


    if table_rows:

        df = pd.DataFrame(
            table_rows
        )


        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )


        csv = df.to_csv(
            index=False
        ).encode("utf-8")


        st.download_button(
            "⬇️ Download Ranking CSV",
            data=csv,
            file_name="candidate_ranking.csv",
            mime="text/csv"
        )


    else:

        st.info(
            "No candidates match your current filters."
        )


    # ========================================================
    # CANDIDATE DETAILS
    # ========================================================

    st.divider()

    st.subheader(
        "Candidate Details"
    )


    for index, candidate in filtered_candidates:

        name = get_candidate_name(
            candidate,
            index
        )


        score = get_score(
            candidate
        )


        matched = get_skills(
            candidate,
            [
                "matched_skills",
                "matched"
            ]
        )


        missing = get_skills(
            candidate,
            [
                "missing_skills",
                "missing"
            ]
        )


        extra = get_skills(
            candidate,
            [
                "extra_skills",
                "extra"
            ]
        )


        # ----------------------------------------------------
        # CANDIDATE CARD
        # ----------------------------------------------------

        st.html(
            f"""
            <div class="candidate-card">

                <div style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                ">

                    <div>

                        <div class="rank">
                            RANK #{index + 1}
                        </div>

                        <div style="
                            font-size:24px;
                            font-weight:700;
                            color:white;
                            margin-top:5px;
                        ">
                            {name}
                        </div>

                    </div>

                    <div class="score">
                        {score:.1f}%
                    </div>

                </div>

            </div>
            """
        )


        # ----------------------------------------------------
        # SCORE BAR
        # ----------------------------------------------------

        st.progress(
            min(
                max(score / 100, 0),
                1
            )
        )


        # ----------------------------------------------------
        # SKILLS
        # ----------------------------------------------------

        skill_col1, skill_col2, skill_col3 = st.columns(3)


        with skill_col1:

            st.markdown(
                "### 🟢 Matched Skills"
            )

            render_skills(
                matched,
                "skill-matched"
            )


        with skill_col2:

            st.markdown(
                "### 🔴 Missing Skills"
            )

            render_skills(
                missing,
                "skill-missing"
            )


        with skill_col3:

            st.markdown(
                "### 🔵 Additional Skills"
            )

            render_skills(
                extra,
                "skill-extra"
            )


        # ----------------------------------------------------
        # RAW DATA
        # ----------------------------------------------------

        with st.expander(
            "View complete candidate data"
        ):

            st.json(
                candidate
            )


# ============================================================
# EMPTY STATE
# ============================================================

else:

    st.divider()

    st.html("""
    <div class="empty-state">

        <div style="
            font-size:55px;
            margin-bottom:15px;
        ">
            🤖
        </div>

        <div style="
            color:white;
            font-size:28px;
            font-weight:700;
        ">
            Ready to screen candidates
        </div>

        <div style="
            color:#8b92a3;
            margin-top:10px;
            font-size:15px;
        ">
            Upload a job description and candidate resumes
            to generate AI-powered rankings.
        </div>

    </div>
    """)