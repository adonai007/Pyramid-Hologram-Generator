#!/usr/bin/env python3
"""Test HoloMind installation and setup"""

import sys
import importlib
import os

def test_imports():
    """Test all required imports"""
    required = [
        'cv2',
        'numpy',
        'torch',
        'anthropic',
        'speech_recognition',
        'mediapipe',
        'sentence_transformers',
        'opensimplex',
        'psutil'
    ]

    print("Testing imports...")
    failed = []
    for module in required:
        try:
            importlib.import_module(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            failed.append(module)

    return len(failed) == 0

def test_gpu():
    """Test GPU availability"""
    try:
        import torch
        print("\nGPU Test:")
        if torch.cuda.is_available():
            print(f"✓ CUDA available: {torch.cuda.get_device_name(0)}")
            return True
        else:
            print("⚠️ No CUDA GPU available (CPU mode will be used)")
            return True
    except ImportError:
        print("⚠️ PyTorch not available for GPU test")
        return True

def test_display():
    """Test display output"""
    try:
        import cv2
        import numpy as np

        print("\nDisplay Test:")
        # Create test window
        test_img = np.zeros((512, 512, 3), dtype=np.uint8)
        cv2.putText(test_img, "HoloMind Test", (150, 256),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Test", test_img)
        print("✓ Display working (press any key to continue)")
        cv2.waitKey(2000)  # Auto-close after 2 seconds
        cv2.destroyAllWindows()
        return True
    except Exception as e:
        print(f"✗ Display error: {e}")
        return False

def test_api_keys():
    """Test API key availability"""
    print("\nAPI Key Test:")
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')

    if openai_key:
        print("✓ OpenAI API key found")
    else:
        print("⚠️ No OpenAI API key found")

    if anthropic_key:
        print("✓ Anthropic API key found")
    else:
        print("⚠️ No Anthropic API key found")

    if openai_key or anthropic_key:
        return True
    else:
        print("✗ No API keys found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY")
        return False

def test_config():
    """Test configuration file"""
    print("\nConfiguration Test:")
    try:
        import json
        with open('config.json', 'r') as f:
            config = json.load(f)
        print("✓ config.json loaded successfully")

        required_keys = ['api_key', 'use_claude', 'agent_name']
        for key in required_keys:
            if key in config:
                print(f"✓ {key}: {config[key]}")
            else:
                print(f"⚠️ Missing {key} in config")
        return True
    except FileNotFoundError:
        print("⚠️ config.json not found")
        return False
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON in config.json: {e}")
        return False

def main():
    print("="*60)
    print("HoloMind Installation & Setup Test")
    print("="*60)

    tests = [
        ("Dependencies", test_imports),
        ("GPU Support", test_gpu),
        ("Display", test_display),
        ("API Keys", test_api_keys),
        ("Configuration", test_config)
    ]

    results = []
    for name, test_func in tests:
        print(f"\n--- {name} ---")
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append(False)

    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print("✅ All tests passed! HoloMind is ready to run.")
        print("\nNext steps:")
        print("1. Run calibration: python calibrate.py")
        print("2. Start HoloMind: python holomind-core.py")
    else:
        print(f"⚠️ {passed}/{total} tests passed. Check the errors above.")

    print("="*60)
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)