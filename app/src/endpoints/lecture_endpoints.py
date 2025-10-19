from fastapi import APIRouter, HTTPException
from app.src.models.model import (
    LectureTopicRequest, 
    LectureResponse, 
    SlideInstruction,
    GeneratedTextResponse
)
from app.src.services.qwen_service import QwenService
from app.src.services.markdown_formatter import LectureMarkdownFormatter  # ← NEW IMPORT
from typing import List
import os

router = APIRouter()

def get_qwen_service():
    """Get Qwen service instance with proper error handling"""
    try:
        return QwenService()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Qwen service initialization failed: {str(e)}")

@router.post("/generate-lecture", response_model=LectureResponse)
def generate_lecture(request: LectureTopicRequest):
    """
    Generate a complete lecture presentation based on the topic
    """
    try:
        # Get Qwen service instance
        qwen_service = get_qwen_service()
        
        # Generate lecture content using Qwen API
        lecture_data = qwen_service.generate_lecture_content(
            topic=request.topic,
            duration_minutes=request.duration_minutes,
            difficulty_level=request.difficulty_level,
            target_audience=request.target_audience,
            tone=request.tone,
            add_ons=request.add_ons.dict() if request.add_ons else {}
        )
        
        # Convert the response to our slide format
        slides = []
        for slide_data in lecture_data.get("slides", []):
            # Handle content field - convert list to string if needed
            content = slide_data.get("content", "")
            
            if isinstance(content, list):
                content = "\n".join(str(item) for item in content)
            elif not isinstance(content, str):
                content = str(content)
            
            slide = SlideInstruction(
                slide_number=slide_data.get("slide_number", 1),
                title=slide_data.get("title", ""),
                content=content,
                image_prompt=slide_data.get("image_prompt", ""),
                slide_type=slide_data.get("slide_type", "content"),
                script=slide_data.get("script", ""),
                code_example=slide_data.get("code_example"),
                exercise=slide_data.get("exercise")
            )
            slides.append(slide)
        
        # Generate human-readable markdown format
        markdown_formatter = LectureMarkdownFormatter()
        markdown_content = markdown_formatter.format_lecture_to_markdown(
            topic=request.topic,
            slides=slides,
            tone=request.tone,
            difficulty_level=request.difficulty_level
        )
        
        return LectureResponse(
            status=1,
            topic=request.topic,
            duration_minutes=request.duration_minutes,
            tone=request.tone,
            slides=slides,
            total_slides=len(slides),
            markdown_content=markdown_content  # NEW FIELD
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating lecture: {str(e)}")

@router.post("/generate-text", response_model=GeneratedTextResponse)
def generate_text(prompt: str):
    """
    Simple text generation endpoint using Qwen API
    """
    try:
        qwen_service = get_qwen_service()
        text = qwen_service.generate_text(prompt)
        return GeneratedTextResponse(status=1, text=text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating text: {str(e)}")

@router.get("/lecture/{topic}")
def get_lecture_by_topic(topic: str, duration: int = 10, difficulty: str = "beginner"):
    """
    Get lecture by topic with query parameters
    """
    request = LectureTopicRequest(
        topic=topic,
        duration_minutes=duration,
        difficulty_level=difficulty
    )
    return generate_lecture(request)