"""
Foreground Detection Utilities
Calculate bounding box of foreground object
"""
import numpy as np
from PIL import Image
from typing import Tuple


def calculate_foreground_bbox(image: Image.Image, threshold: int = 10) -> Tuple[int, int, int, int]:
    """
    Calculate bounding box of foreground object in RGBA image
    
    Args:
        image: PIL Image with RGBA mode
        threshold: Alpha threshold (0-255) to consider as foreground
        
    Returns:
        Tuple of (left, top, width, height)
    """
    # Convert to numpy array
    img_array = np.array(image)
    
    # Extract alpha channel
    if img_array.shape[2] == 4:
        alpha = img_array[:, :, 3]
    else:
        # If no alpha channel, assume full image is foreground
        height, width = img_array.shape[:2]
        return (0, 0, width, height)
    
    # Find non-transparent pixels (foreground)
    foreground_mask = alpha > threshold
    
    if not np.any(foreground_mask):
        # No foreground found, return full image bounds
        height, width = alpha.shape
        return (0, 0, width, height)
    
    # Find bounding box
    rows = np.any(foreground_mask, axis=1)
    cols = np.any(foreground_mask, axis=0)
    
    if not np.any(rows) or not np.any(cols):
        height, width = alpha.shape
        return (0, 0, width, height)
    
    top = np.argmax(rows)
    bottom = len(rows) - np.argmax(rows[::-1])
    left = np.argmax(cols)
    right = len(cols) - np.argmax(cols[::-1])
    
    width = right - left
    height = bottom - top
    
    return (left, top, width, height)

