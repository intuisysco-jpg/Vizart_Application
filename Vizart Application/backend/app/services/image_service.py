import os
import uuid
from PIL import Image
from typing import Dict, Any, Tuple
from app.core.logging import get_logger

logger = get_logger(__name__)

class ImageService:
    """Service for handling image operations."""

    async def get_image_info(self, image_path: str) -> Dict[str, Any]:
        """Get basic information about an image file."""
        try:
            with Image.open(image_path) as img:
                return {
                    "dimensions": {
                        "width": img.width,
                        "height": img.height
                    },
                    "mode": img.mode,
                    "format": img.format
                }
        except Exception as e:
            logger.error(f"Failed to get image info for {image_path}: {e}")
            raise ValueError(f"Invalid image file: {e}")

    async def validate_image(self, image_path: str) -> bool:
        """Validate if the file is a proper image."""
        try:
            with Image.open(image_path) as img:
                img.verify()
            return True
        except Exception as e:
            logger.error(f"Image validation failed for {image_path}: {e}")
            return False

    async def resize_image(
        self,
        input_path: str,
        output_path: str,
        target_size: Tuple[int, int],
        maintain_aspect_ratio: bool = True,
        quality: int = 95
    ) -> Dict[str, Any]:
        """Resize an image to target dimensions."""
        try:
            with Image.open(input_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')

                original_size = (img.width, img.height)

                if maintain_aspect_ratio:
                    img.thumbnail(target_size, Image.Resampling.LANCZOS)
                    final_size = (img.width, img.height)
                else:
                    img = img.resize(target_size, Image.Resampling.LANCZOS)
                    final_size = target_size

                # Save the resized image
                img.save(output_path, 'JPEG', quality=quality, optimize=True)

                logger.info(f"Image resized from {original_size} to {final_size}")

                return {
                    "success": True,
                    "original_size": original_size,
                    "final_size": final_size,
                    "file_size": os.path.getsize(output_path)
                }

        except Exception as e:
            logger.error(f"Failed to resize image {input_path}: {e}")
            raise ValueError(f"Image resize failed: {e}")

    async def create_thumbnail(
        self,
        input_path: str,
        output_path: str,
        size: Tuple[int, int] = (150, 150)
    ) -> str:
        """Create a thumbnail of an image."""
        try:
            with Image.open(input_path) as img:
                img.thumbnail(size, Image.Resampling.LANCZOS)

                # Ensure thumbnail has proper dimensions
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')

                img.save(output_path, 'JPEG', quality=85, optimize=True)

                logger.info(f"Thumbnail created: {output_path}")
                return output_path

        except Exception as e:
            logger.error(f"Failed to create thumbnail for {input_path}: {e}")
            raise ValueError(f"Thumbnail creation failed: {e}")

    async def crop_center(self, input_path: str, output_path: str, target_size: Tuple[int, int]) -> Dict[str, Any]:
        """Crop the center of an image to target dimensions."""
        try:
            with Image.open(input_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')

                width, height = img.size
                target_width, target_height = target_size

                # Calculate crop coordinates
                left = (width - target_width) // 2
                top = (height - target_height) // 2
                right = left + target_width
                bottom = top + target_height

                # Ensure we don't crop outside the image bounds
                left = max(0, left)
                top = max(0, top)
                right = min(width, right)
                bottom = min(height, bottom)

                # Crop and save
                cropped_img = img.crop((left, top, right, bottom))
                cropped_img.save(output_path, 'JPEG', quality=95, optimize=True)

                logger.info(f"Image cropped to {cropped_img.size}")

                return {
                    "success": True,
                    "original_size": (width, height),
                    "cropped_size": cropped_img.size,
                    "crop_coords": (left, top, right, bottom)
                }

        except Exception as e:
            logger.error(f"Failed to crop image {input_path}: {e}")
            raise ValueError(f"Image crop failed: {e}")