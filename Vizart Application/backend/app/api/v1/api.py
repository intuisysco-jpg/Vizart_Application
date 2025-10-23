from fastapi import APIRouter
from .endpoints import jobs, images, processing

api_router = APIRouter()

api_router.include_router(images.router, prefix="/images", tags=["images"])
api_router.include_router(processing.router, prefix="/processing", tags=["processing"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])