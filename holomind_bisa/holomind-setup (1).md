# 🧠 HoloMind - Complete Setup & Deployment Guide

## 📋 System Requirements

### Minimum Requirements
- **CPU**: Intel i5 / AMD Ryzen 5 or better
- **RAM**: 8GB (16GB recommended)
- **GPU**: Optional but recommended (NVIDIA with CUDA support)
- **Storage**: 10GB free space
- **Python**: 3.8 or higher
- **OS**: Windows 10/11, macOS 10.15+, Ubuntu 20.04+

### Hardware for Holographic Display
- **Display**: Monitor/TV with HDMI input
- **Holographic Pyramid/Cone**: Glass or acrylic (25-50cm base diameter recommended)
- **Camera**: For gesture recognition (optional)
- **Microphone**: For voice interaction (optional)

## 🚀 Quick Start Installation

### 1. Basic Installation (All Platforms)

```bash
# Clone repository (or create project folder)
mkdir holomind
cd holomind

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install core dependencies
pip install -r requirements.txt
```

### 2. Requirements File

Create `requirements.txt`:

```txt
# Core AI
anthropic>=0.7.0
openai>=1.0.0

# Vision & Graphics
opencv-python>=4.8.0
numpy>=1.24.0
Pillow>=10.0.0
torch>=2.0.0

# Audio & Voice
SpeechRecognition>=3.10.0
pyttsx3>=2.90
sounddevice>=0.4.6
openai-whisper>=20230918

# Machine Learning
sentence-transformers>=2.2.0
scikit-learn>=1.3.0
transformers>=4.30.0

# Computer Vision
mediapipe>=0.10.0

# Utilities
opensimplex>=0.4.3
psutil>=5.9.0
aiofiles>=23.0.0

# Optional GPU support
# torch+cu118  # Uncomment for CUDA 11.8
```

### 3. Configuration File

Create `config.json`:

```json
{
    "api_key": "YOUR_API_KEY_HERE",
    "use_claude": true,
    "agent_name": "Luma",
    "agent_personality": {
        "curiosity": 0.8,
        "empathy": 0.9,
        "creativity": 0.7,
        "analytical": 0.8,
        "playfulness": 0.6
    },
    "display_settings": {
        "resolution": 1024,
        "fps": 30,
        "fullscreen": false,
        "hdmi_output": true
    },
    "hologram_settings": {
        "projection_type": "pyramid",
        "base_diameter_cm": 30,
        "height_cm": 25,
        "calibration_profile": "default"
    },
    "features": {
        "voice_enabled": true,
        "gesture_recognition": false,
        "multi_agent": false,
        "learning_system": true,
        "memory_persistence": true
    },
    "memory_settings": {
        "memory_path": "./memories/",
        "max_short_term": 10,
        "max_long_term": 1000,
        "auto_save_interval": 300
    },
    "performance": {
        "use_gpu": true,
        "max_particles": 1000,
        "render_quality": "high",
        "cache_size_mb": 500
    }
}
```

## 🖥️ Platform-Specific Setup

### Windows Setup

```powershell
# Install Visual C++ Redistributables
# Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe

# Install PyTorch with CUDA (if NVIDIA GPU available)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For voice features
pip install pyaudio

# Run initial test
python test_setup.py
```

### macOS Setup

```bash
# Install Homebrew dependencies
brew install portaudio ffmpeg

# Install Python packages
pip install pyobjc-framework-Cocoa  # For display management
pip install pyaudio

# Grant permissions
# System Preferences > Security & Privacy > Microphone/Camera
```

### Linux Setup (Ubuntu/Debian)

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y \
    python3-dev \
    portaudio19-dev \
    libopencv-dev \
    libgl1-mesa-glx \
    ffmpeg

# For NVIDIA GPU
sudo apt-get install nvidia-cuda-toolkit

# Install Python packages
pip install -r requirements.txt
```

## 🎮 Running HoloMind

### Basic Launch

```bash
# Activate virtual environment first
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Run HoloMind
python main.py

# With specific configuration
python main.py --config my_config.json

# Headless mode (no display window)
python main.py --headless

# Start in specific mode
python main.py --mode learning
```

### Launch Options

```bash
# Available modes:
python main.py --mode conversation  # Default chat mode
python main.py --mode gesture       # Gesture recognition mode
python main.py --mode data_viz      # Data visualization mode
python main.py --mode learning      # Educational mode
python main.py --mode meditation    # Relaxation mode

# Debug mode
python main.py --debug --log-level DEBUG

# Performance monitoring
python main.py --monitor-performance
```

## 📐 Hologram Calibration

### First-Time Setup

1. **Place your pyramid/cone on the display**
2. **Run calibration mode:**
   ```bash
   python calibrate.py
   ```
3. **Follow on-screen instructions:**
   - Adjust the square to match your pyramid base
   - Use arrow keys or touch gestures
   - Press 'S' to save calibration

### Calibration Profiles

Create different profiles in `calibration_profiles.json`:

```json
{
    "tv_living_room": {
        "display_width": 1920,
        "display_height": 1080,
        "projection_x": 960,
        "projection_y": 540,
        "projection_size": 800,
        "reflector_type": "pyramid"
    },
    "laptop_screen": {
        "display_width": 1366,
        "display_height": 768,
        "projection_x": 683,
        "projection_y": 384,
        "projection_size": 500,
        "reflector_type": "cone"
    }
}
```

## 🔌 HDMI Setup

### Connecting to External Display

1. **Connect HDMI cable** from laptop/device to TV/monitor
2. **Configure display:**
   
   **Windows:**
   - Press Win+P
   - Select "Extend" or "Second screen only"
   
   **macOS:**
   - System Preferences > Displays
   - Arrangement tab > Uncheck "Mirror Displays"
   
   **Linux:**
   ```bash
   xrandr --output HDMI-1 --mode 1920x1080 --right-of eDP-1
   ```

3. **Update config.json:**
   ```json
   {
       "display_settings": {
           "hdmi_output": true,
           "hdmi_resolution": [1920, 1080],
           "hdmi_position": "extended"
       }
   }
   ```

## 🐳 Docker Deployment

### Build Docker Image

```bash
# Generate Docker files
python main.py --generate-docker

# Build image
docker build -t holomind:latest .

# Run container with display
docker run -it \
    -e DISPLAY=$DISPLAY \
    -e ANTHROPIC_API_KEY=your_key_here \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v $(pwd)/memories:/app/memories \
    --device /dev/dri \
    holomind:latest
```

### Docker Compose

```yaml
version: '3.8'

services:
  holomind:
    image: holomind:latest
    environment:
      - DISPLAY=${DISPLAY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - /tmp/.X11-unix:/tmp/.X11-unix:rw
      - ./memories:/app/memories
      - ./config.json:/app/config.json
    devices:
      - /dev/dri:/dev/dri
    network_mode: host
    stdin_open: true
    tty: true
```

## 🏦 Banking/Enterprise Deployment

### Secure Configuration

```json
{
    "security": {
        "api_key_source": "environment",
        "encrypt_memories": true,
        "audit_logging": true,
        "pii_detection": true
    },
    "compliance": {
        "gdpr_mode": true,
        "data_retention_days": 90,
        "user_consent_required": true
    },
    "enterprise": {
        "ldap_integration": false,
        "sso_enabled": false,
        "custom_branding": {
            "agent_name": "BankBot",
            "colors": ["#003366", "#0066CC"],
            "logo_path": "./assets/bank_logo.png"
        }
    }
}
```

### Kiosk Mode Setup

```bash
# Install kiosk dependencies
sudo apt-get install unclutter chromium-browser

# Create kiosk startup script
cat > /home/kiosk/start_holomind.sh << EOF
#!/bin/bash
# Hide cursor
unclutter -idle 0.5 -root &

# Disable screen blanking
xset s noblank
xset s off
xset -dpms

# Start HoloMind in fullscreen
cd /home/kiosk/holomind
python main.py --fullscreen --kiosk-mode
EOF

chmod +x /home/kiosk/start_holomind.sh
```

## 🎯 Testing Installation

Create `test_setup.py`:

```python
#!/usr/bin/env python3
"""Test HoloMind installation"""

import sys
import importlib

def test_imports():
    """Test all required imports"""
    required = [
        'cv2',
        'numpy',
        'torch',
        'anthropic',
        'speech_recognition',
        'mediapipe'
    ]
    
    print("Testing imports...")
    for module in required:
        try:
            importlib.import_module(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            return False
    
    return True

def test_gpu():
    """Test GPU availability"""
    import torch
    
    print("\nGPU Test:")
    if torch.cuda.is_available():
        print(f"✓ CUDA available: {torch.cuda.get_device_name(0)}")
    else:
        print("✗ No CUDA GPU available (CPU mode will be used)")
    
    return True

def test_display():
    """Test display output"""
    import cv2
    import numpy as np
    
    print("\nDisplay Test:")
    try:
        # Create test window
        test_img = np.zeros((512, 512, 3), dtype=np.uint8)
        cv2.putText(test_img, "HoloMind Test", (150, 256),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.imshow("Test", test_img)
        print("✓ Display working (press any key to continue)")
        cv2.waitKey(1000)
        cv2.destroyAllWindows()
        return True
    except Exception as e:
        print(f"✗ Display error: {e}")
        return False

def test_api_connection():
    """Test API connectivity"""
    import os
    
    print("\nAPI Test:")
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if api_key:
        print("✓ API key found")
        # Could add actual API test here
    else:
        print("✗ No API key found. Set ANTHROPIC_API_KEY environment variable")
    
    return True

if __name__ == "__main__":
    print("="*50)
    print("HoloMind Installation Test")
    print("="*50)
    
    all_tests_passed = True
    
    all_tests_passed &= test_imports()
    all_tests_passed &= test_gpu()
    all_tests_passed &= test_display()
    all_tests_passed &= test_api_connection()
    
    print("\n" + "="*50)
    if all_tests_passed:
        print("✅ All tests passed! HoloMind is ready to run.")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    print("="*50)
```

## 🛠️ Troubleshooting

### Common Issues

**1. ImportError: No module named 'cv2'**
```bash
pip uninstall opencv-python opencv-python-headless
pip install opencv-python
```

**2. CUDA not detected**
```bash
# Check CUDA version
nvidia-smi

# Reinstall PyTorch with correct CUDA version
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

**3. Microphone not working**
```bash
# Linux: Check permissions
sudo usermod -a -G audio $USER
# Logout and login again
```

**4. Display issues on HDMI**
```bash
# Check display detection
xrandr  # Linux
# or
python -c "import screeninfo; print(screeninfo.get_monitors())"
```

## 📚 Additional Resources

### Documentation
- [API Reference](./docs/api_reference.md)
- [Creating Custom Visualizations](./docs/custom_visualizations.md)
- [Training Custom Models](./docs/training.md)

### Example Projects
- [Banking Assistant](./examples/banking_assistant/)
- [Educational Tutor](./examples/education/)
- [Therapy Companion](./examples/therapy/)

### Community
- GitHub: https://github.com/yourusername/holomind
- Discord: https://discord.gg/holomind
- Documentation: https://holomind.ai/docs

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

---

**Ready to bring your AI to life? Start HoloMind and watch your digital assistant manifest in the physical world!** 🚀✨