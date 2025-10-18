from pydantic import BaseModel

class TextForGenerationPrompt(BaseModel):
    text: str

class GeneratedTextResponse(BaseModel):
    status: int
    text: str
