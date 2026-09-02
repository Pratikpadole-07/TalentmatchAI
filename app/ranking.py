import os
from typing import Dict, List

from sklearn.metrics.pairwise import cosine_similarity

from app.embedding import embedding_model
from app.parser import extract_text
from app.preprocess import preprocess_text
from app.skills import (
    extract_skills,
    compare_skills,
    skill_match_score,
)


# ---------------------------------------------------
# Prepare Job Description
# ---------------------------------------------------

def prepare_job_description(jd_path: str):

    raw_text = extract_text(jd_path)

    clean_text = preprocess_text(raw_text)

    embedding = embedding_model.generate_embedding(
        clean_text
    )

    skills = extract_skills(clean_text)

    return {
        "embedding": embedding,
        "skills": skills
    }


# ---------------------------------------------------
# Semantic Similarity
# ---------------------------------------------------

def semantic_similarity(
    resume_embedding,
    jd_embedding
):

    score = cosine_similarity(
        [resume_embedding],
        [jd_embedding]
    )[0][0]

    return round(score * 100, 2)


# ---------------------------------------------------
# Final Score
# ---------------------------------------------------

def final_score(
    semantic_score,
    skill_score,
    semantic_weight=0.7,
    skill_weight=0.3
):

    return round(

        semantic_score * semantic_weight +

        skill_score * skill_weight,

        2
    )


# ---------------------------------------------------
# Rank Resumes
# ---------------------------------------------------

def rank_resumes(
    resume_folder: str,
    jd_path: str
):

    jd = prepare_job_description(
        jd_path
    )

    resume_names = []

    resume_texts = []

    resume_skills = []

    # -----------------------------
    # Read every resume once
    # -----------------------------

    for file in os.listdir(resume_folder):

        if not file.endswith(".pdf"):
            continue

        path = os.path.join(
            resume_folder,
            file
        )

        raw = extract_text(path)

        clean = preprocess_text(raw)

        skills = extract_skills(clean)

        resume_names.append(file)

        resume_texts.append(clean)

        resume_skills.append(skills)

    # -----------------------------
    # Batch Embedding Generation
    # -----------------------------

    embeddings = embedding_model.generate_embeddings(
        resume_texts
    )

    # -----------------------------
    # Ranking
    # -----------------------------

    results = []

    for i in range(len(resume_names)):

        semantic = semantic_similarity(

            embeddings[i],

            jd["embedding"]

        )

        comparison = compare_skills(

            resume_skills[i],

            jd["skills"]

        )

        skill = skill_match_score(

            resume_skills[i],

            jd["skills"]

        )

        score = final_score(

            semantic,

            skill

        )

        results.append({

            "resume": resume_names[i],

            "semantic_score": semantic,

            "skill_score": skill,

            "final_score": score,

            "matched_skills":
            comparison["matched"],

            "missing_skills":
            comparison["missing"],

            "extra_skills":
            comparison["extra"]

        })

    results.sort(

        key=lambda x: x["final_score"],

        reverse=True

    )

    return results