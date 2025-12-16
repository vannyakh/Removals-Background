"""
API Routes
FastAPI route handlers
"""
import io
import base64
from typing import Optional
from fastapi import APIRouter, File, UploadFile, HTTPException, Request, Form, Depends, Body
from fastapi.responses import StreamingResponse, JSONResponse
from PIL import Image
import logging

from app.config import settings
from app.services.background_removal import background_removal_service
from app.core.model_manager import model_manager
from app.api.dependencies import verify_authentication
from app.api.schemas import (
    RemoveBgRequest,
    RemoveBgResponse,
    RemoveBgData,
    RemoveBgErrorResponse,
    RemoveBgError
)
from app.utils.exceptions import (
    ModelNotLoadedError,
    ImageProcessingError,
    InvalidImageError,
    create_http_exception
)
from app.utils.logger import setup_logger
from app.utils.image_loader import (
    decode_base64_image,
    download_image_from_url,
    load_image_from_bytes,
    validate_image_resolution,
    resize_image_to_megapixels
)
from app.utils.foreground_detection import calculate_foreground_bbox

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


@router.post("/removebg", response_model=RemoveBgResponse)
async def removebg(
    request: Request,
    auth: bool = Depends(verify_authentication)
):
    """
    Remove the background of an image
    
    Removes the background of a JPG/PNG/WebP image.
    
    - **File size**: up to 22 MB
    - **Input resolution**: up to 50 megapixels
    - **Image source**: File upload (binary or as base64 encoded string) or download from URL
    - **Image Content**: Any photo with a foreground (e.g. people, products, animals, cars, etc.)
    - **Output resolutions**: Preview (up to 0.25 megapixels), Full (up to 25 megapixels), 50MP (up to 50 megapixels)
    - **Authentication**: Requires either an API Key in X-API-Key header or OAuth 2.0 access token in Authorization header (if enabled)
    
    Returns:
        JSON response with base64 encoded result image and foreground bounding box
    """
    try:
        # Check if model is loaded
        if not model_manager.is_loaded():
            return JSONResponse(
                status_code=503,
                content={
                    "errors": [{
                        "code": "service_unavailable",
                        "title": "Service temporarily unavailable. Model is still loading. Please try again in a moment."
                    }]
                }
            )
        
        # Handle both JSON body and multipart form data
        image_file = None
        image_file_b64 = None
        image_url = None
        size = "preview"
        
        content_type = request.headers.get("content-type", "")
        
        if content_type.startswith("application/json"):
            # JSON body
            try:
                json_body = await request.json()
                body = RemoveBgRequest(**json_body)
                image_file_b64 = body.image_file_b64
                image_url = body.image_url
                size = body.size or "preview"
            except Exception as e:
                return JSONResponse(
                    status_code=400,
                    content={
                        "errors": [{
                            "code": "invalid_json",
                            "title": f"Invalid JSON body: {str(e)}"
                        }]
                    }
                )
        elif content_type.startswith("multipart/form-data"):
            # Multipart form data
            form = await request.form()
            image_file = form.get("image_file")
            if image_file and hasattr(image_file, 'file'):
                # It's an UploadFile
                pass
            else:
                image_file = None
            
            image_file_b64 = form.get("image_file_b64")
            image_url = form.get("image_url")
            size = form.get("size", "preview")
        else:
            # Try to parse as JSON anyway
            try:
                json_body = await request.json()
                body = RemoveBgRequest(**json_body)
                image_file_b64 = body.image_file_b64
                image_url = body.image_url
                size = body.size or "preview"
            except:
                return JSONResponse(
                    status_code=400,
                    content={
                        "errors": [{
                            "code": "invalid_content_type",
                            "title": "Content-Type must be application/json or multipart/form-data"
                        }]
                    }
                )
        
        # Validate that exactly one image source is provided
        sources = [image_file, image_file_b64, image_url]
        provided_sources = [s for s in sources if s is not None and (isinstance(s, str) and s != "" or not isinstance(s, str))]
        
        if len(provided_sources) == 0:
            return JSONResponse(
                status_code=400,
                content={
                    "errors": [{
                        "code": "no_source",
                        "title": "No image source provided. Please provide either the image_url, image_file or image_file_b64 parameter."
                    }]
                }
            )
        
        if len(provided_sources) > 1:
            return JSONResponse(
                status_code=400,
                content={
                    "errors": [{
                        "code": "multiple_sources",
                        "title": "Multiple image sources given: Please provide either the image_url, image_file or image_file_b64 parameter."
                    }]
                }
            )
        
        # Validate size parameter
        size = (size or "preview").lower()
        if size not in ["preview", "full", "50mp"]:
            return JSONResponse(
                status_code=400,
                content={
                    "errors": [{
                        "code": "invalid_size",
                        "title": f"Invalid size parameter: {size}. Must be 'preview', 'full', or '50mp'"
                    }]
                }
            )
        
        # Load image from appropriate source
        image_bytes = None
        image_filename = "image"
        
        if image_file:
            # File upload
            if not image_file.content_type or not image_file.content_type.startswith('image/'):
                return JSONResponse(
                    status_code=400,
                    content={
                        "errors": [{
                            "code": "invalid_file_type",
                            "title": "File must be an image. Supported formats: JPG, PNG, WebP"
                        }]
                    }
                )
            
            image_bytes = await image_file.read()
            image_filename = image_file.filename or "image"
            
        elif image_file_b64 and image_file_b64 != "":
            # Base64 encoded
            try:
                image_bytes = decode_base64_image(image_file_b64)
                image_filename = "image_b64"
            except InvalidImageError as e:
                return JSONResponse(
                    status_code=400,
                    content={
                        "errors": [{
                            "code": "invalid_image",
                            "title": str(e)
                        }]
                    }
                )
                
        elif image_url and image_url != "":
            # URL download
            try:
                image_bytes = await download_image_from_url(
                    image_url,
                    max_size=settings.MAX_IMAGE_SIZE_REMOVEBG
                )
                image_filename = "image_url"
            except InvalidImageError as e:
                return JSONResponse(
                    status_code=400,
                    content={
                        "errors": [{
                            "code": "invalid_image",
                            "title": str(e)
                        }]
                    }
                )
        
        # Validate file size
        if len(image_bytes) > settings.MAX_IMAGE_SIZE_REMOVEBG:
            return JSONResponse(
                status_code=400,
                content={
                    "errors": [{
                        "code": "file_too_large",
                        "title": f"File size ({len(image_bytes) / (1024*1024):.1f} MB) exceeds maximum ({settings.MAX_IMAGE_SIZE_REMOVEBG / (1024*1024):.0f} MB)"
                    }]
                }
            )
        
        if len(image_bytes) == 0:
            return JSONResponse(
                status_code=400,
                content={
                    "errors": [{
                        "code": "empty_file",
                        "title": "Image file is empty"
                    }]
                }
            )
        
        # Load and validate image
        try:
            image = load_image_from_bytes(image_bytes)
        except InvalidImageError as e:
            return JSONResponse(
                status_code=400,
                content={
                    "errors": [{
                        "code": "invalid_image",
                        "title": str(e)
                    }]
                }
            )
        
        # Validate input resolution
        try:
            width, height = validate_image_resolution(image, settings.MAX_INPUT_MEGAPIXELS)
        except InvalidImageError as e:
            return JSONResponse(
                status_code=400,
                content={
                    "errors": [{
                        "code": "invalid_resolution",
                        "title": str(e)
                    }]
                }
            )
        
        logger.info(f"Processing image: {image_filename}, size: {image.size}, mode: {image.mode}")
        
        # Remove background
        try:
            result = background_removal_service.remove_background(image)
        except ModelNotLoadedError:
            return JSONResponse(
                status_code=503,
                content={
                    "errors": [{
                        "code": "model_not_loaded",
                        "title": "Model is not loaded. Please wait for the model to initialize."
                    }]
                }
            )
        except ImageProcessingError as e:
            logger.error(f"Image processing error: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "errors": [{
                        "code": "processing_error",
                        "title": str(e)
                    }]
                }
            )
        
        # Validate result
        if result is None:
            return JSONResponse(
                status_code=500,
                content={
                    "errors": [{
                        "code": "processing_error",
                        "title": "Failed to process image - no result returned"
                    }]
                }
            )
        
        # Resize output based on size parameter
        if size == "preview":
            result = resize_image_to_megapixels(result, settings.OUTPUT_PREVIEW_MP)
        elif size == "full":
            result = resize_image_to_megapixels(result, settings.OUTPUT_FULL_MP)
        elif size == "50mp":
            result = resize_image_to_megapixels(result, settings.OUTPUT_50MP_MP)
        
        # Calculate foreground bounding box
        left, top, fg_width, fg_height = calculate_foreground_bbox(result)
        
        # Convert to base64
        try:
            output_buffer = io.BytesIO()
            result.save(output_buffer, format='PNG')
            output_buffer.seek(0)
            
            if len(output_buffer.getvalue()) == 0:
                return JSONResponse(
                    status_code=500,
                    content={
                        "errors": [{
                            "code": "processing_error",
                            "title": "Failed to generate output image"
                        }]
                    }
                )
            
            # Encode to base64
            result_b64 = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
            
        except Exception as save_error:
            logger.error(f"Error saving result image: {str(save_error)}")
            return JSONResponse(
                status_code=500,
                content={
                    "errors": [{
                        "code": "processing_error",
                        "title": f"Failed to save processed image: {str(save_error)}"
                    }]
                }
            )
        
        logger.info(f"Successfully processed {image_filename} with size={size}")
        
        # Return JSON response
        return RemoveBgResponse(
            data=RemoveBgData(
                result_b64=result_b64,
                foreground_top=top,
                foreground_left=left,
                foreground_width=fg_width,
                foreground_height=fg_height
            )
        )
        
    except Exception as e:
        logger.error(f"Unexpected error processing image: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "errors": [{
                    "code": "internal_error",
                    "title": f"Error processing image: {str(e)}. Please try again or contact support if the issue persists."
                }]
            }
        )

