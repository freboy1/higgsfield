from pydantic import BaseModel
from typing import List, Optional, Dict

# Request Models
class AddOnsConfig(BaseModel):
    code_examples: bool = False
    visuals: bool = False
    exercises: bool = False
    qa_section: bool = False

class LectureTopicRequest(BaseModel):
    topic: str
    duration_minutes: Optional[int] = 10
    difficulty_level: Optional[str] = "beginner"  # beginner, intermediate, advanced
    target_audience: Optional[str] = "general"
    tone: Optional[str] = "friendly"  # friendly, formal, exam, story
    add_ons: Optional[AddOnsConfig] = AddOnsConfig()

# Response Models
class SlideInstruction(BaseModel):
    slide_number: int
    title: str
    content: str
    image_prompt: str
    slide_type: str  # title, content, conclusion, qa
    script: str
    code_example: Optional[str] = None
    exercise: Optional[str] = None

class LectureResponse(BaseModel):
    status: int
    topic: str
    duration_minutes: int
    tone: str
    slides: List[SlideInstruction]
    total_slides: int
    markdown_content: Optional[str] = None  # ← NEW FIELD ADDED

# Existing models
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

class TextAndAvatarGeneration(BaseModel):
    text: str
    avatar: str