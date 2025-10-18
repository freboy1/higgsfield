from fastapi import FastAPI
from app.routes.text_route import router as api_router
from app.routes.image_route import router as image_router
from dotenv import load_dotenv
import os

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
HF_SECRET = os.getenv("HF_SECRET")
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

if HF_API_KEY is None or HF_SECRET is None:
    raise RuntimeError("HF_API_KEY or HF_SECRET not set in environment")

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
        "message": "Higgsfield API", 
        "version": "1.0.0",
        "endpoints": {
            "text": "/generate-text", 
            "image": "/generate-image"
        }
    }


app.include_router(api_router)
app.include_router(image_router)
