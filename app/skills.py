"""
skills.py

Handles:
1. Loading predefined skills
2. Extracting skills from text
3. Comparing resume skills with JD skills
4. Calculating skill match score
"""

from pathlib import Path
from typing import List, Dict

import pandas as pd

# ------------------------------------------------------------------
# Load Skills Database
# ------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
SKILLS_FILE = BASE_DIR / "data" / "skills.csv"

try:
    skills_df = pd.read_csv(SKILLS_FILE)

    if "Skill" not in skills_df.columns:
        raise ValueError("skills.csv must contain a 'Skill' column.")

    SKILLS = (
        skills_df["Skill"]
        .dropna()
        .astype(str)
        .str.strip()
        .tolist()
    )

except Exception as e:
    print(f"Error loading skills database: {e}")
    SKILLS = []


# ------------------------------------------------------------------
# Extract Skills
# ------------------------------------------------------------------

def extract_skills(text: str) -> List[str]:
    """
    Extract predefined skills from text.

    Parameters
    ----------
    text : str
        Resume or Job Description text

    Returns
    -------
    List[str]
        List of detected skills
    """

    if not text:
        return []

    text = text.lower()

    detected_skills = []

    for skill in SKILLS:
        if skill.lower() in text:
            detected_skills.append(skill)

    return sorted(list(set(detected_skills)))


# ------------------------------------------------------------------
# Compare Skills
# ------------------------------------------------------------------

def compare_skills(
    resume_skills: List[str],
    jd_skills: List[str]
) -> Dict:
    """
    Compare Resume skills against JD skills.
    """

    resume_set = set(resume_skills)
    jd_set = set(jd_skills)

    matched = sorted(list(resume_set & jd_set))
    missing = sorted(list(jd_set - resume_set))
    extra = sorted(list(resume_set - jd_set))

    return {
        "matched": matched,
        "missing": missing,
        "extra": extra
    }


# ------------------------------------------------------------------
# Skill Match Score
# ------------------------------------------------------------------

def skill_match_score(
    resume_skills: List[str],
    jd_skills: List[str]
) -> float:
    """
    Calculate skill matching percentage.

    Formula

    matched skills
    ------------------ × 100
    total JD skills
    """

    if len(jd_skills) == 0:
        return 0.0

    matched = len(set(resume_skills) & set(jd_skills))

    score = (matched / len(jd_skills)) * 100

    return round(score, 2)


# ------------------------------------------------------------------
# Complete Skill Analysis
# ------------------------------------------------------------------

def analyze_skill_match(
    resume_text: str,
    jd_text: str
) -> Dict:
    """
    Complete pipeline.

    Extract skills

    Compare skills

    Calculate score
    """

    resume_skills = extract_skills(resume_text)

    jd_skills = extract_skills(jd_text)

    comparison = compare_skills(
        resume_skills,
        jd_skills
    )

    score = skill_match_score(
        resume_skills,
        jd_skills
    )

    return {
        "resume_skills": resume_skills,
        "jd_skills": jd_skills,
        "matched_skills": comparison["matched"],
        "missing_skills": comparison["missing"],
        "extra_skills": comparison["extra"],
        "skill_match_score": score
    }


# ------------------------------------------------------------------
# Testing
# ------------------------------------------------------------------

if __name__ == "__main__":

    resume = """
    Python
    SQL
    FastAPI
    Docker
    Git
    Machine Learning
    """

    jd = """
    Python
    Docker
    AWS
    FastAPI
    Machine Learning
    """

    result = analyze_skill_match(
        resume,
        jd
    )

    print("\nResume Skills")
    print(result["resume_skills"])

    print("\nJD Skills")
    print(result["jd_skills"])

    print("\nMatched Skills")
    print(result["matched_skills"])

    print("\nMissing Skills")
    print(result["missing_skills"])

    print("\nExtra Skills")
    print(result["extra_skills"])

    print("\nSkill Match Score")
    print(result["skill_match_score"], "%")