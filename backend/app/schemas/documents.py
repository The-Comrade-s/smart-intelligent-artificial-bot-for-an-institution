"""
Pydantic schemas for document upload and AI-assisted file analysis.
"""
from pydantic import BaseModel, Field


class DocumentExtractResponse(BaseModel):
    filename: str
    character_count: int
    extracted_text: str


class DocumentAnalyzeRequest(BaseModel):
    text: str = Field(min_length=1)
    action: str = Field(description="summarize | explain | quiz | flashcards | question")
    question: str | None = None  # required when action == "question"


class DocumentAnalyzeResponse(BaseModel):
    action: str
    result: str
