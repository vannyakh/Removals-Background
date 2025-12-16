"""
Custom Exceptions
"""
from fastapi import HTTPException, status


class BackgroundRemovalError(Exception):
    """Base exception for background removal errors"""
    pass


class ModelNotLoadedError(BackgroundRemovalError):
    """Raised when model is not loaded"""
    pass


class ImageProcessingError(BackgroundRemovalError):
    """Raised when image processing fails"""
    pass


class InvalidImageError(BackgroundRemovalError):
    """Raised when image is invalid"""
    pass


def create_http_exception(
    status_code: int,
    detail: str,
    error_type: str = None
) -> HTTPException:
    """
    Create HTTP exception with error type
    
    Args:
        status_code: HTTP status code
        detail: Error message
        error_type: Error type identifier
        
    Returns:
        HTTPException instance
    """
    content = {"detail": detail}
    if error_type:
        content["error_type"] = error_type
    
    return HTTPException(status_code=status_code, detail=detail)

