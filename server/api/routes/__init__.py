from fastapi import APIRouter

from .software import router as software_router

api_router = APIRouter()
api_router.include_router(software_router, prefix="/software", tags=["software"])

