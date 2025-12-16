from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
import torch
import cv2
import numpy as np
from PIL import Image
import io
from pathlib import Path
import logging
import traceback

# Import U2NET model
from service.u2net import U2NET, U2NETP
from torchvision import transforms

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Background Removal API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle any unhandled exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    logger.error(f"Request URL: {request.url}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred. Please try again later.",
            "error_type": type(exc).__name__
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.error(f"Validation error: {str(exc)}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Invalid request. Please check your input.",
            "errors": exc.errors()
        }
    )

# Global variables for model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = None
MODEL_PATH = Path("service/models/u2net.pth")

# Image preprocessing transform
transform = transforms.Compose([
    transforms.Resize((320, 320)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])


def load_model():
    """Load U2NET model"""
    global model
    try:
        logger.info("Loading U2NET model...")
        model = U2NET(3, 1)
        
        if MODEL_PATH.exists():
            logger.info(f"Loading weights from {MODEL_PATH}")
            model.load_state_dict(torch.load(MODEL_PATH, map_location=device, weights_only=False))
        else:
            logger.warning(f"Model weights not found at {MODEL_PATH}. Using untrained model.")
            logger.warning("Download model from: https://drive.google.com/uc?id=1ao1ovG1Qtx4b7EoskHXmi2E9rp5CHLcZ")
        
        model.to(device)
        model.eval()
        logger.info("Model loaded successfully!")
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise


@app.on_event("startup")
async def startup_event():
    """Initialize model on startup"""
    load_model()


@app.get("/")
async def root():
    """Health check endpoint"""
    try:
        return {
            "message": "Background Removal API is running",
            "model_loaded": model is not None,
            "device": str(device),
            "status": "ready" if model is not None else "loading"
        }
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return {
            "message": "Background Removal API is running",
            "model_loaded": False,
            "device": "unknown",
            "status": "error",
            "error": str(e)
        }


def normalize_prediction(pred):
    """Normalize prediction to 0-255 range"""
    ma = torch.max(pred)
    mi = torch.min(pred)
    # Handle division by zero case
    if ma == mi:
        return torch.zeros_like(pred)
    return (pred - mi) / (ma - mi)


def remove_background(image: Image.Image) -> Image.Image:
    """
    Remove background from image using U2NET
    
    Args:
        image: PIL Image
        
    Returns:
        PIL Image with transparent background
        
    Raises:
        ValueError: If model is not loaded or image is invalid
    """
    # Check if model is loaded
    if model is None:
        raise ValueError("Model is not loaded. Please wait for the model to initialize.")
    
    # Validate image
    if image is None:
        raise ValueError("Invalid image provided")
    
    try:
        # Store original size
        original_size = image.size
        
        # Validate image size
        if original_size[0] == 0 or original_size[1] == 0:
            raise ValueError("Image has invalid dimensions")
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Preprocess image
        input_tensor = transform(image).unsqueeze(0).to(device)
        
        # Run inference
        with torch.no_grad():
            d1, d2, d3, d4, d5, d6, d7 = model(input_tensor)
            pred = d1[:, 0, :, :]
            pred = normalize_prediction(pred)
        
        # Convert prediction to numpy
        pred_np = pred.squeeze().cpu().numpy()
        
        # Validate prediction output
        if pred_np.size == 0:
            raise ValueError("Model prediction failed - empty output")
        
        # Resize mask to original image size
        mask = Image.fromarray((pred_np * 255).astype(np.uint8))
        mask = mask.resize(original_size, Image.LANCZOS)
        
        # Apply mask to original image
        image_np = np.array(image)
        mask_np = np.array(mask)
        
        # Validate arrays
        if image_np.size == 0 or mask_np.size == 0:
            raise ValueError("Failed to process image arrays")
        
        # Create RGBA image
        rgba = np.dstack((image_np, mask_np))
        result_image = Image.fromarray(rgba, 'RGBA')
        
        # Validate result
        if result_image is None or result_image.size[0] == 0:
            raise ValueError("Failed to create result image")
        
        return result_image
        
    except Exception as e:
        logger.error(f"Error in remove_background: {str(e)}")
        raise


@app.post("/remove-background")
async def remove_bg_endpoint(file: UploadFile = File(...)):
    """
    Remove background from uploaded image
    
    Args:
        file: Uploaded image file
        
    Returns:
        Image with transparent background
    """
    try:
        # Check if model is loaded
        if model is None:
            logger.error("Model is not loaded")
            raise HTTPException(
                status_code=503, 
                detail="Service temporarily unavailable. Model is still loading. Please try again in a moment."
            )
        
        # Validate file exists
        if file is None:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image. Supported formats: JPG, PNG, WebP")
        
        # Validate filename
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")
        
        # Read image with size limit
        contents = await file.read()
        
        # Validate file size (10MB limit)
        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
        
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Validate and open image
        try:
            image = Image.open(io.BytesIO(contents))
            # Verify image can be loaded
            image.verify()
            # Reopen after verify (verify closes the image)
            image = Image.open(io.BytesIO(contents))
        except Exception as img_error:
            logger.error(f"Invalid image file: {str(img_error)}")
            raise HTTPException(status_code=400, detail=f"Invalid or corrupted image file: {str(img_error)}")
        
        logger.info(f"Processing image: {file.filename}, size: {image.size}, mode: {image.mode}")
        
        # Remove background
        result = remove_background(image)
        
        # Validate result
        if result is None:
            raise HTTPException(status_code=500, detail="Failed to process image - no result returned")
        
        # Convert to bytes
        try:
            output_buffer = io.BytesIO()
            result.save(output_buffer, format='PNG')
            output_buffer.seek(0)
            
            # Validate output buffer
            if output_buffer.getvalue() is None or len(output_buffer.getvalue()) == 0:
                raise HTTPException(status_code=500, detail="Failed to generate output image")
            
        except Exception as save_error:
            logger.error(f"Error saving result image: {str(save_error)}")
            raise HTTPException(status_code=500, detail=f"Failed to save processed image: {str(save_error)}")
        
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
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing image: {str(e)}. Please try again or contact support if the issue persists."
        )


@app.post("/remove-background-preview")
async def remove_bg_preview(file: UploadFile = File(...)):
    """
    Remove background and return for preview (same as remove-background but different endpoint)
    """
    try:
        # Reuse the same endpoint logic
        return await remove_bg_endpoint(file)
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error in preview endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing preview: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

