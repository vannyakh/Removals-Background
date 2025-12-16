"""
Model Manager
Handles model loading, caching, and device management
"""
import torch
from pathlib import Path
from typing import Optional
import logging

from app.config import settings
from app.models.u2net import U2NET, U2NETP
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ModelManager:
    """Manages AI model lifecycle"""
    
    def __init__(self):
        self.model: Optional[torch.nn.Module] = None
        self.device: torch.device = self._get_device()
        self.model_type: str = settings.MODEL_TYPE
        logger.info(f"Initialized ModelManager with device: {self.device}")
    
    def _get_device(self) -> torch.device:
        """
        Determine the best available device
        
        Returns:
            torch.device instance
        """
        if settings.DEVICE == "cpu":
            return torch.device("cpu")
        elif settings.DEVICE == "cuda":
            if torch.cuda.is_available():
                return torch.device("cuda")
            else:
                logger.warning("CUDA requested but not available, falling back to CPU")
                return torch.device("cpu")
        else:  # auto
            if torch.cuda.is_available():
                device = torch.device("cuda")
                logger.info(f"Using CUDA device: {torch.cuda.get_device_name(0)}")
                return device
            else:
                logger.info("CUDA not available, using CPU")
                return torch.device("cpu")
    
    def load_model(self, model_type: Optional[str] = None) -> None:
        """
        Load the specified model
        
        Args:
            model_type: Model type ("u2net" or "u2netp"), uses config default if None
        """
        model_type = model_type or settings.MODEL_TYPE
        
        try:
            logger.info(f"Loading {model_type} model...")
            
            # Initialize model architecture
            if model_type.lower() == "u2netp":
                self.model = U2NETP(3, 1)
                model_path = Path(settings.MODEL_P_PATH)
            else:
                self.model = U2NET(3, 1)
                model_path = Path(settings.MODEL_PATH)
            
            # Load weights if available
            if model_path.exists():
                logger.info(f"Loading weights from {model_path}")
                try:
                    state_dict = torch.load(
                        model_path,
                        map_location=self.device,
                        weights_only=False
                    )
                    self.model.load_state_dict(state_dict)
                    logger.info("Model weights loaded successfully")
                except Exception as e:
                    logger.warning(f"Failed to load weights: {e}. Using untrained model.")
            else:
                logger.warning(f"Model weights not found at {model_path}")
                logger.warning("Model will run without pre-trained weights")
            
            # Move to device and set to eval mode
            self.model.to(self.device)
            self.model.eval()
            
            # Optimize for inference
            if hasattr(torch, 'compile') and self.device.type == "cuda":
                try:
                    self.model = torch.compile(self.model, mode="reduce-overhead")
                    logger.info("Model compiled with torch.compile for faster inference")
                except Exception as e:
                    logger.warning(f"Failed to compile model: {e}")
            
            self.model_type = model_type
            logger.info(f"Model loaded successfully on {self.device}")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}", exc_info=True)
            raise
    
    def get_model(self) -> torch.nn.Module:
        """
        Get the loaded model
        
        Returns:
            Loaded model instance
            
        Raises:
            ModelNotLoadedError: If model is not loaded
        """
        if self.model is None:
            raise ModelNotLoadedError("Model is not loaded. Please load the model first.")
        return self.model
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.model is not None
    
    def get_device(self) -> torch.device:
        """Get current device"""
        return self.device
    
    def get_model_info(self) -> dict:
        """
        Get model information
        
        Returns:
            Dictionary with model information
        """
        return {
            "model_type": self.model_type,
            "device": str(self.device),
            "loaded": self.is_loaded(),
            "cuda_available": torch.cuda.is_available(),
            "cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        }


# Global model manager instance
model_manager = ModelManager()

