import pytest
from backend.models.schemas import Clause, DocType, ConflictType
from backend.services.precedence import PrecedenceEngine

def test_upstream_priority():
    c_internal = Clause(
        circular_id="C-001", title="داخلی", doc_type=DocType.INTERNAL,
        issuer="اعتبارات", issue_date="1401/01/01", clause_number=1, content="سقف ۵۰ میلیون"
    )
    c_upstream = Clause(
        circular_id="C-005", title="نظارتی", doc_type=DocType.UPSTREAM,
        issuer="بانک مرکزی", issue_date="1402/01/01", clause_number=1, content="سقف ۳۰ میلیون"
    )
    
    result = PrecedenceEngine.resolve_conflict(
        case_id="T1", clause_a=c_internal, clause_b=c_upstream,
        conflict_type=ConflictType.HIERARCHICAL_CONFLICT, ai_explanation="تست"
    )
    
    assert result.winning_clause == "C-005: بند 1"
    assert result.requires_human_review is False

def test_newer_date_same_issuer():
    c_old = Clause(
        circular_id="C-001", title="قدیم", doc_type=DocType.INTERNAL,
        issuer="اعتبارات", issue_date="1401/01/01", clause_number=1, content="سقف ۵۰ میلیون"
    )
    c_new = Clause(
        circular_id="C-002", title="جدید", doc_type=DocType.INTERNAL,
        issuer="اعتبارات", issue_date="1402/01/01", clause_number=1, content="سقف ۸۰ میلیون"
    )
    
    result = PrecedenceEngine.resolve_conflict(
        case_id="T2", clause_a=c_old, clause_b=c_new,
        conflict_type=ConflictType.FULL_CONFLICT, ai_explanation="تست"
    )
    
    assert result.winning_clause == "C-002: بند 1"
    assert result.requires_human_review is False