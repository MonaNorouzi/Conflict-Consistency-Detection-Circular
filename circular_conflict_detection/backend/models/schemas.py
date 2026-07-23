from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class DocType(str, Enum):
    UPSTREAM = "بالادستی/نظارتی"
    INTERNAL = "داخلی"

class ConflictType(str, Enum):
    FULL_CONFLICT = "تعارض کامل"
    FULL_CONFLIC = "تعارض کامل"
    HIERARCHICAL_CONFLICT = "تعارض کامل (سلسله‌مراتبی)"
    INTER_DEPARTMENTAL = "تعارض کامل (بین واحدی، بدون اولویت مشخص)"
    PARTIAL_SUPERSEDE = "نسخ جزئی (نه تعارض کامل)"
    EXPLICIT_SUPERSEDE = "نسخ صریح"
    CHAIN_CONFLICT = "تعارض کامل (زنجیره‌ای، پس از نسخ)"
    NO_CONFLICT = "بدون تعارض"

class ClauseInput(BaseModel):
    clause_number: int = Field(..., example=1)
    content: str = Field(..., example="متن بند بخشنامه...")

class CircularJSONInput(BaseModel):
    circular_id: str = Field(..., example="C-001")
    title: str = Field(..., example="عنوان بخشنامه")
    doc_type: DocType = Field(..., example="داخلی")
    issuer: str = Field(..., example="اداره اعتبارات و تسهیلات")
    issue_date: str = Field(..., example="1401/02/10")
    clauses: List[ClauseInput]

class Clause(BaseModel):
    circular_id: str
    title: str
    doc_type: DocType
    issuer: str
    issue_date: str
    clause_number: int
    content: str

    @property
    def full_id(self) -> str:
        return f"{self.circular_id}: بند {self.clause_number}"



#class CircularSubmission(BaseModel):
#    circular_id: str
#    title: str
#    doc_type: DocType
#    issuer: str
#    issue_date: str
#    clauses: List[dict] # لیست بندها {"clause_number": 1, "content": "..."}

class ConflictAnalysisResult(BaseModel):
    case_id: str
    circular_a_id: str
    circular_b_id: str
    clauses_involved: str
    conflict_type: ConflictType
    explanation: str
    winning_clause: Optional[str] = Field(None, description="بند برنده یا معتبر")
    requires_human_review: bool = Field(False, description="نیازمند بازبینی توسط واحد حقوقی/تطبیق")
    simple_summary: Optional[str] = Field(None, description="خلاصه ساده و روان جهت واحد حقوقی (Bonus)")

class PeriodicAuditResponse(BaseModel):
    total_circulars_checked: int
    total_conflicts_found: int
    conflicts: List[ConflictAnalysisResult]