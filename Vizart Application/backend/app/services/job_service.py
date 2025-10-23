import uuid
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import BackgroundTasks
from app.core.database import get_db, SessionLocal
from app.models.job import Job, JobStatus
from app.core.logging import get_logger

logger = get_logger(__name__)

class JobService:
    """Service for managing processing jobs."""

    async def create_job(
        self,
        job_type: str,
        model_image_path: str,
        garment_image_path: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Job:
        """Create a new processing job."""
        db = SessionLocal()
        try:
            job = Job(
                id=str(uuid.uuid4()),
                job_type=job_type,
                model_image_path=model_image_path,
                garment_image_path=garment_image_path,
                options=options,
                status=JobStatus.PENDING,
                progress=0.0,
                message="Job created"
            )

            db.add(job)
            db.commit()
            db.refresh(job)

            logger.info(f"Created job {job.id} of type {job_type}")
            return job

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create job: {e}")
            raise
        finally:
            db.close()

    async def get_job(self, job_id: str) -> Optional[Job]:
        """Get a job by ID."""
        db = SessionLocal()
        try:
            return db.query(Job).filter(Job.id == job_id).first()
        except Exception as e:
            logger.error(f"Failed to get job {job_id}: {e}")
            return None
        finally:
            db.close()

    async def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        progress: float,
        message: str,
        result_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        processing_time: Optional[float] = None
    ) -> bool:
        """Update job status and progress."""
        db = SessionLocal()
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                return False

            job.status = status
            job.progress = progress
            job.message = message

            if result_data:
                job.result_data = result_data

            if error_message:
                job.error_message = error_message

            if processing_time:
                job.processing_time = processing_time

            if status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                job.completed_at = datetime.utcnow()

            db.commit()
            db.refresh(job)

            logger.info(f"Updated job {job_id} status to {status.value}, progress: {progress}%")
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update job {job_id}: {e}")
            return False
        finally:
            db.close()

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a job."""
        return await self.update_job_status(
            job_id=job_id,
            status=JobStatus.CANCELLED,
            progress=0.0,
            message="Job cancelled by user"
        )

    async def list_jobs(
        self,
        status: Optional[str] = None,
        job_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Job]:
        """List jobs with optional filtering."""
        db = SessionLocal()
        try:
            query = db.query(Job)

            if status:
                try:
                    status_enum = JobStatus(status)
                    query = query.filter(Job.status == status_enum)
                except ValueError:
                    pass

            if job_type:
                query = query.filter(Job.job_type == job_type)

            return query.order_by(Job.created_at.desc()).offset(offset).limit(limit).all()

        except Exception as e:
            logger.error(f"Failed to list jobs: {e}")
            return []
        finally:
            db.close()

    async def count_jobs(
        self,
        status: Optional[str] = None,
        job_type: Optional[str] = None
    ) -> int:
        """Count jobs with optional filtering."""
        db = SessionLocal()
        try:
            query = db.query(Job)

            if status:
                try:
                    status_enum = JobStatus(status)
                    query = query.filter(Job.status == status_enum)
                except ValueError:
                    pass

            if job_type:
                query = query.filter(Job.job_type == job_type)

            return query.count()

        except Exception as e:
            logger.error(f"Failed to count jobs: {e}")
            return 0
        finally:
            db.close()

    async def get_job_result(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job result data."""
        job = await self.get_job(job_id)
        if not job or job.status != JobStatus.COMPLETED:
            return None

        return job.result_data

    async def cleanup_job(self, job_id: str) -> bool:
        """Clean up job files and remove job from database."""
        import os
        from app.core.config import settings

        db = SessionLocal()
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                return False

            # Remove uploaded files
            if job.model_image_path and os.path.exists(job.model_image_path):
                os.remove(job.model_image_path)

            if job.garment_image_path and os.path.exists(job.garment_image_path):
                os.remove(job.garment_image_path)

            # Remove result files if they exist
            if job.result_data:
                # Extract image URLs from result data and remove files
                for key, value in job.result_data.items():
                    if isinstance(value, str) and value.startswith('/static/results/'):
                        file_path = value.replace('/static/results/', settings.RESULTS_DIR + '/')
                        if os.path.exists(file_path):
                            os.remove(file_path)

            # Remove job from database
            db.delete(job)
            db.commit()

            logger.info(f"Cleaned up job {job_id}")
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to cleanup job {job_id}: {e}")
            return False
        finally:
            db.close()