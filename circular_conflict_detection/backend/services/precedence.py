from backend.models.schemas import Clause, ConflictType, ConflictAnalysisResult, DocType

class PrecedenceEngine:
    @staticmethod
    def resolve_conflict(
        case_id: str,
        clause_a: Clause,
        clause_b: Clause,
        conflict_type: ConflictType,
        explanation: str,
        simple_summary: str = ""
    ) -> ConflictAnalysisResult:
        
        winning_clause = None
        requires_human_review = False

        # ---------------------------------------------------------
        # ۱. برتری نسخ صریح (Explicit Override) - [GT-07]
        # ---------------------------------------------------------
        if conflict_type == ConflictType.EXPLICIT_SUPERSEDE:
            # در نسخ صریح، بخشنامه‌ای که حکم لغو صریح را آورده همیشه برنده و معتبر جاری است
            # فرض بر این است که clause_a بخشنامه جدیدتر/صادرکننده لغو است یا بر اساس تاریخ تعیین می‌شود
            if clause_a.issue_date >= clause_b.issue_date:
                winning_clause = f"{clause_a.circular_id} (بند {clause_a.clause_number})"
                explanation += f" | بند {clause_b.circular_id} صراحتاً توسط {clause_a.circular_id} لغو و بی‌اعتبار شده است."
            else:
                winning_clause = f"{clause_b.circular_id} (بند {clause_b.clause_number})"
                explanation += f" | بند {clause_a.circular_id} صراحتاً توسط {clause_b.circular_id} لغو و بی‌اعتبار شده است."
            requires_human_review = False

        # ---------------------------------------------------------
        # ۲. برتری اصلاح یا نسخ جزئی (Partial Override) - [GT-05]
        # ---------------------------------------------------------
        elif conflict_type == ConflictType.PARTIAL_SUPERSEDE:
            # در نسخ جزئی، بند جدید جایگزین بند قدیمی می‌شود و مابقی بندهای سند قدیمی معتبر می‌مانند
            newer_clause = clause_a if clause_a.issue_date >= clause_b.issue_date else clause_b
            older_clause = clause_b if clause_a.issue_date >= clause_b.issue_date else clause_a
            
            winning_clause = f"{newer_clause.circular_id} (بند {newer_clause.clause_number})"
            explanation += f" | نسخ جزئی: بند {newer_clause.clause_number} از بخشنامه {newer_clause.circular_id} جایگزین بند مربوطه در {older_clause.circular_id} می‌شود. سایر بندهای {older_clause.circular_id} کماکان معتبرند."
            requires_human_review = False

        # ---------------------------------------------------------
        # ۳. برتری سلسله‌مراتبی (Hierarchical Priority) - [GT-02, GT-03]
        # ---------------------------------------------------------
        elif clause_a.doc_type != clause_b.doc_type:
            # مقایسه بر اساس نوع سند (بالادستی/نظارتی اولویت مطلق دارد، حتی اگر قدیمی‌تر باشد)
            if clause_a.doc_type == DocType.UPSTREAM or clause_a.doc_type == "بالادستی/نظارتی":
                winning_clause = f"{clause_a.circular_id} (بند {clause_a.clause_number})"
                explanation += f" | برتری سلسله‌مراتبی: بخشنامه بالادستی/نظارتی ({clause_a.circular_id}) بر بخشنامه داخلی ارجحیت کامل دارد."
            else:
                winning_clause = f"{clause_b.circular_id} (بند {clause_b.clause_number})"
                explanation += f" | برتری سلسله‌مراتبی: بخشنامه بالادستی/نظارتی ({clause_b.circular_id}) بر بخشنامه داخلی ارجحیت کامل دارد."
            requires_human_review = False

        # ---------------------------------------------------------
        # ۴. برتری زمانی (Temporal Priority) - [GT-01, GT-06]
        # ---------------------------------------------------------
        elif clause_a.issuer == clause_b.issuer:
            if clause_a.issue_date > clause_b.issue_date:
                winning_clause = f"{clause_a.circular_id} (بند {clause_a.clause_number})"
                explanation += f" | برتری زمانی: بخشنامه {clause_a.circular_id} به دلیل صدور جدیدتر ({clause_a.issue_date}) از همان واحد، بخشنامه {clause_b.circular_id} را نسخ می‌کند."
            elif clause_b.issue_date > clause_a.issue_date:
                winning_clause = f"{clause_b.circular_id} (بند {clause_b.clause_number})"
                explanation += f" | برتری زمانی: بخشنامه {clause_b.circular_id} به دلیل صدور جدیدتر ({clause_b.issue_date}) از همان واحد، بخشنامه {clause_a.circular_id} را نسخ می‌کند."
            else:
                requires_human_review = True
                winning_clause = "نامشخص (تاریخ صدور و واحد یکسان)"

        # ---------------------------------------------------------
        # ۵ و ۶. برتری زنجیره‌ای (Chain) یا عدم وجود برتری (No Applicable Priority) - [GT-04, GT-08]
        # ---------------------------------------------------------
        else:
            # اگر تعارض زنجیره‌ای باشد یا دو بخشنامه از دو واحد مختلف و هم‌رتبه باشند
            requires_human_review = True
            winning_clause = "نیازمند تصمیم‌گیری واحد حقوقی/تطبیق"
            
            if conflict_type == ConflictType.CHAIN_CONFLICT:
                explanation += " | تعارض زنجیره‌ای: پس از اعمال آخرین نسخ/اصلاحات، تعارض بین دو واحد مجزا باقی مانده و نیازمند تصمیم انسانی است."
            else:
                explanation += " | عدم وجود قانون اولویت: دو بخشنامه هم‌رتبه از دو واحد متفاوت صادر شده‌اند و سلسله‌مراتب یا تقدم زمانی مشخصی ندارند."

        return ConflictAnalysisResult(
            case_id=case_id,
            circular_a_id=clause_a.circular_id,
            circular_b_id=clause_b.circular_id,
            clauses_involved=f"{clause_a.circular_id}: بند {clause_a.clause_number}؛ {clause_b.circular_id}: بند {clause_b.clause_number}",
            conflict_type=conflict_type,
            explanation=explanation,
            winning_clause=winning_clause,
            requires_human_review=requires_human_review,
            simple_summary=simple_summary
        )