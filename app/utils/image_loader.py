"""
Image Loading Utilities
Handle image loading from various sources (file, base64, URL)
"""
import io
import base64
import aiohttp
from typing import Optional, Tuple
from PIL import Image
import logging

from app.utils.logger import setup_logger
from app.utils.exceptions import InvalidImageError

logger = setup_logger(__name__)


def decode_base64_image(base64_string: str) -> bytes:
    """
    Decode base64 encoded image string
    
    Args:
        base64_string: Base64 encoded image string (with or without data URL prefix)
        
    Returns:
        Decoded image bytes
        
    Raises:
        InvalidImageError: If base64 string is invalid
    """
    try:
        # Remove data URL prefix if present (e.g., "data:image/png;base64,")
        if ',' in base64_string:
            base64_string = base64_string.split(',', 1)[1]
        
        # Decode base64
        image_bytes = base64.b64decode(base64_string)
        return image_bytes
    except Exception as e:
        logger.error(f"Failed to decode base64 image: {str(e)}")
        raise InvalidImageError(f"Invalid base64 encoded image: {str(e)}")


async def download_image_from_url(url: str, max_size: int = 22 * 1024 * 1024) -> bytes:
    """
    Download image from URL
    
    Args:
        url: Image URL
        max_size: Maximum file size in bytes
        
    Returns:
        Image bytes
        
    Raises:
        InvalidImageError: If download fails or file is too large
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status != 200:
                    raise InvalidImageError(f"Failed to download image: HTTP {response.status}")
                
                # Check content length if available
                content_length = response.headers.get('Content-Length')
                if content_length and int(content_length) > max_size:
                    raise InvalidImageError(f"Image file size ({content_length} bytes) exceeds maximum ({max_size} bytes)")
                
                # Read image data
                image_bytes = await response.read()
                
                if len(image_bytes) > max_size:
                    raise InvalidImageError(f"Image file size ({len(image_bytes)} bytes) exceeds maximum ({max_size} bytes)")
                
                return image_bytes
    except aiohttp.ClientError as e:
        logger.error(f"Failed to download image from URL: {str(e)}")
        raise InvalidImageError(f"Failed to download image from URL: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error downloading image: {str(e)}")
        raise InvalidImageError(f"Failed to download image: {str(e)}")


def load_image_from_bytes(image_bytes: bytes) -> Image.Image:
    """
    Load PIL Image from bytes
    
    Args:
        image_bytes: Image bytes
        
    Returns:
        PIL Image
        
    Raises:
        InvalidImageError: If image cannot be loaded
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.verify()  # Verify image integrity
        image = Image.open(io.BytesIO(image_bytes))  # Reopen after verify
        return image
    except Exception as e:
        logger.error(f"Failed to load image from bytes: {str(e)}")
        raise InvalidImageError(f"Invalid or corrupted image: {str(e)}")


def validate_image_resolution(image: Image.Image, max_megapixels: float = 50.0) -> Tuple[int, int]:
    """
    Validate image resolution
    
    Args:
        image: PIL Image
        max_megapixels: Maximum resolution in megapixels
        
    Returns:
        Tuple of (width, height)
        
    Raises:
        InvalidImageError: If resolution exceeds maximum
    """
    width, height = image.size
    megapixels = (width * height) / 1_000_000
    
    if megapixels > max_megapixels:
        raise InvalidImageError(
            f"Image resolution ({megapixels:.2f} MP) exceeds maximum ({max_megapixels} MP)"
        )
    
    return width, height


def resize_image_to_megapixels(image: Image.Image, target_mp: float) -> Image.Image:
    """
    Resize image to target megapixels while maintaining aspect ratio
    
    Args:
        image: PIL Image
        target_mp: Target resolution in megapixels
        
    Returns:
        Resized PIL Image
    """
    width, height = image.size
    current_mp = (width * height) / 1_000_000
    
    # If already smaller than target, return original
    if current_mp <= target_mp:
        return image
    
    # Calculate scale factor
    scale = (target_mp / current_mp) ** 0.5
    
    new_width = int(width * scale)
    new_height = int(height * scale)
    
    return image.resize((new_width, new_height), Image.LANCZOS)

