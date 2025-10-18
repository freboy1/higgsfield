from pydantic import BaseModel
from typing import List, Optional

class TextForGenerationPrompt(BaseModel):
    text: str

class GeneratedTextResponse(BaseModel):
    status: int
    text: str

class ItemResult(BaseModel):
    id: str
    url: Optional[str] = None


class GenerateImageResponse(BaseModel):
    status: int
    result: List[ItemResult]
