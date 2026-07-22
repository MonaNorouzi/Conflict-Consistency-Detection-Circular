class NLIService:
    def __init__(self) -> None:
        self.provider = "ollama"

    def infer(self, premise: str, hypothesis: str) -> dict[str, str]:
        return {"result": "neutral"}
