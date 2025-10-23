import uuid
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.services.processing_service import ProcessingService
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()
processing_service = ProcessingService()

class TryOnOptions(BaseModel):
    preserve_background: Optional[bool] = False
    adjust_size: Optional[bool] = True
    garment_type: Optional[str] = "upper"

class TryOffOptions(BaseModel):
    extract_all: Optional[bool] = True
    garment_types: Optional[list] = ["upper", "lower", "full"]
    output_format: Optional[str] = "png"

@router.post("/try-on")
async def try_on_garment(
    background_tasks: BackgroundTasks,
    model_image: UploadFile = File(...),
    garment_image: UploadFile = File(...),
    options: Optional[str] = Form(None)
) -> Dict:
    """
    Submit a try-on request to put a garment on a model.
    """
    try:
        # Parse options if provided
        try_on_options = TryOnOptions()
        if options:
            import json
            try_on_options = TryOnOptions(**json.loads(options))

        # Submit processing job
        job_id = await processing_service.submit_try_on_job(
            model_image=model_image,
            garment_image=garment_image,
            options=try_on_options.dict(),
            background_tasks=background_tasks
        )

        logger.info(f"Try-on job submitted: {job_id}")

        return {
            "success": True,
            "job_id": job_id,
            "message": "Try-on job submitted successfully",
            "estimated_time": "30-60 seconds"
        }

    except Exception as e:
        logger.error(f"Failed to submit try-on job: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit try-on job")

@router.post("/try-off")
async def extract_garments(
    background_tasks: BackgroundTasks,
    model_image: UploadFile = File(...),
    options: Optional[str] = Form(None)
) -> Dict:
    """
    Submit a try-off request to extract garments from a model image.
    """
    try:
        # Parse options if provided
        try_off_options = TryOffOptions()
        if options:
            import json
            try_off_options = TryOffOptions(**json.loads(options))

        # Submit processing job
        job_id = await processing_service.submit_try_off_job(
            model_image=model_image,
            options=try_off_options.dict(),
            background_tasks=background_tasks
        )

        logger.info(f"Try-off job submitted: {job_id}")

        return {
            "success": True,
            "job_id": job_id,
            "message": "Try-off job submitted successfully",
            "estimated_time": "45-90 seconds"
        }

    except Exception as e:
        logger.error(f"Failed to submit try-off job: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit try-off job")

@router.post("/preview")
async def preview_processing(
    model_image: UploadFile = File(...),
    garment_image: Optional[UploadFile] = File(None),
    processing_type: str = Form(...),
    options: Optional[str] = Form(None)
) -> Dict:
    """
    Get a quick preview of the processing results (lower quality, faster).
    """
    try:
        if processing_type not in ["try-on", "try-off"]:
            raise HTTPException(status_code=400, detail="Invalid processing type")

        # Parse options
        processing_options = {}
        if options:
            import json
            processing_options = json.loads(options)

        # Generate preview
        preview_result = await processing_service.generate_preview(
            model_image=model_image,
            garment_image=garment_image,
            processing_type=processing_type,
            options=processing_options
        )

        return {
            "success": True,
            "preview_url": preview_result["preview_url"],
            "processing_estimate": preview_result["processing_estimate"]
        }

    except Exception as e:
        logger.error(f"Failed to generate preview: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate preview")

@router.get("/models")
async def get_available_models() -> Dict:
    """
    Get information about available AI models and their capabilities.
    """
    try:
        models_info = await processing_service.get_available_models()
        return {
            "success": True,
            "models": models_info
        }

    except Exception as e:
        logger.error(f"Failed to get models info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get models information")