from fastapi import APIRouter
from app.src.models.model import GeneratedTextResponse, TextForGenerationPrompt

router = APIRouter()


@router.post("/generate-text", response_model=GeneratedTextResponse)
def generate_text_prompt(prompt: TextForGenerationPrompt):
    # Здесь — твоя логика генерации
    return GeneratedTextResponse(status=1, text="idk")
