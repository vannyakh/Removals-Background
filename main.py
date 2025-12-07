"""
Main entry point for the Background Removal Tool
Run this file to start the FastAPI backend server
"""

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("🎨 Background Removal Tool - Starting Server")
    print("=" * 60)
    print("\n📦 Loading U²-Net model...")
    print("⚠️  Make sure you have downloaded the model weights!")
    print("   Run: python service/download_model.py")
    print("=" * 60)
    print("\n🚀 Server will start at: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🌐 Open client/index.html in your browser to use the UI")
    print("\n⏸️  Press CTRL+C to stop the server")
    print("=" * 60 + "\n")
    
    uvicorn.run(
        "service.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

