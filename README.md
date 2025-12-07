# Background Removal Tool 🎨

An AI-powered online background removal tool built with **FastAPI**, **PyTorch**, and the **U²-Net** deep learning model. Features a beautiful, modern UI with drag-and-drop functionality and real-time preview.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-2.1-red.svg)

## ✨ Features

- 🎯 **High-Quality Background Removal** using U²-Net AI model
- 🖼️ **Drag & Drop** image upload
- 👁️ **Live Preview** with before/after comparison
- 🎨 **Background Options** (transparent, white, black, custom colors)
- 📥 **One-Click Download** with PNG transparency
- 📱 **Responsive Design** works on all devices
- ⚡ **Fast Processing** optimized for performance

## 🏗️ Architecture

```
remove-bg/
├── client/              # Frontend
│   ├── index.html      # Main HTML
│   ├── styles.css      # Styling
│   └── script.js       # JavaScript logic
├── service/            # Backend
│   ├── app.py          # FastAPI server
│   ├── u2net.py        # U²-Net model architecture
│   └── models/         # Model weights (create this)
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- 4GB+ RAM recommended
- GPU (optional, but faster)

### Installation

1. **Clone or navigate to the project directory:**
```bash
cd remove-bg
```

2. **Create a virtual environment (recommended):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Download the U²-Net model weights:**

Create a `service/models` directory and download the pre-trained weights:

```bash
mkdir -p service/models
```

Download the model from:
- **U²-Net Full**: [Google Drive Link](https://drive.google.com/uc?id=1ao1ovG1Qtx4b7EoskHXmi2E9rp5CHLcZ)
- Save as: `service/models/u2net.pth`

Or use this command (requires gdown):
```bash
pip install gdown
gdown https://drive.google.com/uc?id=1ao1ovG1Qtx4b7EoskHXmi2E9rp5CHLcZ -O service/models/u2net.pth
```

### Running the Application

1. **Start the backend server:**
```bash
python -m uvicorn service.app:app --reload --host 0.0.0.0 --port 8000
```

Or simply:
```bash
python service/app.py
```

2. **Open the frontend:**

Open `client/index.html` in your web browser, or serve it with a simple HTTP server:

```bash
# Using Python's built-in server
cd client
python -m http.server 3000
```

Then visit: `http://localhost:3000`

3. **Try it out!**
   - Drag and drop an image or click to upload
   - Wait for processing (usually 3-10 seconds)
   - View the result and try different backgrounds
   - Download your image with transparent background

## 🔧 Configuration

### API Endpoint

The frontend is configured to connect to `http://localhost:8000`. If you change the backend port, update the `API_URL` in `client/script.js`:

```javascript
const API_URL = 'http://localhost:8000';
```

### Model Options

You can switch to the lighter U²-Net-P model for faster processing:

In `service/app.py`, change:
```python
model = U2NETP(3, 1)  # Lighter/faster model
```

## 📝 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints

#### `GET /`
Health check endpoint
```json
{
  "message": "Background Removal API is running",
  "model_loaded": true,
  "device": "cpu"
}
```

#### `POST /remove-background`
Remove background from an image
- **Input**: multipart/form-data with image file
- **Output**: PNG image with transparent background

Example with curl:
```bash
curl -X POST "http://localhost:8000/remove-background" \
  -H "accept: image/png" \
  -F "file=@your-image.jpg" \
  --output result.png
```

## 🎨 Customization

### Frontend Styling

Edit `client/styles.css` to customize:
- Colors (CSS variables in `:root`)
- Layout and spacing
- Animations and transitions

### Backend Processing

Edit `service/app.py` to:
- Adjust image preprocessing
- Change model parameters
- Add new endpoints

## 🐛 Troubleshooting

### Backend won't start
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check if port 8000 is already in use
- Verify Python version: `python --version` (should be 3.8+)

### Model not loading
- Ensure model file exists at `service/models/u2net.pth`
- Check file size (should be ~176MB)
- Verify download completed successfully

### Frontend can't connect to backend
- Check that backend is running on port 8000
- Verify CORS is enabled in `service/app.py`
- Check browser console for errors

### Processing is slow
- Use GPU if available (CUDA-enabled PyTorch)
- Switch to U²-Net-P (lighter model)
- Reduce input image size

### Out of memory errors
- Reduce image size before processing
- Use U²-Net-P instead of U²-Net
- Close other applications

## 🚀 Deployment

### Deploy Backend (Options)

1. **Docker** (recommended)
2. **Heroku** with buildpack
3. **AWS EC2** or **Google Cloud**
4. **DigitalOcean App Platform**

### Deploy Frontend

1. **GitHub Pages** (static hosting)
2. **Netlify** or **Vercel**
3. **AWS S3** + CloudFront

**Note**: Update the `API_URL` in `script.js` to your deployed backend URL.

## 📊 Model Information

**U²-Net (U Square Net)**
- Paper: [U²-Net: Going Deeper with Nested U-Structure for Salient Object Detection](https://arxiv.org/abs/2005.09007)
- Architecture: Nested U-structure for accurate segmentation
- Size: ~176MB (full model), ~4.7MB (portable)
- Performance: High-quality results on portraits and objects

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- U²-Net model by [Xuebin Qin et al.](https://github.com/xuebinqin/U-2-Net)
- FastAPI framework
- PyTorch team

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review the API documentation
3. Check browser console and server logs
4. Ensure all dependencies are correctly installed

---

Built with ❤️ using FastAPI, PyTorch, and U²-Net

