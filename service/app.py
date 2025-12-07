from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import torch
import cv2
import numpy as np
from PIL import Image
import io
from pathlib import Path
import logging

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
            model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
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
    return {
        "message": "Background Removal API is running",
        "model_loaded": model is not None,
        "device": str(device)
    }


def normalize_prediction(pred):
    """Normalize prediction to 0-255 range"""
    ma = torch.max(pred)
    mi = torch.min(pred)
    return (pred - mi) / (ma - mi)


def remove_background(image: Image.Image) -> Image.Image:
    """
    Remove background from image using U2NET
    
    Args:
        image: PIL Image
        
    Returns:
        PIL Image with transparent background
    """
    # Store original size
    original_size = image.size
    
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
    
    # Resize mask to original image size
    mask = Image.fromarray((pred_np * 255).astype(np.uint8))
    mask = mask.resize(original_size, Image.LANCZOS)
    
    # Apply mask to original image
    image_np = np.array(image)
    mask_np = np.array(mask)
    
    # Create RGBA image
    rgba = np.dstack((image_np, mask_np))
    result_image = Image.fromarray(rgba, 'RGBA')
    
    return result_image


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
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        logger.info(f"Processing image: {file.filename}, size: {image.size}, mode: {image.mode}")
        
        # Remove background
        result = remove_background(image)
        
        # Convert to bytes
        output_buffer = io.BytesIO()
        result.save(output_buffer, format='PNG')
        output_buffer.seek(0)
        
        logger.info(f"Successfully processed {file.filename}")
        
        return StreamingResponse(
            output_buffer,
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename=removed_bg_{file.filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


@app.post("/remove-background-preview")
async def remove_bg_preview(file: UploadFile = File(...)):
    """
    Remove background and return for preview (same as remove-background but different endpoint)
    """
    return await remove_bg_endpoint(file)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

