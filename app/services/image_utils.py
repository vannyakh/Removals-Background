"""
Image Utilities
Helper functions for image processing
"""
import cv2
import numpy as np
from PIL import Image
from typing import Tuple, Optional
import logging

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def resize_with_aspect_ratio(
    image: Image.Image,
    max_size: int,
    min_size: Optional[int] = None
) -> Image.Image:
    """
    Resize image maintaining aspect ratio
    
    Args:
        image: PIL Image
        max_size: Maximum dimension (width or height)
        min_size: Minimum dimension (optional)
        
    Returns:
        Resized PIL Image
    """
    width, height = image.size
    
    # Calculate scaling factor
    scale = max_size / max(width, height)
    
    if min_size:
        min_scale = min_size / min(width, height)
        scale = min(scale, min_scale)
    
    new_width = int(width * scale)
    new_height = int(height * scale)
    
    return image.resize((new_width, new_height), Image.LANCZOS)


def apply_mask_smoothing(mask: np.ndarray, kernel_size: int = 5) -> np.ndarray:
    """
    Apply Gaussian smoothing to mask for better edges
    
    Args:
        mask: Binary mask array (0-255)
        kernel_size: Gaussian kernel size (must be odd)
        
    Returns:
        Smoothed mask
    """
    if kernel_size % 2 == 0:
        kernel_size += 1
    
    # Convert to float for processing
    mask_float = mask.astype(np.float32) / 255.0
    
    # Apply Gaussian blur
    smoothed = cv2.GaussianBlur(mask_float, (kernel_size, kernel_size), 0)
    
    # Convert back to uint8
    return (smoothed * 255).astype(np.uint8)


def refine_mask_edges(
    mask: np.ndarray,
    image: np.ndarray,
    edge_threshold: float = 0.5
) -> np.ndarray:
    """
    Refine mask edges using image gradients
    
    Args:
        mask: Binary mask array (0-255)
        image: Original image array (RGB)
        edge_threshold: Threshold for edge detection
        
    Returns:
        Refined mask
    """
    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    # Apply Canny edge detection
    edges = cv2.Canny(gray, 50, 150)
    
    # Dilate edges slightly
    kernel = np.ones((3, 3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)
    
    # Use edges to refine mask boundaries
    mask_float = mask.astype(np.float32) / 255.0
    
    # Where edges exist, slightly adjust mask
    edge_mask = (edges > 0).astype(np.float32)
    refined = mask_float * (1 - edge_mask * 0.1) + edge_mask * mask_float
    
    # Ensure values stay in valid range
    refined = np.clip(refined, 0, 1)
    
    return (refined * 255).astype(np.uint8)


def create_alpha_channel(image: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """
    Create RGBA image from RGB image and mask
    
    Args:
        image: RGB image array
        mask: Alpha mask array (0-255)
        
    Returns:
        RGBA image array
    """
    # Normalize mask to 0-1 range
    alpha = mask.astype(np.float32) / 255.0
    
    # Ensure image and mask have same dimensions
    if image.shape[:2] != mask.shape[:2]:
        mask = cv2.resize(mask, (image.shape[1], image.shape[0]))
        alpha = mask.astype(np.float32) / 255.0
    
    # Create RGBA image
    if len(image.shape) == 2:
        # Grayscale to RGB
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    
    rgba = np.dstack((image, (alpha * 255).astype(np.uint8)))
    return rgba


def enhance_mask_quality(mask: np.ndarray) -> np.ndarray:
    """
    Enhance mask quality with morphological operations
    
    Args:
        mask: Binary mask array (0-255)
        
    Returns:
        Enhanced mask
    """
    # Convert to binary
    _, binary = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
    
    # Remove small noise
    kernel = np.ones((3, 3), np.uint8)
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # Fill small holes
    filled = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel, iterations=1)
    
    return filled


def normalize_image_for_model(image: Image.Image) -> np.ndarray:
    """
    Normalize image for model input
    
    Args:
        image: PIL Image
        
    Returns:
        Normalized numpy array ready for model
    """
    # Convert to RGB if needed
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Convert to numpy array
    img_array = np.array(image).astype(np.float32)
    
    # Normalize to [0, 1]
    img_array = img_array / 255.0
    
    # Apply ImageNet normalization
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    
    img_array = (img_array - mean) / std
    
    # Convert to CHW format
    img_array = np.transpose(img_array, (2, 0, 1))
    
    return img_array

