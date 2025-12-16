"""
Script to download the U2NET pre-trained model
"""
import os
import urllib.request
import re
from pathlib import Path

def download_model():
    """Download U2NET model weights from Google Drive"""
    
    # Create models directory
    models_dir = Path("service/models")
    models_dir.mkdir(exist_ok=True, parents=True)
    
    model_path = models_dir / "u2net.pth"
    
    # Check if already exists and is valid
    if model_path.exists():
        file_size = model_path.stat().st_size / (1024 * 1024)
        # Check if file is valid (not HTML)
        with open(model_path, 'rb') as f:
            first_bytes = f.read(100)
            if first_bytes.startswith(b'<!DOCTYPE') or first_bytes.startswith(b'<html'):
                print(f"⚠ Invalid model file detected (HTML). Removing and re-downloading...")
                model_path.unlink()
            else:
                print(f"✓ Model already exists at {model_path}")
                print(f"  File size: {file_size:.1f} MB")
                return
    
    print("Downloading U2NET model weights...")
    print("This may take a few minutes (file size: ~176 MB)")
    
    # Google Drive file ID
    file_id = "1ao1ovG1Qtx4b7EoskHXmi2E9rp5CHLcZ"
    
    try:
        # First attempt: try direct download with confirm parameter
        url = f"https://drive.google.com/uc?export=download&id={file_id}&confirm=t"
        
        # Download with progress
        def report_progress(block_num, block_size, total_size):
            if total_size > 0:
                downloaded = block_num * block_size
                percent = min(downloaded * 100 / total_size, 100)
                print(f"\rProgress: {percent:.1f}%", end="")
        
        urllib.request.urlretrieve(url, model_path, report_progress)
        print("\n✓ Download completed!")
        
        # Verify file is not HTML
        with open(model_path, 'rb') as f:
            first_bytes = f.read(100)
            if first_bytes.startswith(b'<!DOCTYPE') or first_bytes.startswith(b'<html'):
                print("⚠ Downloaded file is HTML (Google Drive warning page).")
                print("  Trying alternative download method...")
                model_path.unlink()
                
                # Try using gdown if available
                try:
                    import gdown
                    print("Using gdown library...")
                    url = f"https://drive.google.com/uc?id={file_id}"
                    gdown.download(url, str(model_path), quiet=False)
                except ImportError:
                    print("\n✗ gdown not available. Please install it:")
                    print("  pip install gdown")
                    print("\nOr download manually:")
                    print(f"1. Visit: https://drive.google.com/uc?id={file_id}")
                    print(f"2. Click 'Download anyway' if virus scan warning appears")
                    print(f"3. Save the file as: {model_path}")
                    raise
        
        # Verify file size
        file_size = model_path.stat().st_size / (1024 * 1024)
        print(f"✓ Model downloaded successfully!")
        print(f"  Saved to: {model_path}")
        print(f"  File size: {file_size:.1f} MB")
        
        if file_size < 100:
            print("⚠ Warning: File size seems too small. Download may have failed.")
            print("  Please download manually from:")
            print(f"  https://drive.google.com/uc?id={file_id}")
        
    except Exception as e:
        print(f"\n✗ Download failed: {e}")
        print("\nPlease download the model manually:")
        print(f"1. Visit: https://drive.google.com/uc?id={file_id}")
        print(f"2. Click 'Download anyway' if virus scan warning appears")
        print(f"3. Save the file as: {model_path}")
        print("\nOr install gdown and run:")
        print("  pip install gdown")
        print(f"  gdown https://drive.google.com/uc?id={file_id} -O {model_path}")

if __name__ == "__main__":
    download_model()

