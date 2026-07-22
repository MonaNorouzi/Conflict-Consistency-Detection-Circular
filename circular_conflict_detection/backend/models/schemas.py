from pydantic import BaseModel, Field


class RegulationDocument(BaseModel):
    id: str = Field(..., description="Unique identifier")
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Regulation text")


class ConflictCheckRequest(BaseModel):
    text: str = Field(..., description="User-provided text to analyze")
