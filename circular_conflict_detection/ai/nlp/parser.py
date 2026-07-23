import re
from typing import List, Dict, Any

try:
    from hazm import Normalizer
except ImportError:
    raise ImportError("The 'hazm' library is required. Please add it to requirements.txt (pip install hazm).")


class CircularParser:
    """
    Handles deterministic text processing, normalization, and regex-based chunking
    of Persian banking circulars.
    """
    def __init__(self):
        # Initialize Hazm normalizer for character unification and spacing fixes
        self.normalizer = Normalizer()
        
        # Regex pattern to detect clauses.
        # Matches keywords like "ماده", "بند", "تبصره" followed by Persian or English digits.
        # It also handles optional punctuation like dashes or colons after the clause number.
        self.clause_pattern = re.compile(r'(ماده|بند|تبصره|بخش)\s+([\d۰-۹]+)\s*[-:]?')

    def clean_text(self, text: str) -> str:
        """
        Normalizes the Persian text to ensure consistency before embedding or LLM processing.
        - Converts Arabic characters to Persian (e.g., ي -> ی, ك -> ک)
        - Fixes spacing and zero-width non-joiners (نیم‌فاصله)
        """
        if not text:
            return ""
        return self.normalizer.normalize(text.strip())

    def parse_circular(self, raw_text: str, document_metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Splits the raw text of a circular into individual clauses using Regex.
        
        Args:
            raw_text (str): The full text of the newly registered circular.
            document_metadata (dict): Global metadata for the document (e.g., doc_id, date, type, department).
            
        Returns:
            List[Dict]: A list of dictionaries, each containing a parsed clause and its specific metadata.
        """
        cleaned_text = self.clean_text(raw_text)
        doc_meta = document_metadata or {}
        
        # Find all clause headers in the text
        matches = list(self.clause_pattern.finditer(cleaned_text))
        parsed_clauses = []

        if not matches:
            # Fallback: If the circular lacks standard structural keywords, treat it as a single chunk.
            parsed_clauses.append({
                "clause_id": "general",
                "text": cleaned_text,
                "metadata": doc_meta.copy()
            })
            return parsed_clauses

        for i, match in enumerate(matches):
            clause_type = match.group(1)   # e.g., 'ماده' or 'تبصره'
            clause_number = match.group(2) # e.g., '۱' or '12'
            clause_id = f"{clause_type} {clause_number}"
            
            # The text for this clause is everything from the end of this match up to the start of the next match
            start_idx = match.end()
            end_idx = matches[i+1].start() if i + 1 < len(matches) else len(cleaned_text)
            
            clause_text = cleaned_text[start_idx:end_idx].strip()
            
            # We only append if there is actual content under the clause header
            if clause_text:
                parsed_clauses.append({
                    "clause_id": clause_id,
                    "text": clause_text,
                    "metadata": {
                        **doc_meta,
                        "clause_type": clause_type,
                        "clause_number": clause_number
                    }
                })
                
        return parsed_clauses

# --- Example Usage for local testing ---
if __name__ == "__main__":
    sample_text = """
    ماده ۱ - بانک‌ها موظف به رعایت نرخ سود مصوب هستند.
    تبصره ۱: این قانون شامل سپرده‌های ارزی نمی‌شود.
    بند ۲- تسهیلات خرد باید با ضمانت کمتر ارائه گردد.
    """
    
    parser = CircularParser()
    clauses = parser.parse_circular(
        raw_text=sample_text, 
        document_metadata={"doc_id": "CIRC-1402-001", "type": "Regulatory"}
    )
    
    import json
    print(json.dumps(clauses, ensure_ascii=False, indent=2))