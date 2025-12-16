"""
API Routes
FastAPI route handlers
"""
import io
from fastapi import APIRouter, File, UploadFile, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from PIL import Image
import logging

from app.config import settings
from app.services.background_removal import background_removal_service
from app.core.model_manager import model_manager
from app.utils.exceptions import (
    ModelNotLoadedError,
    ImageProcessingError,
    InvalidImageError,
    create_http_exception
)
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


@router.get("/")
async def root():
    """Health check endpoint"""
    try:
        model_info = model_manager.get_model_info()
        return {
            "message": "Background Removal API is running",
            "version": settings.APP_VERSION,
            "model_loaded": model_info["loaded"],
            "model_type": model_info["model_type"],
            "device": model_info["device"],
            "status": "ready" if model_info["loaded"] else "loading"
        }
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return {
            "message": "Background Removal API is running",
            "version": settings.APP_VERSION,
            "model_loaded": False,
            "device": "unknown",
            "status": "error",
            "error": str(e)
        }


@router.get("/health")
async def health():
    """Detailed health check"""
    try:
        model_info = model_manager.get_model_info()
        return {
            "status": "healthy" if model_info["loaded"] else "degraded",
            "model": model_info,
            "config": {
                "max_image_size": settings.MAX_IMAGE_SIZE,
                "input_size": settings.INPUT_SIZE,
                "multi_scale": settings.USE_MULTI_SCALE,
                "mask_smoothing": settings.MASK_SMOOTHING,
                "edge_refinement": settings.EDGE_REFINEMENT,
            }
        }
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )


@router.post("/remove-background")
async def remove_background(
    request: Request,
    file: UploadFile = File(...)
):
    """
    Remove background from uploaded image
    
    Args:
        file: Uploaded image file
        
    Returns:
        Image with transparent background (PNG)
    """
    try:
        # Check if model is loaded
        if not model_manager.is_loaded():
            raise create_http_exception(
                503,
                "Service temporarily unavailable. Model is still loading. Please try again in a moment.",
                "ModelNotLoaded"
            )
        
        # Validate file
        if file is None:
            raise create_http_exception(400, "No file provided", "InvalidRequest")
        
        if not file.content_type or not file.content_type.startswith('image/'):
            raise create_http_exception(
                400,
                "File must be an image. Supported formats: JPG, PNG, WebP",
                "InvalidFileType"
            )
        
        if not file.filename:
            raise create_http_exception(400, "Filename is required", "InvalidRequest")
        
        # Read and validate file
        contents = await file.read()
        
        if len(contents) > settings.MAX_IMAGE_SIZE:
            raise create_http_exception(
                400,
                f"File size exceeds {settings.MAX_IMAGE_SIZE / (1024*1024):.0f}MB limit",
                "FileTooLarge"
            )
        
        if len(contents) == 0:
            raise create_http_exception(400, "File is empty", "InvalidFile")
        
        # Validate and open image
        try:
            image = Image.open(io.BytesIO(contents))
            image.verify()  # Verify image integrity
            image = Image.open(io.BytesIO(contents))  # Reopen after verify
        except Exception as img_error:
            logger.error(f"Invalid image file: {str(img_error)}")
            raise create_http_exception(
                400,
                f"Invalid or corrupted image file: {str(img_error)}",
                "InvalidImage"
            )
        
        logger.info(f"Processing image: {file.filename}, size: {image.size}, mode: {image.mode}")
        
        # Remove background
        try:
            result = background_removal_service.remove_background(image)
        except ModelNotLoadedError:
            raise create_http_exception(
                503,
                "Model is not loaded. Please wait for the model to initialize.",
                "ModelNotLoaded"
            )
        except ImageProcessingError as e:
            logger.error(f"Image processing error: {str(e)}")
            raise create_http_exception(500, str(e), "ProcessingError")
        
        # Validate result
        if result is None:
            raise create_http_exception(
                500,
                "Failed to process image - no result returned",
                "ProcessingError"
            )
        
        # Convert to bytes
        try:
            output_buffer = io.BytesIO()
            result.save(output_buffer, format='PNG')
            output_buffer.seek(0)
            
            if len(output_buffer.getvalue()) == 0:
                raise create_http_exception(
                    500,
                    "Failed to generate output image",
                    "ProcessingError"
                )
            
        except Exception as save_error:
            logger.error(f"Error saving result image: {str(save_error)}")
            raise create_http_exception(
                500,
                f"Failed to save processed image: {str(save_error)}",
                "ProcessingError"
            )
        
        logger.info(f"Successfully processed {file.filename}")
        
        return StreamingResponse(
            output_buffer,
            media_type="image/png",
            headers={
                "Content-Disposition": f"attachment; filename=removed_bg_{file.filename}",
                "Content-Length": str(len(output_buffer.getvalue()))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing image: {str(e)}", exc_info=True)
        raise create_http_exception(
            500,
            f"Error processing image: {str(e)}. Please try again or contact support if the issue persists.",
            "InternalError"
        )


@router.post("/remove-background-preview")
async def remove_background_preview(request: Request, file: UploadFile = File(...)):
    """
    Remove background and return for preview (same as remove-background)
    """
    return await remove_background(request, file)

