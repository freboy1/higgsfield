from fastapi import APIRouter

from app.src.endpoints.text_endpoints  import router as endpoints_router

router = APIRouter()

router.include_router(endpoints_router, prefix="", tags=["text"])
