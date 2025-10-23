import os
import cv2
import numpy as np
from typing import Dict, Any, Optional, List, Callable
from PIL import Image
import mediapipe as mp
import rembg
from app.core.config import settings
from app.core.logging import get_logger
from app.services.image_service import ImageService

logger = get_logger(__name__)

class AIProcessor:
    """AI processor for virtual try-on and try-off operations."""

    def __init__(self):
        self.device = settings.MODEL_DEVICE
        self.image_service = ImageService()

        # Initialize MediaPipe for pose detection
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=2,
            enable_segmentation=True,
            min_detection_confidence=0.5
        )

        # Initialize background remover
        self.bg_remover = rembg.new_session('u2net')

        logger.info(f"AI Processor initialized on device: {self.device}")

    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about available AI models and their capabilities."""
        return {
            "pose_detection": {
                "model": "MediaPipe Pose",
                "capabilities": ["human_pose_estimation", "segmentation"],
                "device": self.device
            },
            "background_removal": {
                "model": "U2Net",
                "capabilities": ["background_removal", "foreground_segmentation"],
                "device": self.device
            },
            "try_on": {
                "status": "in_development",
                "capabilities": ["garment_warping", "pose_transfer", "image_generation"],
                "supported_garments": ["upper", "lower", "full"],
                "processing_time": "30-90 seconds"
            },
            "try_off": {
                "status": "in_development",
                "capabilities": ["garment_segmentation", "extraction", "classification"],
                "supported_garments": ["upper", "lower", "full"],
                "processing_time": "45-120 seconds"
            }
        }

    async def process_try_on(
        self,
        model_path: str,
        garment_path: str,
        options: Dict[str, Any],
        job_id: str,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Dict[str, Any]:
        """Process a try-on request using AI models."""
        try:
            if progress_callback:
                progress_callback(20.0, "Loading model image...")

            # Load and preprocess model image
            model_image = cv2.imread(model_path)
            if model_image is None:
                raise ValueError(f"Could not load model image: {model_path}")

            if progress_callback:
                progress_callback(30.0, "Detecting human pose...")

            # Detect human pose
            pose_result = await self._detect_pose(model_image)
            if not pose_result["success"]:
                raise ValueError("Failed to detect human pose in model image")

            if progress_callback:
                progress_callback(40.0, "Loading garment image...")

            # Load and preprocess garment image
            garment_image = cv2.imread(garment_path)
            if garment_image is None:
                raise ValueError(f"Could not load garment image: {garment_path}")

            if progress_callback:
                progress_callback(50.0, "Removing garment background...")

            # Remove background from garment
            garment_mask = await self._remove_background(garment_path)

            if progress_callback:
                progress_callback(60.0, "Warping garment to pose...")

            # Warp garment to fit model pose
            warped_garment = await self._warp_garment_to_pose(
                garment_image, garment_mask, pose_result, options
            )

            if progress_callback:
                progress_callback(75.0, "Blending with model...")

            # Blend warped garment with model image
            result_image = await self._blend_garment_with_model(
                model_image, warped_garment, pose_result, options
            )

            if progress_callback:
                progress_callback(85.0, "Saving result...")

            # Save result image
            result_filename = await self._save_result_image(result_image, job_id)

            if progress_callback:
                progress_callback(95.0, "Finalizing...")

            # Create result data
            result_data = {
                "result_image_url": f"/static/results/{result_filename}",
                "processing_info": {
                    "model_detected": True,
                    "pose_confidence": pose_result["confidence"],
                    "garment_type": options.get("garment_type", "upper"),
                    "preserve_background": options.get("preserve_background", False)
                }
            }

            return result_data

        except Exception as e:
            logger.error(f"Try-on processing failed: {e}")
            raise

    async def process_try_off(
        self,
        model_path: str,
        options: Dict[str, Any],
        job_id: str,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Dict[str, Any]:
        """Process a try-off request to extract garments from model."""
        try:
            if progress_callback:
                progress_callback(20.0, "Loading model image...")

            # Load model image
            model_image = cv2.imread(model_path)
            if model_image is None:
                raise ValueError(f"Could not load model image: {model_path}")

            if progress_callback:
                progress_callback(30.0, "Detecting human pose...")

            # Detect human pose
            pose_result = await self._detect_pose(model_image)
            if not pose_result["success"]:
                raise ValueError("Failed to detect human pose in model image")

            if progress_callback:
                progress_callback(40.0, "Segmenting garments...")

            # Segment and extract garments
            extracted_garments = await self._extract_garments(
                model_image, pose_result, options, progress_callback
            )

            if progress_callback:
                progress_callback(85.0, "Saving results...")

            # Save extracted garments
            saved_garments = []
            for garment in extracted_garments:
                filename = await self._save_garment_image(garment["image"], job_id, garment["type"])
                saved_garments.append({
                    "type": garment["type"],
                    "image_url": f"/static/results/{filename}",
                    "confidence": garment["confidence"],
                    "mask_url": f"/static/results/{filename.replace('.jpg', '_mask.jpg')}"
                })

            if progress_callback:
                progress_callback(95.0, "Finalizing...")

            result_data = {
                "extracted_garments": saved_garments,
                "processing_info": {
                    "model_detected": True,
                    "pose_confidence": pose_result["confidence"],
                    "total_garments": len(extracted_garments),
                    "garment_types": [g["type"] for g in saved_garments]
                }
            }

            return result_data

        except Exception as e:
            logger.error(f"Try-off processing failed: {e}")
            raise

    async def generate_preview(
        self,
        model_path: str,
        garment_path: Optional[str],
        processing_type: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a quick preview of processing results."""
        try:
            if processing_type == "try-on" and not garment_path:
                raise ValueError("Garment image required for try-on preview")

            # Create a small thumbnail preview
            if processing_type == "try-on":
                # Simple overlay preview for try-on
                preview_image = await self._create_try_on_preview(model_path, garment_path)
            else:
                # Simple segmentation preview for try-off
                preview_image = await self._create_try_off_preview(model_path)

            # Save preview
            preview_filename = f"preview_{uuid.uuid4().hex}.jpg"
            preview_path = os.path.join(settings.RESULTS_DIR, preview_filename)
            cv2.imwrite(preview_path, preview_image)

            return {
                "preview_url": f"/static/results/{preview_filename}",
                "processing_estimate": {
                    "try-on": "30-60 seconds",
                    "try-off": "45-90 seconds"
                }.get(processing_type, "60-120 seconds")
            }

        except Exception as e:
            logger.error(f"Preview generation failed: {e}")
            raise

    async def _detect_pose(self, image: np.ndarray) -> Dict[str, Any]:
        """Detect human pose in image."""
        try:
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_image)

            if not results.pose_landmarks:
                return {"success": False, "message": "No human pose detected"}

            # Extract landmark coordinates
            landmarks = []
            for landmark in results.pose_landmarks.landmark:
                landmarks.append({
                    "x": landmark.x,
                    "y": landmark.y,
                    "z": landmark.z,
                    "visibility": landmark.visibility
                })

            # Calculate pose confidence
            confidence = sum(l["visibility"] for l in landmarks) / len(landmarks)

            return {
                "success": True,
                "landmarks": landmarks,
                "confidence": confidence,
                "segmentation_mask": results.segmentation_mask
            }

        except Exception as e:
            logger.error(f"Pose detection failed: {e}")
            return {"success": False, "message": str(e)}

    async def _remove_background(self, image_path: str) -> np.ndarray:
        """Remove background from image using rembg."""
        try:
            # Load image
            image = Image.open(image_path)

            # Remove background
            output = rembg.remove(image, session=self.bg_remover)

            # Convert to numpy array and return mask
            mask = np.array(output)

            # Create binary mask (1 for foreground, 0 for background)
            if len(mask.shape) == 3:  # RGB image
                # Create mask from alpha channel or by checking if pixel is not white
                if mask.shape[2] == 4:  # RGBA
                    mask = mask[:, :, 3] > 0
                else:
                    # Convert to grayscale and threshold
                    gray = cv2.cvtColor(mask, cv2.COLOR_RGB2GRAY)
                    _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
                    mask = mask > 0

            return mask.astype(np.uint8)

        except Exception as e:
            logger.error(f"Background removal failed: {e}")
            raise

    async def _warp_garment_to_pose(
        self,
        garment_image: np.ndarray,
        garment_mask: np.ndarray,
        pose_result: Dict[str, Any],
        options: Dict[str, Any]
    ) -> np.ndarray:
        """Warp garment to fit the model's pose."""
        try:
            # This is a simplified implementation
            # In a production system, you would use more sophisticated warping algorithms

            garment_type = options.get("garment_type", "upper")
            landmarks = pose_result["landmarks"]

            # Define key points for garment warping based on type
            if garment_type == "upper":
                # Use shoulder, chest, and waist landmarks for upper garments
                key_points = [
                    landmarks[11],  # left shoulder
                    landmarks[12],  # right shoulder
                    landmarks[23],  # left hip
                    landmarks[24],  # right hip
                ]
            elif garment_type == "lower":
                # Use hip and leg landmarks for lower garments
                key_points = [
                    landmarks[23],  # left hip
                    landmarks[24],  # right hip
                    landmarks[25],  # left knee
                    landmarks[26],  # right knee
                ]
            else:  # full
                # Use full body landmarks
                key_points = landmarks[11:27]  # shoulder to feet

            # For now, return the original garment with mask applied
            # In a real implementation, you would perform perspective transformation
            garment_with_mask = cv2.bitwise_and(garment_image, garment_image, mask=garment_mask)

            return garment_with_mask

        except Exception as e:
            logger.error(f"Garment warping failed: {e}")
            raise

    async def _blend_garment_with_model(
        self,
        model_image: np.ndarray,
        warped_garment: np.ndarray,
        pose_result: Dict[str, Any],
        options: Dict[str, Any]
    ) -> np.ndarray:
        """Blend the warped garment with the model image."""
        try:
            # Simple overlay implementation
            # In production, you would use more sophisticated blending techniques

            garment_type = options.get("garment_type", "upper")
            preserve_background = options.get("preserve_background", False)

            if not preserve_background:
                # Remove background from model
                model_mask = await self._remove_background_from_person(model_image)
                model_image = cv2.bitwise_and(model_image, model_image, mask=model_mask)

            # Create a result image
            result = model_image.copy()

            # For demonstration, overlay garment in center
            # In production, you would position it based on pose landmarks
            h, w = warped_garment.shape[:2]
            start_x = (result.shape[1] - w) // 2
            start_y = (result.shape[0] - h) // 2

            if start_x >= 0 and start_y >= 0:
                # Overlay garment
                end_x = start_x + w
                end_y = start_y + h

                # Ensure we don't go out of bounds
                end_x = min(end_x, result.shape[1])
                end_y = min(end_y, result.shape[0])

                # Adjust garment size if needed
                garment_resized = cv2.resize(warped_garment, (end_x - start_x, end_y - start_y))

                # Simple alpha blending
                alpha = 0.8  # Transparency
                result[start_y:end_y, start_x:end_x] = cv2.addWeighted(
                    result[start_y:end_y, start_x:end_x],
                    1 - alpha,
                    garment_resized,
                    alpha,
                    0
                )

            return result

        except Exception as e:
            logger.error(f"Garment blending failed: {e}")
            raise

    async def _extract_garments(
        self,
        model_image: np.ndarray,
        pose_result: Dict[str, Any],
        options: Dict[str, Any],
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> List[Dict[str, Any]]:
        """Extract garments from the model image."""
        try:
            extracted_garments = []
            garment_types = options.get("garment_types", ["upper", "lower"])

            if "upper" in garment_types:
                if progress_callback:
                    progress_callback(50.0, "Extracting upper body garment...")

                # Extract upper body garment
                upper_garment = await self._extract_upper_body_garment(model_image, pose_result)
                if upper_garment:
                    extracted_garments.append(upper_garment)

            if "lower" in garment_types:
                if progress_callback:
                    progress_callback(65.0, "Extracting lower body garment...")

                # Extract lower body garment
                lower_garment = await self._extract_lower_body_garment(model_image, pose_result)
                if lower_garment:
                    extracted_garments.append(lower_garment)

            if "full" in garment_types:
                if progress_callback:
                    progress_callback(75.0, "Extracting full body garment...")

                # Extract full body garment
                full_garment = await self._extract_full_body_garment(model_image, pose_result)
                if full_garment:
                    extracted_garments.append(full_garment)

            return extracted_garments

        except Exception as e:
            logger.error(f"Garment extraction failed: {e}")
            raise

    async def _extract_upper_body_garment(self, model_image: np.ndarray, pose_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract upper body garment."""
        try:
            landmarks = pose_result["landmarks"]
            h, w = model_image.shape[:2]

            # Define bounding box for upper body based on landmarks
            top_shoulder = min(landmarks[11]["y"], landmarks[12]["y"]) * h
            bottom_hip = max(landmarks[23]["y"], landmarks[24]["y"]) * h

            left_shoulder = landmarks[11]["x"] * w
            right_shoulder = landmarks[12]["x"] * w

            # Add padding
            padding = 20
            y1 = max(0, int(top_shoulder - padding))
            y2 = min(h, int(bottom_hip + padding))
            x1 = max(0, int(min(left_shoulder, right_shoulder) - padding))
            x2 = min(w, int(max(left_shoulder, right_shoulder) + padding))

            # Extract upper body region
            upper_body = model_image[y1:y2, x1:x2]

            return {
                "type": "upper",
                "image": upper_body,
                "confidence": pose_result["confidence"],
                "bbox": [x1, y1, x2, y2]
            }

        except Exception as e:
            logger.error(f"Upper body garment extraction failed: {e}")
            return None

    async def _extract_lower_body_garment(self, model_image: np.ndarray, pose_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract lower body garment."""
        try:
            landmarks = pose_result["landmarks"]
            h, w = model_image.shape[:2]

            # Define bounding box for lower body based on landmarks
            top_hip = min(landmarks[23]["y"], landmarks[24]["y"]) * h
            bottom_knee = max(landmarks[25]["y"], landmarks[26]["y"]) * h

            left_hip = landmarks[23]["x"] * w
            right_hip = landmarks[24]["x"] * w

            # Add padding
            padding = 20
            y1 = max(0, int(top_hip - padding))
            y2 = min(h, int(bottom_knee + padding))
            x1 = max(0, int(min(left_hip, right_hip) - padding))
            x2 = min(w, int(max(left_hip, right_hip) + padding))

            # Extract lower body region
            lower_body = model_image[y1:y2, x1:x2]

            return {
                "type": "lower",
                "image": lower_body,
                "confidence": pose_result["confidence"],
                "bbox": [x1, y1, x2, y2]
            }

        except Exception as e:
            logger.error(f"Lower body garment extraction failed: {e}")
            return None

    async def _extract_full_body_garment(self, model_image: np.ndarray, pose_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract full body garment."""
        try:
            # For now, return the entire image with the person
            # In a real implementation, you would segment the full body
            return {
                "type": "full",
                "image": model_image,
                "confidence": pose_result["confidence"],
                "bbox": [0, 0, model_image.shape[1], model_image.shape[0]]
            }

        except Exception as e:
            logger.error(f"Full body garment extraction failed: {e}")
            return None

    async def _remove_background_from_person(self, image: np.ndarray) -> np.ndarray:
        """Remove background leaving only the person."""
        try:
            # Use MediaPipe segmentation
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_image)

            if results.segmentation_mask is not None:
                # Convert segmentation mask to binary mask
                mask = (results.segmentation_mask > 0.5).astype(np.uint8) * 255
                return mask
            else:
                # Fallback: use background removal
                from PIL import Image
                pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                output = rembg.remove(pil_image, session=self.bg_remover)

                if len(np.array(output).shape) == 3 and np.array(output).shape[2] == 4:
                    mask = np.array(output)[:, :, 3] > 0
                    return (mask * 255).astype(np.uint8)
                else:
                    # Create a simple mask (this is a fallback)
                    return np.ones((image.shape[0], image.shape[1]), dtype=np.uint8) * 255

        except Exception as e:
            logger.error(f"Background removal from person failed: {e}")
            # Return a mask that keeps everything
            return np.ones((image.shape[0], image.shape[1]), dtype=np.uint8) * 255

    async def _create_try_on_preview(self, model_path: str, garment_path: str) -> np.ndarray:
        """Create a simple preview for try-on."""
        # Load images and create side-by-side preview
        model = cv2.imread(model_path)
        garment = cv2.imread(garment_path)

        if model is None or garment is None:
            raise ValueError("Could not load images for preview")

        # Resize to same height
        target_height = 300
        model_resized = cv2.resize(model, (int(model.shape[1] * target_height / model.shape[0]), target_height))
        garment_resized = cv2.resize(garment, (int(garment.shape[1] * target_height / garment.shape[0]), target_height))

        # Create side-by-side image
        preview = np.hstack([model_resized, garment_resized])

        return preview

    async def _create_try_off_preview(self, model_path: str) -> np.ndarray:
        """Create a simple preview for try-off."""
        # Load and resize image
        model = cv2.imread(model_path)
        if model is None:
            raise ValueError("Could not load image for preview")

        target_height = 400
        preview = cv2.resize(model, (int(model.shape[1] * target_height / model.shape[0]), target_height))

        # Add "SEGMENTED" text overlay
        cv2.putText(preview, "SEGMENTATION PREVIEW", (50, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        return preview

    async def _save_result_image(self, image: np.ndarray, job_id: str) -> str:
        """Save result image to disk."""
        filename = f"{job_id}_result.jpg"
        filepath = os.path.join(settings.RESULTS_DIR, filename)
        cv2.imwrite(filepath, image, [cv2.IMWRITE_JPEG_QUALITY, 95])
        return filename

    async def _save_garment_image(self, image: np.ndarray, job_id: str, garment_type: str) -> str:
        """Save extracted garment image to disk."""
        filename = f"{job_id}_{garment_type}_garment.jpg"
        filepath = os.path.join(settings.RESULTS_DIR, filename)
        cv2.imwrite(filepath, image, [cv2.IMWRITE_JPEG_QUALITY, 95])
        return filename