import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON, Enum
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from app.core.database import Base

class JobStatus(PyEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    job_type = Column(String, nullable=False)  # 'try-on' or 'try-off'
    progress = Column(Float, default=0.0)
    message = Column(String, default="")

    # Input file paths
    model_image_path = Column(String, nullable=False)
    garment_image_path = Column(String, nullable=True)

    # Result data
    result_data = Column(JSON, nullable=True)

    # Processing metadata
    processing_time = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Configuration
    options = Column(JSON, nullable=True)