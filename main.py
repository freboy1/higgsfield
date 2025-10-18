from fastapi import FastAPI
from app.routes.text_route import router as api_router
from app.routes.image_route import router as image_router
from dotenv import load_dotenv
import os

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
HF_SECRET = os.getenv("HF_SECRET")
if HF_API_KEY is None or HF_SECRET is None:
    raise RuntimeError("HF_API_KEY or HF_SECRET not set in environment")

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

app.include_router(api_router)
app.include_router(image_router)
