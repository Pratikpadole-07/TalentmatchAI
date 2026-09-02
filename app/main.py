import os
import shutil

from fastapi import FastAPI, UploadFile, File, HTTPException

from app.config import RESUME_FOLDER, JD_FOLDER
from app.ranking import rank_resumes

from app.schemas import (
    UploadResponse,
    MultipleUploadResponse,
    RankingResponse,
)

from app.utils import (
    is_pdf,
    create_directory,
    logger,
)

# -------------------------------------------------------
# Create FastAPI App
# -------------------------------------------------------

app = FastAPI(
    title="TalentMatch AI",
    version="1.0.0",
    description="AI Powered Resume Screening System"
)

# -------------------------------------------------------
# Create Required Directories
# -------------------------------------------------------

create_directory(RESUME_FOLDER)
create_directory(JD_FOLDER)

# -------------------------------------------------------
# Home Endpoint
# -------------------------------------------------------


@app.get("/")
def home():

    return {
        "message": "TalentMatch AI API Running Successfully",
        "status": "Healthy"
    }


# -------------------------------------------------------
# Upload Single Resume
# -------------------------------------------------------


@app.post(
    "/upload_resume",
    response_model=UploadResponse
)
async def upload_resume(file: UploadFile = File(...)):

    if not is_pdf(file.filename):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    file_path = os.path.join(
        RESUME_FOLDER,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    logger.info(f"Uploaded Resume : {file.filename}")

    return UploadResponse(
        message="Resume uploaded successfully.",
        filename=file.filename
    )


# -------------------------------------------------------
# Upload Multiple Resumes
# -------------------------------------------------------


@app.post(
    "/upload_resumes",
    response_model=MultipleUploadResponse
)
async def upload_resumes(
    files: list[UploadFile] = File(...)
):

    uploaded_files = []

    for file in files:

        if not is_pdf(file.filename):
            continue

        file_path = os.path.join(
            RESUME_FOLDER,
            file.filename
        )

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        uploaded_files.append(file.filename)

        logger.info(f"Uploaded Resume : {file.filename}")

    return MultipleUploadResponse(
        uploaded_files=uploaded_files
    )


# -------------------------------------------------------
# Upload Job Description
# -------------------------------------------------------


@app.post(
    "/upload_jd",
    response_model=UploadResponse
)
async def upload_job_description(
    file: UploadFile = File(...)
):

    if not is_pdf(file.filename):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    file_path = os.path.join(
        JD_FOLDER,
        "job_description.pdf"
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    logger.info("Job Description Uploaded")

    return UploadResponse(
        message="Job Description uploaded successfully.",
        filename="job_description.pdf"
    )


# -------------------------------------------------------
# Rank Candidates
# -------------------------------------------------------


@app.get(
    "/rank_candidates",
    response_model=RankingResponse
)
async def rank_candidates():

    jd_path = os.path.join(
        JD_FOLDER,
        "job_description.pdf"
    )

    if not os.path.exists(jd_path):
        raise HTTPException(
            status_code=404,
            detail="Please upload Job Description first."
        )

    results = rank_resumes(
        RESUME_FOLDER,
        jd_path
    )

    logger.info("Candidate Ranking Completed")

    return RankingResponse(
        total_candidates=len(results),
        ranking=results
    )