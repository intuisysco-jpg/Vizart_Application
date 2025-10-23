from fastapi import APIRouter, HTTPException, Path, Query
from typing import List, Optional
from app.services.job_service import JobService
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()
job_service = JobService()

@router.get("/{job_id}")
async def get_job_status(job_id: str = Path(...)) -> dict:
    """Get the status of a specific job."""
    try:
        job = await job_service.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        return {
            "success": True,
            "job": {
                "id": job.id,
                "status": job.status.value,
                "job_type": job.job_type,
                "progress": job.progress,
                "message": job.message,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "updated_at": job.updated_at.isoformat() if job.updated_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "processing_time": job.processing_time,
                "error_message": job.error_message
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get job status")

@router.get("/{job_id}/result")
async def get_job_result(job_id: str = Path(...)) -> dict:
    """Get the result of a completed job."""
    try:
        job = await job_service.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        if job.status.value != "completed":
            raise HTTPException(status_code=400, detail="Job not completed")

        result_data = await job_service.get_job_result(job_id)

        return {
            "success": True,
            "job_id": job_id,
            "result": result_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job result: {e}")
        raise HTTPException(status_code=500, detail="Failed to get job result")

@router.delete("/{job_id}")
async def cancel_job(job_id: str = Path(...)) -> dict:
    """Cancel a running or pending job."""
    try:
        success = await job_service.cancel_job(job_id)
        if not success:
            raise HTTPException(status_code=404, detail="Job not found or cannot be cancelled")

        return {
            "success": True,
            "message": "Job cancelled successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel job: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel job")

@router.get("/")
async def list_jobs(
    status: Optional[str] = Query(None, description="Filter by job status"),
    job_type: Optional[str] = Query(None, description="Filter by job type"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of jobs to return"),
    offset: int = Query(0, ge=0, description="Number of jobs to skip")
) -> dict:
    """List jobs with optional filtering."""
    try:
        jobs = await job_service.list_jobs(
            status=status,
            job_type=job_type,
            limit=limit,
            offset=offset
        )

        total = await job_service.count_jobs(status=status, job_type=job_type)

        return {
            "success": True,
            "jobs": [
                {
                    "id": job.id,
                    "status": job.status.value,
                    "job_type": job.job_type,
                    "progress": job.progress,
                    "message": job.message,
                    "created_at": job.created_at.isoformat() if job.created_at else None,
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                    "processing_time": job.processing_time
                }
                for job in jobs
            ],
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            }
        }

    except Exception as e:
        logger.error(f"Failed to list jobs: {e}")
        raise HTTPException(status_code=500, detail="Failed to list jobs")

@router.delete("/{job_id}/cleanup")
async def cleanup_job(job_id: str = Path(...)) -> dict:
    """Clean up job files and remove job from database."""
    try:
        success = await job_service.cleanup_job(job_id)
        if not success:
            raise HTTPException(status_code=404, detail="Job not found")

        return {
            "success": True,
            "message": "Job cleaned up successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cleanup job: {e}")
        raise HTTPException(status_code=500, detail="Failed to cleanup job")