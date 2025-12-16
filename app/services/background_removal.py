"""
Background Removal Service
Main service for removing backgrounds from images
"""
import torch
import numpy as np
import cv2
from PIL import Image
from typing import Tuple
import logging

from app.config import settings
from app.core.model_manager import model_manager
from app.services.image_utils import (
    resize_with_aspect_ratio,
    apply_mask_smoothing,
    refine_mask_edges,
    create_alpha_channel,
    enhance_mask_quality,
    normalize_image_for_model
)
from app.utils.logger import setup_logger
from app.utils.exceptions import ModelNotLoadedError, ImageProcessingError

logger = setup_logger(__name__)


class BackgroundRemovalService:
    """Service for removing backgrounds from images"""
    
    def __init__(self):
        self.model_manager = model_manager
    
    def preprocess_image(
        self,
        image: Image.Image,
        target_size: int = None
    ) -> Tuple[torch.Tensor, Tuple[int, int]]:
        """
        Preprocess image for model input
        
        Args:
            image: PIL Image
            target_size: Target size for model input (default from config)
            
        Returns:
            Tuple of (preprocessed tensor, original size)
        """
        target_size = target_size or settings.INPUT_SIZE
        original_size = image.size
        
        # Resize maintaining aspect ratio
        if max(original_size) > settings.MAX_DIMENSION:
            image = resize_with_aspect_ratio(image, settings.MAX_DIMENSION)
        
        # Resize to model input size
        resized = image.resize((target_size, target_size), Image.LANCZOS)
        
        # Normalize
        img_array = normalize_image_for_model(resized)
        
        # Convert to tensor
        tensor = torch.from_numpy(img_array).unsqueeze(0)
        
        return tensor, original_size
    
    def predict_mask(
        self,
        input_tensor: torch.Tensor,
        use_multi_scale: bool = None
    ) -> torch.Tensor:
        """
        Predict mask using the model
        
        Args:
            input_tensor: Preprocessed image tensor
            use_multi_scale: Whether to use multi-scale inference
            
        Returns:
            Predicted mask tensor
        """
        use_multi_scale = use_multi_scale if use_multi_scale is not None else settings.USE_MULTI_SCALE
        
        model = self.model_manager.get_model()
        device = self.model_manager.get_device()
        input_tensor = input_tensor.to(device)
        
        with torch.no_grad():
            if use_multi_scale:
                # Multi-scale inference for better quality
                scales = [0.75, 1.0, 1.25]
                predictions = []
                
                for scale in scales:
                    if scale != 1.0:
                        scaled_size = int(settings.INPUT_SIZE * scale)
                        scaled_tensor = torch.nn.functional.interpolate(
                            input_tensor,
                            size=(scaled_size, scaled_size),
                            mode='bilinear',
                            align_corners=False
                        )
                    else:
                        scaled_tensor = input_tensor
                    
                    # Get model output
                    outputs = model(scaled_tensor)
                    pred = outputs[0][:, 0, :, :]
                    
                    # Normalize prediction
                    pred = self._normalize_prediction(pred)
                    
                    # Resize back to original input size
                    if scale != 1.0:
                        pred = torch.nn.functional.interpolate(
                            pred.unsqueeze(1),
                            size=(settings.INPUT_SIZE, settings.INPUT_SIZE),
                            mode='bilinear',
                            align_corners=False
                        ).squeeze(1)
                    
                    predictions.append(pred)
                
                # Average predictions
                final_pred = torch.mean(torch.stack(predictions), dim=0)
            else:
                # Single-scale inference
                outputs = model(input_tensor)
                pred = outputs[0][:, 0, :, :]
                final_pred = self._normalize_prediction(pred)
        
        return final_pred
    
    def _normalize_prediction(self, pred: torch.Tensor) -> torch.Tensor:
        """
        Normalize prediction to 0-1 range
        
        Args:
            pred: Prediction tensor
            
        Returns:
            Normalized prediction tensor
        """
        ma = torch.max(pred)
        mi = torch.min(pred)
        
        if ma == mi:
            return torch.zeros_like(pred)
        
        return (pred - mi) / (ma - mi)
    
    def postprocess_mask(
        self,
        mask: np.ndarray,
        original_image: np.ndarray,
        original_size: Tuple[int, int]
    ) -> np.ndarray:
        """
        Post-process mask for better quality
        
        Args:
            mask: Mask array (0-255)
            original_image: Original image array
            original_size: Original image size
            
        Returns:
            Post-processed mask
        """
        # Resize mask to original size
        mask_resized = cv2.resize(
            mask,
            original_size,
            interpolation=cv2.INTER_LANCZOS4
        )
        
        # Enhance mask quality
        if settings.MASK_SMOOTHING:
            mask_resized = enhance_mask_quality(mask_resized)
            mask_resized = apply_mask_smoothing(mask_resized, kernel_size=3)
        
        # Refine edges if enabled
        if settings.EDGE_REFINEMENT:
            try:
                mask_resized = refine_mask_edges(mask_resized, original_image)
            except Exception as e:
                logger.warning(f"Edge refinement failed: {e}")
        
        return mask_resized
    
    def remove_background(
        self,
        image: Image.Image
    ) -> Image.Image:
        """
        Remove background from image
        
        Args:
            image: PIL Image
            
        Returns:
            PIL Image with transparent background (RGBA)
            
        Raises:
            ModelNotLoadedError: If model is not loaded
            ImageProcessingError: If processing fails
        """
        if not self.model_manager.is_loaded():
            raise ModelNotLoadedError("Model is not loaded")
        
        try:
            # Validate image
            if image is None:
                raise ImageProcessingError("Invalid image provided")
            
            if image.size[0] == 0 or image.size[1] == 0:
                raise ImageProcessingError("Image has invalid dimensions")
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Preprocess
            input_tensor, original_size = self.preprocess_image(image)
            
            # Predict mask
            pred_tensor = self.predict_mask(input_tensor)
            
            # Convert to numpy
            pred_np = pred_tensor.squeeze().cpu().numpy()
            
            if pred_np.size == 0:
                raise ImageProcessingError("Model prediction failed - empty output")
            
            # Convert to 0-255 range
            mask = (pred_np * 255).astype(np.uint8)
            
            # Get original image as numpy array
            original_image_np = np.array(image)
            
            # Post-process mask
            mask = self.postprocess_mask(mask, original_image_np, original_size)
            
            # Create RGBA image
            rgba = create_alpha_channel(original_image_np, mask)
            
            # Convert to PIL Image
            result_image = Image.fromarray(rgba, 'RGBA')
            
            if result_image is None or result_image.size[0] == 0:
                raise ImageProcessingError("Failed to create result image")
            
            return result_image
            
        except (ModelNotLoadedError, ImageProcessingError):
            raise
        except Exception as e:
            logger.error(f"Error in remove_background: {e}", exc_info=True)
            raise ImageProcessingError(f"Failed to process image: {str(e)}")


# Global service instance
background_removal_service = BackgroundRemovalService()

