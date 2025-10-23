from typing import Dict, Any, Optional, List
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

class ValidationUtils:
    """Utility functions for data validation."""

    @staticmethod
    def validate_image_upload(file) -> Dict[str, Any]:
        """Validate an uploaded image file."""
        errors = []

        # Check if file is provided
        if not file:
            return {"valid": False, errors: ["No file provided"]}

        # Check file size
        if file.size and file.size > settings.MAX_UPLOAD_SIZE:
            errors.append(f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE / (1024*1024):.1f}MB")

        # Check content type
        if file.content_type not in settings.ALLOWED_MIME_TYPES:
            errors.append(f"File type {file.content_type} is not allowed")

        # Check filename
        if file.filename:
            if not file.filename.strip():
                errors.append("Filename cannot be empty")

            # Check file extension
            from app.utils.file_utils import FileUtils
            if not FileUtils.is_valid_image_extension(file.filename):
                errors.append("File extension not allowed")

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    @staticmethod
    def validate_job_options(options: Dict[str, Any], job_type: str) -> Dict[str, Any]:
        """Validate job processing options."""
        errors = []

        if not isinstance(options, dict):
            return {"valid": False, errors: ["Options must be a dictionary"]}

        if job_type == "try-on":
            # Validate try-on specific options
            if "garment_type" in options:
                garment_type = options["garment_type"]
                if garment_type not in ["upper", "lower", "full"]:
                    errors.append("garment_type must be one of: upper, lower, full")

            if "preserve_background" in options:
                if not isinstance(options["preserve_background"], bool):
                    errors.append("preserve_background must be a boolean")

            if "adjust_size" in options:
                if not isinstance(options["adjust_size"], bool):
                    errors.append("adjust_size must be a boolean")

        elif job_type == "try-off":
            # Validate try-off specific options
            if "extract_all" in options:
                if not isinstance(options["extract_all"], bool):
                    errors.append("extract_all must be a boolean")

            if "garment_types" in options:
                garment_types = options["garment_types"]
                if not isinstance(garment_types, list):
                    errors.append("garment_types must be a list")
                else:
                    valid_types = ["upper", "lower", "full"]
                    for garment_type in garment_types:
                        if garment_type not in valid_types:
                            errors.append(f"Invalid garment_type: {garment_type}. Must be one of: {valid_types}")

            if "output_format" in options:
                output_format = options["output_format"]
                if output_format not in ["png", "jpg", "webp"]:
                    errors.append("output_format must be one of: png, jpg, webp")

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    @staticmethod
    def validate_pagination_parameters(
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> Dict[str, Any]:
        """Validate pagination parameters."""
        errors = []

        if limit is not None:
            if not isinstance(limit, int) or limit <= 0:
                errors.append("limit must be a positive integer")
            elif limit > 100:
                errors.append("limit cannot exceed 100")

        if offset is not None:
            if not isinstance(offset, int) or offset < 0:
                errors.append("offset must be a non-negative integer")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "limit": limit or 50,
            "offset": offset or 0
        }

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent path traversal attacks."""
        import re
        import os

        # Remove path separators and parent directory references
        filename = os.path.basename(filename)

        # Remove any non-alphanumeric characters except dots, underscores, and hyphens
        filename = re.sub(r'[^\w\-_\.]', '', filename)

        # Ensure filename is not empty
        if not filename:
            filename = "unknown_file"

        return filename

    @staticmethod
    def validate_uuid(uuid_string: str) -> bool:
        """Validate if a string is a valid UUID."""
        import uuid as uuid_lib
        try:
            uuid_lib.UUID(uuid_string)
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_email(email: str) -> bool:
        """Basic email validation."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Validate password strength."""
        errors = []
        score = 0

        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        else:
            score += 1

        if not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        else:
            score += 1

        if not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        else:
            score += 1

        if not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one digit")
        else:
            score += 1

        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            errors.append("Password must contain at least one special character")
        else:
            score += 1

        strength = ["Very Weak", "Weak", "Fair", "Good", "Strong"][min(score, 4)]

        return {
            "valid": len(errors) == 0,
            "strength": strength,
            "score": score,
            "errors": errors
        }