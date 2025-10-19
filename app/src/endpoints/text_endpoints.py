from fastapi import APIRouter
from app.src.models.model import GeneratedTextResponse, TextForGenerationPrompt, GenerateTextFromRequest

router = APIRouter()


@router.post("/generate-text", response_model=GeneratedTextResponse)
def generate_text_prompt(prompt: GenerateTextFromRequest):
    # Здесь — твоя логика генерации
    return GeneratedTextResponse(status=1, text="idk")
