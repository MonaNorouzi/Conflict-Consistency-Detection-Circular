class EmbeddingService:
    def __init__(self) -> None:
        self.model_name = "parsbert"

    def embed(self, text: str) -> list[float]:
        return [0.0, 0.1, 0.2, 0.3]
