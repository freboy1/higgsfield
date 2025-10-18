from fastapi import FastAPI
from app.routes.text_route import router as api_router

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

app.include_router(api_router)
