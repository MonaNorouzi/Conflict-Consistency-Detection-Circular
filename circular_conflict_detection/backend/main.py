from fastapi import FastAPI

app = FastAPI(title="Circular Conflict & Consistency Detection API")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
