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

<<<<<<< HEAD
# Lecture Presentation Models
class LectureTopicRequest(BaseModel):
    topic: str
    duration_minutes: Optional[int] = 10
    difficulty_level: Optional[str] = "beginner"  # beginner, intermediate, advanced
    target_audience: Optional[str] = "general"

class SlideInstruction(BaseModel):
    slide_number: int
    title: str
    content: str
    image_prompt: str
    slide_type: str  # title, content, conclusion, etc.
    script: str  # Lecture script content for this specific slide

class LectureResponse(BaseModel):
    status: int
    topic: str
    duration_minutes: int
    slides: List[SlideInstruction]
    total_slides: int

class QwenRequest(BaseModel):
    model: str = "qwen3-max-preview"
    messages: List[dict]
    stream: bool = False

class TextAndAvatarGeneration(BaseModel):
    text: str
    avatar: str
=======
class TextAndAvatarGeneration(BaseModel):
    text: str
    avatar: str
>>>>>>> parent of fc24065 (merge)
