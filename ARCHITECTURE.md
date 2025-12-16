# Architecture Documentation

## Overview

This project has been refactored with a modern, modular architecture that separates concerns and improves maintainability, testability, and scalability.

## Project Structure

```
removals-background/
├── app/                          # Main application package
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI application entry point
│   ├── config.py                # Configuration management
│   ├── api/                     # API layer
│   │   ├── __init__.py
│   │   └── routes.py           # API route handlers
│   ├── core/                    # Core business logic
│   │   ├── __init__.py
│   │   └── model_manager.py    # AI model lifecycle management
│   ├── services/                # Business services
│   │   ├── __init__.py
│   │   ├── background_removal.py  # Main background removal service
│   │   └── image_utils.py       # Image processing utilities
│   ├── models/                  # AI model architectures
│   │   ├── __init__.py
│   │   └── u2net.py            # U²-Net model definition
│   └── utils/                   # Utility modules
│       ├── __init__.py
│       ├── logger.py            # Logging configuration
│       ├── exceptions.py        # Custom exceptions
│       └── download_model.py    # Model download utility
├── client/                      # Frontend (unchanged)
│   ├── index.html
│   ├── script.js
│   └── styles.css
├── models/                      # Model weights directory
│   └── u2net.pth               # Pre-trained model weights
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── start.bat                    # Windows startup script
├── start.sh                     # Linux/Mac startup script
└── README.md                    # Project documentation
```

## Architecture Layers

### 1. API Layer (`app/api/`)
- **Purpose**: Handle HTTP requests and responses
- **Responsibilities**:
  - Request validation
  - Response formatting
  - Error handling
  - Route definitions

**Key Files:**
- `routes.py`: Contains all API endpoints

### 2. Service Layer (`app/services/`)
- **Purpose**: Business logic and domain services
- **Responsibilities**:
  - Image processing orchestration
  - Background removal logic
  - Image utilities

**Key Files:**
- `background_removal.py`: Main service for removing backgrounds
- `image_utils.py`: Helper functions for image manipulation

### 3. Core Layer (`app/core/`)
- **Purpose**: Core infrastructure and model management
- **Responsibilities**:
  - Model loading and lifecycle
  - Device management (CPU/GPU)
  - Model optimization

**Key Files:**
- `model_manager.py`: Manages AI model loading and inference

### 4. Models Layer (`app/models/`)
- **Purpose**: AI model architectures
- **Responsibilities**:
  - Model definitions
  - Neural network architectures

**Key Files:**
- `u2net.py`: U²-Net model implementation

### 5. Utils Layer (`app/utils/`)
- **Purpose**: Shared utilities
- **Responsibilities**:
  - Logging configuration
  - Custom exceptions
  - Helper functions

## Key Improvements

### 1. Configuration Management
- Centralized configuration using `pydantic-settings`
- Environment variable support
- Type-safe configuration
- Easy to override for different environments

### 2. Enhanced Model Processing
- **Multi-scale inference**: Processes image at multiple scales and averages results for better quality
- **Mask smoothing**: Applies Gaussian smoothing for cleaner edges
- **Edge refinement**: Uses image gradients to refine mask boundaries
- **Adaptive resizing**: Maintains aspect ratio while optimizing for model input

### 3. Better Error Handling
- Custom exception hierarchy
- Proper HTTP status codes
- Detailed error messages
- Comprehensive logging

### 4. Improved Model Management
- Automatic device detection (CPU/GPU)
- Model compilation for faster inference (PyTorch 2.0+)
- Better error handling for model loading
- Model information endpoints

### 5. Code Organization
- Separation of concerns
- Single Responsibility Principle
- Dependency injection ready
- Easy to test and extend

## Configuration

Configuration is managed through `app/config.py` using environment variables. See `.env.example` for all available options.

### Key Configuration Options

- `MODEL_TYPE`: Choose between "u2net" (full) or "u2netp" (portable)
- `DEVICE`: "auto" (detect), "cpu", or "cuda"
- `USE_MULTI_SCALE`: Enable multi-scale inference for better quality
- `MASK_SMOOTHING`: Apply Gaussian smoothing to masks
- `EDGE_REFINEMENT`: Use edge detection to refine mask boundaries

## API Endpoints

### `GET /`
Health check endpoint

### `GET /health`
Detailed health check with model information

### `POST /remove-background`
Remove background from uploaded image
- **Input**: multipart/form-data with image file
- **Output**: PNG image with transparent background

### `POST /remove-background-preview`
Same as `/remove-background` (for preview purposes)

## Model Improvements

### Preprocessing
- Adaptive image resizing maintaining aspect ratio
- Proper normalization for model input
- Support for large images (with size limits)

### Inference
- Multi-scale inference (3 scales: 0.75x, 1.0x, 1.25x)
- Averaged predictions for better quality
- Optimized tensor operations

### Post-processing
- Mask quality enhancement (morphological operations)
- Gaussian smoothing for cleaner edges
- Edge refinement using image gradients
- High-quality upsampling (LANCZOS4)

## Performance Optimizations

1. **Model Compilation**: Uses `torch.compile` when available (PyTorch 2.0+)
2. **GPU Support**: Automatic CUDA detection and usage
3. **Efficient Resizing**: Maintains aspect ratio to reduce artifacts
4. **Optimized Inference**: Multi-scale inference can be disabled for speed

## Extending the Architecture

### Adding a New Model
1. Add model architecture to `app/models/`
2. Update `model_manager.py` to support the new model
3. Update configuration in `app/config.py`

### Adding New Endpoints
1. Add route handlers to `app/api/routes.py`
2. Create service methods in `app/services/` if needed
3. Update API documentation

### Adding New Image Processing Features
1. Add utilities to `app/services/image_utils.py`
2. Integrate into `background_removal.py` service
3. Add configuration options if needed

## Testing

The modular architecture makes testing easier:
- Unit tests for services
- Integration tests for API endpoints
- Mock model for faster testing

## Deployment

The architecture supports:
- Docker containerization
- Environment-based configuration
- Horizontal scaling (stateless design)
- Health check endpoints for load balancers

## Migration from Old Structure

The old `service/` directory structure is maintained for backward compatibility, but new code uses the `app/` structure. The model weights location has changed from `service/models/` to `models/` at the root level.

