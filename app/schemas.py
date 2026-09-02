from typing import List

from pydantic import BaseModel


class UploadResponse(BaseModel):
    message: str
    filename: str


class MultipleUploadResponse(BaseModel):
    uploaded_files: List[str]


class ResumeRanking(BaseModel):
    resume: str
    semantic_score: float
    skill_score: float
    final_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    extra_skills: List[str]


class RankingResponse(BaseModel):
    total_candidates: int
    ranking: List[ResumeRanking]