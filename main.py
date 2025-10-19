from fastapi import FastAPI
from app.routes.text_route import router as api_router
from app.routes.image_route import router as image_router
from app.routes.lecture_route import router as lecture_router
from app.routes.video_route import router as video_router
from dotenv import load_dotenv
import os

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
HF_SECRET = os.getenv("HF_SECRET")
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

# For development, use test values if not set
if HF_API_KEY is None:
    HF_API_KEY = "test_hf_api_key"
    print("WARNING: HF_API_KEY not set, using test value")

if HF_SECRET is None:
    HF_SECRET = "test_hf_secret"
    print("WARNING: HF_SECRET not set, using test value")

if DASHSCOPE_API_KEY is None:
    DASHSCOPE_API_KEY = "test_dashscope_api_key"
    print("WARNING: DASHSCOPE_API_KEY not set, using test value")

app = FastAPI(
    title="Higgsfield Lecture Generator API",
    description="API for generating lecture presentations using Qwen LLM and Higgsfield image generation",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "message": "Higgsfield Lecture Generator API", 
        "version": "1.0.0",
        "endpoints": {
            "lecture": "/lecture/generate-lecture",
            "text": "/generate-text", 
            "image": "/generate-image"
        }
    }

app.include_router(api_router)
app.include_router(image_router)
app.include_router(lecture_router)

app.include_router(video_router)