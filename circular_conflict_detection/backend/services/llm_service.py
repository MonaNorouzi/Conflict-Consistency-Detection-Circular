class LLMService:
    def __init__(self) -> None:
        self.provider = "ollama"

    def analyze(self, text: str) -> dict[str, str]:
        return {"summary": f"Analyzed: {text[:80]}"}
