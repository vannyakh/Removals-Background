"""
Main entry point for the Background Removal Tool
Run this file to start the FastAPI backend server
"""

if __name__ == "__main__":
    import uvicorn
    from app.config import settings
    
    print("=" * 60)
    print("🎨 Background Removal Tool - Starting Server")
    print("=" * 60)
    print("\n📦 Loading U²-Net model...")
    print("⚠️  Make sure you have downloaded the model weights!")
    print("   Run: python app/utils/download_model.py")
    print("=" * 60)
    print(f"\n🚀 Server will start at: http://{settings.HOST}:{settings.PORT}")
    print(f"📚 API Docs: http://{settings.HOST}:{settings.PORT}/docs")
    print("🌐 Open client/index.html in your browser to use the UI")
    print("\n⏸️  Press CTRL+C to stop the server")
    print("=" * 60 + "\n")
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )

