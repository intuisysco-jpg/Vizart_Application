import os
import uuid
import aiofiles
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from typing import Dict
from app.core.config import settings
from app.core.logging import get_logger
from app.services.image_service import ImageService

logger = get_logger(__name__)
router = APIRouter()
image_service = ImageService()

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)) -> Dict:
    """Upload an image file and return the file information."""

    # Validate file type
    if file.content_type not in settings.ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(settings.ALLOWED_MIME_TYPES)}"
        )

    # Check file size
    if file.size and file.size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / (1024*1024):.1f}MB"
        )

    try:
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        filename = f"{file_id}{file_extension}"
        file_path = os.path.join(settings.UPLOAD_DIR, filename)

        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        # Validate and get image info
        image_info = await image_service.get_image_info(file_path)

        logger.info(f"Image uploaded successfully: {filename}")

        return {
            "success": True,
            "file_id": file_id,
            "filename": filename,
            "original_filename": file.filename,
            "content_type": file.content_type,
            "size": file.size,
            "dimensions": image_info["dimensions"],
            "url": f"/static/uploads/{filename}"
        }

    except Exception as e:
        logger.error(f"Failed to upload image: {e}")
        # Clean up file if upload failed
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

        raise HTTPException(status_code=500, detail="Failed to upload image")

@router.get("/uploads/{filename}")
async def get_uploaded_image(filename: str):
    """Serve uploaded image files."""
    file_path = os.path.join(settings.UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(file_path)

@router.get("/results/{filename}")
async def get_result_image(filename: str):
    """Serve result image files."""
    file_path = os.path.join(settings.RESULTS_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Result image not found")

    return FileResponse(file_path)