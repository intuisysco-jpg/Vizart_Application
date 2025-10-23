import os
import uuid
import aiofiles
import hashlib
from typing import Optional, Dict, Any
from pathlib import Path
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

class FileUtils:
    """Utility functions for file operations."""

    @staticmethod
    def get_file_hash(file_path: str) -> str:
        """Get MD5 hash of a file."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Get file size in bytes."""
        return os.path.getsize(file_path)

    @staticmethod
    def ensure_directory_exists(directory_path: str) -> None:
        """Ensure directory exists, create if it doesn't."""
        Path(directory_path).mkdir(parents=True, exist_ok=True)

    @staticmethod
    async def save_uploaded_file(
        uploaded_file,
        upload_dir: str = None,
        custom_filename: str = None
    ) -> Dict[str, Any]:
        """Save an uploaded file and return file information."""
        try:
            upload_dir = upload_dir or settings.UPLOAD_DIR
            FileUtils.ensure_directory_exists(upload_dir)

            # Generate filename
            if custom_filename:
                filename = custom_filename
            else:
                file_id = str(uuid.uuid4())
                file_extension = Path(uploaded_file.filename).suffix
                filename = f"{file_id}{file_extension}"

            file_path = os.path.join(upload_dir, filename)

            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await uploaded_file.read()
                await f.write(content)

            # Get file info
            file_size = len(content)
            file_hash = FileUtils.get_file_hash(file_path)

            logger.info(f"Saved uploaded file: {filename} ({file_size} bytes)")

            return {
                "filename": filename,
                "file_path": file_path,
                "file_size": file_size,
                "file_hash": file_hash,
                "original_filename": uploaded_file.filename,
                "content_type": uploaded_file.content_type
            }

        except Exception as e:
            logger.error(f"Failed to save uploaded file: {e}")
            raise

    @staticmethod
    def delete_file(file_path: str) -> bool:
        """Delete a file if it exists."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return False

    @staticmethod
    def copy_file(source_path: str, destination_path: str) -> bool:
        """Copy a file from source to destination."""
        try:
            import shutil
            FileUtils.ensure_directory_exists(os.path.dirname(destination_path))
            shutil.copy2(source_path, destination_path)
            logger.info(f"Copied file from {source_path} to {destination_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to copy file from {source_path} to {destination_path}: {e}")
            return False

    @staticmethod
    def move_file(source_path: str, destination_path: str) -> bool:
        """Move a file from source to destination."""
        try:
            import shutil
            FileUtils.ensure_directory_exists(os.path.dirname(destination_path))
            shutil.move(source_path, destination_path)
            logger.info(f"Moved file from {source_path} to {destination_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to move file from {source_path} to {destination_path}: {e}")
            return False

    @staticmethod
    def file_exists(file_path: str) -> bool:
        """Check if a file exists."""
        return os.path.exists(file_path)

    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Get file extension from filename."""
        return Path(filename).suffix.lower()

    @staticmethod
    def is_valid_image_extension(filename: str) -> bool:
        """Check if file has valid image extension."""
        valid_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
        return FileUtils.get_file_extension(filename) in valid_extensions