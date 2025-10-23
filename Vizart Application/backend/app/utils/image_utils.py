import cv2
import numpy as np
from PIL import Image, ImageOps, ImageEnhance
from typing import Tuple, Optional, Dict, Any
from app.core.logging import get_logger

logger = get_logger(__name__)

class ImageUtils:
    """Utility functions for image processing."""

    @staticmethod
    def load_image(image_path: str) -> Optional[np.ndarray]:
        """Load an image using OpenCV."""
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            return image
        except Exception as e:
            logger.error(f"Failed to load image {image_path}: {e}")
            return None

    @staticmethod
    def save_image(image: np.ndarray, output_path: str, quality: int = 95) -> bool:
        """Save an image using OpenCV."""
        try:
            # Create directory if it doesn't exist
            import os
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Save with specified quality
            cv2.imwrite(output_path, image, [cv2.IMWRITE_JPEG_QUALITY, quality])
            return True
        except Exception as e:
            logger.error(f"Failed to save image {output_path}: {e}")
            return False

    @staticmethod
    def resize_image(
        image: np.ndarray,
        target_size: Tuple[int, int],
        maintain_aspect_ratio: bool = True,
        interpolation: int = cv2.INTER_LINEAR
    ) -> np.ndarray:
        """Resize an image to target dimensions."""
        try:
            h, w = image.shape[:2]
            target_w, target_h = target_size

            if maintain_aspect_ratio:
                # Calculate new dimensions maintaining aspect ratio
                aspect_ratio = w / h
                if target_w / target_h > aspect_ratio:
                    new_h = target_h
                    new_w = int(target_h * aspect_ratio)
                else:
                    new_w = target_w
                    new_h = int(target_w / aspect_ratio)

                resized = cv2.resize(image, (new_w, new_h), interpolation=interpolation)
            else:
                resized = cv2.resize(image, target_size, interpolation=interpolation)

            return resized

        except Exception as e:
            logger.error(f"Failed to resize image: {e}")
            raise

    @staticmethod
    def crop_center(image: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
        """Crop the center of an image to target dimensions."""
        try:
            h, w = image.shape[:2]
            target_w, target_h = target_size

            # Calculate crop coordinates
            start_x = max(0, (w - target_w) // 2)
            start_y = max(0, (h - target_h) // 2)
            end_x = min(w, start_x + target_w)
            end_y = min(h, start_y + target_h)

            return image[start_y:end_y, start_x:end_x]

        except Exception as e:
            logger.error(f"Failed to crop image: {e}")
            raise

    @staticmethod
    def apply_gaussian_blur(image: np.ndarray, kernel_size: int = 5) -> np.ndarray:
        """Apply Gaussian blur to an image."""
        try:
            # Ensure kernel size is odd
            if kernel_size % 2 == 0:
                kernel_size += 1

            return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)

        except Exception as e:
            logger.error(f"Failed to apply Gaussian blur: {e}")
            raise

    @staticmethod
    def enhance_brightness_contrast(
        image: np.ndarray,
        alpha: float = 1.0,  # Contrast control (1.0-3.0)
        beta: int = 0        # Brightness control (0-100)
    ) -> np.ndarray:
        """Enhance brightness and contrast of an image."""
        try:
            # Apply contrast and brightness
            enhanced = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
            return enhanced

        except Exception as e:
            logger.error(f"Failed to enhance brightness/contrast: {e}")
            raise

    @staticmethod
    def remove_background_simple(image: np.ndarray, threshold: int = 240) -> Tuple[np.ndarray, np.ndarray]:
        """Simple background removal using color thresholding."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Apply threshold to create mask
            _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)

            # Apply mask to image
            foreground = cv2.bitwise_and(image, image, mask=mask)

            return foreground, mask

        except Exception as e:
            logger.error(f"Failed to remove background: {e}")
            raise

    @staticmethod
    def create_thumbnail(image: np.ndarray, size: Tuple[int, int] = (150, 150)) -> np.ndarray:
        """Create a thumbnail of an image."""
        try:
            # Resize maintaining aspect ratio
            thumbnail = ImageUtils.resize_image(image, size, maintain_aspect_ratio=True)

            # If image is smaller than target size, pad it
            h, w = thumbnail.shape[:2]
            target_w, target_h = size

            if h < target_h or w < target_w:
                # Create a black canvas
                canvas = np.zeros((target_h, target_w, 3), dtype=np.uint8)

                # Calculate position to center the image
                start_x = (target_w - w) // 2
                start_y = (target_h - h) // 2

                # Place image in center
                canvas[start_y:start_y+h, start_x:start_x+w] = thumbnail

                return canvas

            return thumbnail

        except Exception as e:
            logger.error(f"Failed to create thumbnail: {e}")
            raise

    @staticmethod
    def get_image_stats(image: np.ndarray) -> Dict[str, Any]:
        """Get basic statistics about an image."""
        try:
            h, w = image.shape[:2]
            channels = image.shape[2] if len(image.shape) > 2 else 1

            # Calculate mean brightness
            if len(image.shape) == 3:
                brightness = np.mean(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
            else:
                brightness = np.mean(image)

            return {
                "width": w,
                "height": h,
                "channels": channels,
                "total_pixels": h * w,
                "aspect_ratio": w / h,
                "mean_brightness": float(brightness),
                "size_mb": image.nbytes / (1024 * 1024)
            }

        except Exception as e:
            logger.error(f"Failed to get image stats: {e}")
            return {}

    @staticmethod
    def calculate_histogram(image: np.ndarray) -> Dict[str, np.ndarray]:
        """Calculate histogram for each color channel."""
        try:
            histograms = {}

            if len(image.shape) == 3:
                # Color image
                colors = ['b', 'g', 'r']
                for i, color in enumerate(colors):
                    hist = cv2.calcHist([image], [i], None, [256], [0, 256])
                    histograms[color] = hist.flatten()
            else:
                # Grayscale image
                hist = cv2.calcHist([image], [0], None, [256], [0, 256])
                histograms['gray'] = hist.flatten()

            return histograms

        except Exception as e:
            logger.error(f"Failed to calculate histogram: {e}")
            return {}

    @staticmethod
    def rotate_image(image: np.ndarray, angle: float, center: Optional[Tuple[int, int]] = None) -> np.ndarray:
        """Rotate an image by a given angle."""
        try:
            h, w = image.shape[:2]

            if center is None:
                center = (w // 2, h // 2)

            # Get rotation matrix
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

            # Perform rotation
            rotated = cv2.warpAffine(image, rotation_matrix, (w, h), flags=cv2.INTER_LINEAR)

            return rotated

        except Exception as e:
            logger.error(f"Failed to rotate image: {e}")
            raise

    @staticmethod
    def apply_edge_detection(image: np.ndarray, low_threshold: int = 50, high_threshold: int = 150) -> np.ndarray:
        """Apply Canny edge detection."""
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image

            # Apply Canny edge detection
            edges = cv2.Canny(gray, low_threshold, high_threshold)

            return edges

        except Exception as e:
            logger.error(f"Failed to apply edge detection: {e}")
            raise