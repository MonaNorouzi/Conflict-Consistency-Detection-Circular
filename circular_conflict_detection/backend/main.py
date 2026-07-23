from fastapi import FastAPI
from backend.core.config import settings
from backend.api import routes

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs"
)

app.include_router(routes.router, prefix=f"{settings.API_PREFIX}/circulars", tags=["Circulars"])

@app.get("/")
def root():
    return {"message": "Circular Conflict & Consistency Detection API is running..."}