"""
Script to download the U2NET pre-trained model
"""
import os
import urllib.request
from pathlib import Path

def download_model():
    """Download U2NET model weights from Google Drive"""
    
    # Create models directory
    models_dir = Path("service/models")
    models_dir.mkdir(exist_ok=True, parents=True)
    
    model_path = models_dir / "u2net.pth"
    
    # Check if already exists
    if model_path.exists():
        print(f"✓ Model already exists at {model_path}")
        file_size = model_path.stat().st_size / (1024 * 1024)
        print(f"  File size: {file_size:.1f} MB")
        return
    
    print("Downloading U2NET model weights...")
    print("This may take a few minutes (file size: ~176 MB)")
    
    # Google Drive direct download link
    url = "https://drive.google.com/uc?export=download&id=1ao1ovG1Qtx4b7EoskHXmi2E9rp5CHLcZ"
    
    try:
        # Download with progress
        def report_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(downloaded * 100 / total_size, 100)
            print(f"\rProgress: {percent:.1f}%", end="")
        
        urllib.request.urlretrieve(url, model_path, report_progress)
        print("\n✓ Model downloaded successfully!")
        
        # Verify file size
        file_size = model_path.stat().st_size / (1024 * 1024)
        print(f"  Saved to: {model_path}")
        print(f"  File size: {file_size:.1f} MB")
        
        if file_size < 100:
            print("⚠ Warning: File size seems too small. Download may have failed.")
            print("  Please download manually from:")
            print("  https://drive.google.com/uc?id=1ao1ovG1Qtx4b7EoskHXmi2E9rp5CHLcZ")
        
    except Exception as e:
        print(f"\n✗ Download failed: {e}")
        print("\nPlease download the model manually:")
        print("1. Visit: https://drive.google.com/uc?id=1ao1ovG1Qtx4b7EoskHXmi2E9rp5CHLcZ")
        print(f"2. Save the file as: {model_path}")
        print("\nOr install gdown and run:")
        print("  pip install gdown")
        print("  gdown https://drive.google.com/uc?id=1ao1ovG1Qtx4b7EoskHXmi2E9rp5CHLcZ -O service/models/u2net.pth")

if __name__ == "__main__":
    download_model()

