#!/usr/bin/env python3
"""Test script to verify rink image path resolution in GitHub Actions"""

import os
import sys

def test_rink_image_path():
    """Test that the rink image can be found using the same logic as pdf_report_generator.py"""
    
    print("=" * 60)
    print("TESTING RINK IMAGE PATH RESOLUTION")
    print("=" * 60)
    
    # Test 1: Get script directory using __file__ (same as pdf_report_generator.py)
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"\n✅ Test 1: Script directory (using __file__): {script_dir}")
    except NameError:
        script_dir = os.getcwd()
        print(f"\n⚠️  Test 1: Script directory (fallback to cwd): {script_dir}")
    
    # Test 2: Construct rink path (same logic as pdf_report_generator.py)
    rink_path = os.path.join(script_dir, 'F300E016-E2BD-450A-B624-5BADF3853AC0.jpeg')
    print(f"\n✅ Test 2: Rink path (script_dir): {rink_path}")
    print(f"   Exists: {os.path.exists(rink_path)}")
    
    # Test 3: Check current working directory
    cwd = os.getcwd()
    print(f"\n✅ Test 3: Current working directory: {cwd}")
    cwd_rink_path = os.path.join(cwd, 'F300E016-E2BD-450A-B624-5BADF3853AC0.jpeg')
    print(f"   CWD rink path: {cwd_rink_path}")
    print(f"   Exists: {os.path.exists(cwd_rink_path)}")
    
    # Test 4: List files in script directory
    print(f"\n✅ Test 4: Files in script directory:")
    try:
        files = os.listdir(script_dir)
        rink_files = [f for f in files if 'F300E016' in f or 'rink' in f.lower()]
        if rink_files:
            for f in rink_files:
                full_path = os.path.join(script_dir, f)
                exists = os.path.exists(full_path)
                size = os.path.getsize(full_path) if exists else 0
                print(f"   - {f}: exists={exists}, size={size} bytes")
        else:
            print(f"   No rink-related files found")
            print(f"   First 10 files in directory: {files[:10]}")
    except Exception as e:
        print(f"   Error listing directory: {e}")
    
    # Final check: Which path actually works?
    print(f"\n" + "=" * 60)
    print("FINAL RESULT:")
    print("=" * 60)
    
    if os.path.exists(rink_path):
        print(f"✅ SUCCESS: Rink image found at: {rink_path}")
        file_size = os.path.getsize(rink_path)
        print(f"   File size: {file_size} bytes")
        
        # Try to verify it's actually an image
        try:
            from PIL import Image
            img = Image.open(rink_path)
            print(f"   Image format: {img.format}")
            print(f"   Image size: {img.size}")
            print(f"   Image mode: {img.mode}")
            print(f"✅ Image file is valid!")
            return 0
        except Exception as e:
            print(f"   ⚠️  Warning: Could not verify as image: {e}")
            return 0
    elif os.path.exists(cwd_rink_path):
        print(f"✅ SUCCESS: Rink image found at (cwd): {cwd_rink_path}")
        file_size = os.path.getsize(cwd_rink_path)
        print(f"   File size: {file_size} bytes")
        return 0
    else:
        print(f"❌ FAILURE: Rink image not found!")
        print(f"   Tried: {rink_path}")
        print(f"   Tried: {cwd_rink_path}")
        return 1

if __name__ == "__main__":
    exit_code = test_rink_image_path()
    sys.exit(exit_code)

