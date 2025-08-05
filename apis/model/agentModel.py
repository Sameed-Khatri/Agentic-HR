from pydantic import BaseModel
from typing import List, Optional

class CandidateModel(BaseModel):
    job_id: str
    top_n: int = 5

class JobDetail(BaseModel):
    job_id: str
    title: str
    description: str
    experience_level: str
    skills: List[str]
    location: Optional[str] = None
    source: Optional[str] = None
    seq_num: Optional[int] = None

class Candidate(BaseModel):
    application_id: str
    job_id: str
    name: str
    email: str
    years_experience: float
    skills: List[str]
    education: Optional[str] = None
    current_title: Optional[str] = None
    location: Optional[str] = None
    experience_level: Optional[str] = None
    description: str
    score: float
    source: Optional[str] = None
    seq_num: Optional[int] = None

class GraphRequest(BaseModel):
    query: str
    job_id: str
    job_details: List[JobDetail]
    candidates: List[Candidate]
    thread_id: str
    mode: str