import json
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from backend.models.schemas import CircularJSONInput, ConflictAnalysisResult, PeriodicAuditResponse, Clause, ConflictType, ClauseInput, DocType
from backend.services.precedence import PrecedenceEngine

router = APIRouter()

# پایگاه داده ساده در حافظه (In-Memory Repository)
db_clauses: List[Clause] = []

def process_single_circular(data: CircularJSONInput) -> List[ConflictAnalysisResult]:
    detected_conflicts = []
    
    new_clauses = [
        Clause(
            circular_id=data.circular_id,
            title=data.title,
            doc_type=data.doc_type,
            issuer=data.issuer,
            issue_date=data.issue_date,
            clause_number=c.clause_number,
            content=c.content
        ) for c in data.clauses
    ]
    
    for new_c in new_clauses:
        for existing_c in db_clauses:
            if new_c.circular_id == existing_c.circular_id:
                continue
            
            # نمونه بررسی منطق AI (در این بخش توابع ai نفر اول فراخوانی می‌شوند)
            if any(term in new_c.content for term in ["سقف", "کارمزد", "سود", "چک", "سن"]) and \
               any(term in existing_c.content for term in ["سقف", "کارمزد", "سود", "چک", "سن"]):
                
                res = PrecedenceEngine.resolve_conflict(
                    case_id=f"CONF-{new_c.circular_id}-{existing_c.circular_id}",
                    clause_a=new_c,
                    clause_b=existing_c,
                    conflict_type=ConflictType.FULL_CONFLICT,
                    ai_explanation=f"مغایرت در مفاد بین {new_c.full_id} و {existing_c.full_id}.",
                    simple_summary="تناقض در مقادیر یا شروط اعلامی."
                )
                detected_conflicts.append(res)
        
        db_clauses.append(new_c)
        
    return detected_conflicts

@router.post("/upload-json", response_model=List[ConflictAnalysisResult])
async def upload_circular_json(file: UploadFile = File(...)):
    """ثبت و مقایسه بخشنامه جدید از طریق آپلود فایل JSON"""
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="فقط فایل‌های .json مجاز هستند.")
    
    content = await file.read()
    data = json.loads(content.decode('utf-8'))
    
    if isinstance(data, list):
        results = []
        for item in data:
            results.extend(process_single_circular(CircularJSONInput(**item)))
        return results
    else:
        return process_single_circular(CircularJSONInput(**data))

@router.post("/process-text", response_model=List[ConflictAnalysisResult])
async def process_text(payload: dict):
    """پردازش متن خام بخشنامه و تبدیل آن به یک ورودی استاندارد برای تحلیل تعارض"""
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Body must be a JSON object.")

    text = payload.get("text", "")
    metadata = payload.get("metadata", {}) or {}

    if not isinstance(text, str) or not text.strip():
        raise HTTPException(status_code=400, detail="Field 'text' is required and must be a non-empty string.")

    doc_id = metadata.get("doc_id") or "TEXT-001"
    doc_type = metadata.get("type") or "Internal"
    department = metadata.get("department") or "نامشخص"
    issue_date = metadata.get("date") or "1401/01/01"

    doc_type_value = DocType.UPSTREAM if doc_type in {"Regulatory", "بالادستی/نظارتی"} else DocType.INTERNAL

    data = CircularJSONInput(
        circular_id=doc_id,
        title="متن ورودی از UI",
        doc_type=doc_type_value,
        issuer=department,
        issue_date=issue_date,
        clauses=[ClauseInput(clause_number=1, content=text)]
    )

    return process_single_circular(data)

@router.get("/periodic-audit", response_model=PeriodicAuditResponse)
async def periodic_audit():
    """پایش و بررسی دوره‌ای کل آرشیو برای کشف تعارضات پنهان"""
    conflicts = []
    n = len(db_clauses)
    
    for i in range(n):
        for j in range(i + 1, n):
            c1, c2 = db_clauses[i], db_clauses[j]
            if c1.circular_id != c2.circular_id:
                if any(w in c1.content for w in ["سقف", "سود", "چک"]) and any(w in c2.content for w in ["سقف", "سود", "چک"]):
                    res = PrecedenceEngine.resolve_conflict(
                        case_id=f"AUDIT-{i}-{j}",
                        clause_a=c1,
                        clause_b=c2,
                        conflict_type=ConflictType.FULL_CONFLICT,
                        ai_explanation="تعارض پنهان کشف‌شده در پایش دوره‌ای آرشیو.",
                        simple_summary="عدم مطابقت دو بند قدیمی در آرشیو."
                    )
                    conflicts.append(res)
                    
    unique_ids = len(set(c.circular_id for c in db_clauses))
    return PeriodicAuditResponse(
        total_circulars_checked=unique_ids,
        total_conflicts_found=len(conflicts),
        conflicts=conflicts
    )