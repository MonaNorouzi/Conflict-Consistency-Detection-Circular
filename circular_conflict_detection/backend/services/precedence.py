from backend.models.schemas import Clause, ConflictType, ConflictAnalysisResult


"""
    سرویس منطق تجاری برای تعیین اولویت بخشنامه‌ها بر اساس:
    ۱. سلسله‌مراتب اسناد (بالادستی > داخلی)
    ۲. تقدم زمانی (جدیدتر > قدیمی‌تر برای همان واحد)
    ۳. تعارض بین‌واحدی (نیازمند تصمیم انسانی)
"""
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

        # ۱. بررسی سلسله‌مراتب (بالادستی بر داخلی اولویت دارد)
        if clause_a.doc_type != clause_b.doc_type:
            if clause_a.doc_type == "بالادستی/نظارتی":
                winning_clause = f"{clause_a.circular_id} (بند {clause_a.clause_number})"
                explanation += f" | بر اساس سلسله‌مراتب، بخشنامه بالادستی ({clause_a.circular_id}) بر بخشنامه داخلی ارجحیت دارد."
            else:
                winning_clause = f"{clause_b.circular_id} (بند {clause_b.clause_number})"
                explanation += f" | بر اساس سلسله‌مراتب، بخشنامه بالادستی ({clause_b.circular_id}) بر بخشنامه داخلی ارجحیت دارد."
            requires_human_review = False

        # ۲. بررسی تعارض بین دو بخشنامه از یک واحد (تاریخ جدیدتر برنده است)
        elif clause_a.issuer == clause_b.issuer:
            # مقایسه تاریخ صدور (YYYY/MM/DD)
            if clause_a.issue_date > clause_b.issue_date:
                winning_clause = f"{clause_a.circular_id} (بند {clause_a.clause_number})"
                explanation += f" | بخشنامه {clause_a.circular_id} به دلیل تاریخ صدور جدیدتر ({clause_a.issue_date}) نسبت به {clause_b.circular_id} ({clause_b.issue_date}) معتبر است."
            elif clause_b.issue_date > clause_a.issue_date:
                winning_clause = f"{clause_b.circular_id} (بند {clause_b.clause_number})"
                explanation += f" | بخشنامه {clause_b.circular_id} به دلیل تاریخ صدور جدیدتر ({clause_b.issue_date}) نسبت به {clause_a.circular_id} ({clause_a.issue_date}) معتبر است."
            else:
                requires_human_review = True
                winning_clause = "نامشخص (تاریخ صدور یکسان)"
            
            if conflict_type == ConflictType.PARTIAL_SUPERSEDE:
                winning_clause = f"بند اصلاحی جدید جایگزین شد ({winning_clause})"

        # ۳. تعارض بین‌واحدی (هم‌رتبه از دو واحد مختلف)
        else:
            requires_human_review = True
            winning_clause = "نیازمند تصمیم‌گیری واحد حقوقی/تطبیق"
            explanation += " | دو بخشنامه هم‌رتبه از دو واحد متفاوت صادر شده‌اند؛ تعیین اولویت نیازمند بررسی انسانی است."

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