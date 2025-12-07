"""
Test script to verify the setup is correct
"""
import sys
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'torch', 'torchvision', 
        'PIL', 'numpy', 'cv2'
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == 'PIL':
                __import__('PIL')
            elif package == 'cv2':
                __import__('cv2')
            else:
                __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("\n✓ All dependencies installed!")
        return True

def check_model():
    """Check if model weights exist"""
    print("\n🔍 Checking model weights...")
    
    model_path = Path("service/models/u2net.pth")
    
    if not model_path.exists():
        print(f"  ✗ Model not found at {model_path}")
        print("\n⚠️  Please download the model:")
        print("  Run: python service/download_model.py")
        return False
    
    file_size = model_path.stat().st_size / (1024 * 1024)
    print(f"  ✓ Model found: {model_path}")
    print(f"  ✓ File size: {file_size:.1f} MB")
    
    if file_size < 100:
        print("  ⚠️  Warning: File size seems small. May be corrupted.")
        return False
    
    return True

def check_structure():
    """Check project structure"""
    print("\n🔍 Checking project structure...")
    
    required_files = [
        "service/app.py",
        "service/u2net.py",
        "service/__init__.py",
        "client/index.html",
        "client/styles.css",
        "client/script.js",
        "requirements.txt",
        "main.py",
    ]
    
    missing = []
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} - MISSING")
            missing.append(file_path)
    
    if missing:
        print(f"\n⚠️  Missing files: {', '.join(missing)}")
        return False
    else:
        print("\n✓ All required files present!")
        return True

def check_pytorch():
    """Check PyTorch installation and CUDA availability"""
    print("\n🔍 Checking PyTorch...")
    
    try:
        import torch
        print(f"  ✓ PyTorch version: {torch.__version__}")
        print(f"  ✓ CUDA available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"  ✓ CUDA version: {torch.version.cuda}")
            print(f"  ✓ GPU device: {torch.cuda.get_device_name(0)}")
        else:
            print("  ℹ️  Running on CPU (slower but works)")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_model_import():
    """Test if model can be imported"""
    print("\n🔍 Testing model import...")
    
    try:
        from service.u2net import U2NET
        print("  ✓ U2NET model can be imported")
        
        model = U2NET(3, 1)
        print("  ✓ U2NET model can be instantiated")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    """Run all checks"""
    print("=" * 60)
    print("🎨 Background Removal Tool - Setup Verification")
    print("=" * 60)
    
    checks = [
        ("Project Structure", check_structure),
        ("Dependencies", check_dependencies),
        ("PyTorch", check_pytorch),
        ("Model Import", test_model_import),
        ("Model Weights", check_model),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} check failed with error: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All checks passed! You're ready to run the application.")
        print("\nNext steps:")
        print("  1. Start backend: python main.py")
        print("  2. Open frontend: client/index.html")
        print("  3. Or run: ./start.sh (Mac/Linux) or start.bat (Windows)")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nQuick fixes:")
        print("  - Install deps: pip install -r requirements.txt")
        print("  - Download model: python service/download_model.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())

