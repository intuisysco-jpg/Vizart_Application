import os
import uuid
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import UploadFile, BackgroundTasks
from app.services.job_service import JobService
from app.services.image_service import ImageService
from app.workers.ai_processor import AIProcessor
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

class ProcessingService:
    """Service for handling AI processing tasks."""

    def __init__(self):
        self.job_service = JobService()
        self.image_service = ImageService()
        self.ai_processor = AIProcessor()

    async def submit_try_on_job(
        self,
        model_image: UploadFile,
        garment_image: UploadFile,
        options: Dict[str, Any],
        background_tasks: BackgroundTasks
    ) -> str:
        """Submit a try-on processing job."""
        try:
            # Save uploaded files
            model_filename = await self._save_uploaded_file(model_image)
            garment_filename = await self._save_uploaded_file(garment_image)

            # Create job
            job = await self.job_service.create_job(
                job_type="try-on",
                model_image_path=model_filename,
                garment_image_path=garment_filename,
                options=options
            )

            # Add background task to process the job
            background_tasks.add_task(
                self._process_try_on_job,
                job.id,
                model_filename,
                garment_filename,
                options
            )

            return job.id

        except Exception as e:
            logger.error(f"Failed to submit try-on job: {e}")
            raise

    async def submit_try_off_job(
        self,
        model_image: UploadFile,
        options: Dict[str, Any],
        background_tasks: BackgroundTasks
    ) -> str:
        """Submit a try-off processing job."""
        try:
            # Save uploaded file
            model_filename = await self._save_uploaded_file(model_image)

            # Create job
            job = await self.job_service.create_job(
                job_type="try-off",
                model_image_path=model_filename,
                options=options
            )

            # Add background task to process the job
            background_tasks.add_task(
                self._process_try_off_job,
                job.id,
                model_filename,
                options
            )

            return job.id

        except Exception as e:
            logger.error(f"Failed to submit try-off job: {e}")
            raise

    async def generate_preview(
        self,
        model_image: UploadFile,
        garment_image: Optional[UploadFile],
        processing_type: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a quick preview of processing results."""
        try:
            # Save files temporarily
            model_filename = await self._save_uploaded_file(model_image)
            garment_filename = None
            if garment_image:
                garment_filename = await self._save_uploaded_file(garment_image)

            # Generate preview using AI processor
            preview_result = await self.ai_processor.generate_preview(
                model_path=model_filename,
                garment_path=garment_filename,
                processing_type=processing_type,
                options=options
            )

            return preview_result

        except Exception as e:
            logger.error(f"Failed to generate preview: {e}")
            raise

    async def get_available_models(self) -> Dict[str, Any]:
        """Get information about available AI models."""
        return await self.ai_processor.get_model_info()

    async def _save_uploaded_file(self, file: UploadFile) -> str:
        """Save an uploaded file and return the filename."""
        import aiofiles

        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        filename = f"{file_id}{file_extension}"
        file_path = os.path.join(settings.UPLOAD_DIR, filename)

        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        logger.info(f"Saved uploaded file: {filename}")
        return file_path

    async def _process_try_on_job(
        self,
        job_id: str,
        model_path: str,
        garment_path: str,
        options: Dict[str, Any]
    ) -> None:
        """Process a try-on job in the background."""
        start_time = datetime.utcnow()

        try:
            # Update job status to processing
            await self.job_service.update_job_status(
                job_id=job_id,
                status="processing",
                progress=10.0,
                message="Starting try-on processing..."
            )

            # Process with AI
            result = await self.ai_processor.process_try_on(
                model_path=model_path,
                garment_path=garment_path,
                options=options,
                job_id=job_id,
                progress_callback=lambda progress, message: self._update_job_progress(job_id, progress, message)
            )

            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()

            # Update job with result
            await self.job_service.update_job_status(
                job_id=job_id,
                status="completed",
                progress=100.0,
                message="Try-on processing completed successfully",
                result_data=result,
                processing_time=processing_time
            )

            logger.info(f"Try-on job {job_id} completed in {processing_time:.2f}s")

        except Exception as e:
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()

            # Update job with error
            await self.job_service.update_job_status(
                job_id=job_id,
                status="failed",
                progress=0.0,
                message="Try-on processing failed",
                error_message=str(e),
                processing_time=processing_time
            )

            logger.error(f"Try-on job {job_id} failed: {e}")

    async def _process_try_off_job(
        self,
        job_id: str,
        model_path: str,
        options: Dict[str, Any]
    ) -> None:
        """Process a try-off job in the background."""
        start_time = datetime.utcnow()

        try:
            # Update job status to processing
            await self.job_service.update_job_status(
                job_id=job_id,
                status="processing",
                progress=10.0,
                message="Starting garment extraction..."
            )

            # Process with AI
            result = await self.ai_processor.process_try_off(
                model_path=model_path,
                options=options,
                job_id=job_id,
                progress_callback=lambda progress, message: self._update_job_progress(job_id, progress, message)
            )

            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()

            # Update job with result
            await self.job_service.update_job_status(
                job_id=job_id,
                status="completed",
                progress=100.0,
                message="Garment extraction completed successfully",
                result_data=result,
                processing_time=processing_time
            )

            logger.info(f"Try-off job {job_id} completed in {processing_time:.2f}s")

        except Exception as e:
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()

            # Update job with error
            await self.job_service.update_job_status(
                job_id=job_id,
                status="failed",
                progress=0.0,
                message="Garment extraction failed",
                error_message=str(e),
                processing_time=processing_time
            )

            logger.error(f"Try-off job {job_id} failed: {e}")

    async def _update_job_progress(self, job_id: str, progress: float, message: str) -> None:
        """Update job progress during processing."""
        await self.job_service.update_job_status(
            job_id=job_id,
            status="processing",
            progress=progress,
            message=message
        )