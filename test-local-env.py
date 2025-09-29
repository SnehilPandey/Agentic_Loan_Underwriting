#!/usr/bin/env python3
"""
Test script to verify local Python environment setup
"""

import sys
import os
import platform
import subprocess
import tempfile
from pathlib import Path

def test_python_version():
    """Test Python version and basic info"""
    print("=" * 50)
    print("PYTHON ENVIRONMENT TESTS")
    print("=" * 50)
    
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.architecture()}")
    return True

def test_virtual_environment():
    """Test if we're in a virtual environment"""
    print("\n--- Virtual Environment Test ---")
    
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if in_venv:
        print("✅ Running in virtual environment")
        print(f"   Virtual env path: {sys.prefix}")
        print(f"   Base Python: {sys.base_prefix}")
    else:
        print("⚠️  Not in virtual environment")
    
    return in_venv

def test_basic_imports():
    """Test basic Python module imports"""
    print("\n--- Basic Module Import Tests ---")
    
    modules_to_test = [
        'os', 'sys', 'json', 'datetime', 'urllib.request',
        'sqlite3', 'csv', 'random', 'math', 'collections'
    ]
    
    passed = 0
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {module}")
            passed += 1
        except ImportError as e:
            print(f"❌ {module} - {e}")
    
    print(f"\nModule import test: {passed}/{len(modules_to_test)} passed")
    return passed == len(modules_to_test)

def test_file_operations():
    """Test basic file operations"""
    print("\n--- File Operations Test ---")
    
    try:
        # Test temporary file creation
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            test_content = "Hello, local environment!"
            f.write(test_content)
            temp_file = f.name
        
        # Test reading
        with open(temp_file, 'r') as f:
            content = f.read()
        
        if content == test_content:
            print("✅ File write/read operations")
        else:
            print("❌ File content mismatch")
            return False
        
        # Test file deletion
        os.unlink(temp_file)
        print("✅ File deletion")
        
        return True
        
    except Exception as e:
        print(f"❌ File operations failed: {e}")
        return False

def test_current_directory():
    """Test current working directory access"""
    print("\n--- Current Directory Test ---")
    
    try:
        cwd = os.getcwd()
        print(f"✅ Current directory: {cwd}")
        
        # Test listing directory contents
        items = os.listdir('.')
        print(f"✅ Directory listing: {len(items)} items found")
        
        # Show some key files if they exist
        key_files = ['setup.py', 'README.rst', 'LICENSE', 'configure']
        found_files = [f for f in key_files if f in items]
        if found_files:
            print(f"   Key files found: {', '.join(found_files)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Directory access failed: {e}")
        return False

def test_pip_availability():
    """Test if pip is available and working"""
    print("\n--- Pip Availability Test ---")
    
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"✅ Pip available: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Pip error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Pip test failed: {e}")
        return False

def test_network_access():
    """Test basic network access"""
    print("\n--- Network Access Test ---")
    
    try:
        import urllib.request
        import socket
        
        # Test DNS resolution
        socket.gethostbyname('google.com')
        print("✅ DNS resolution")
        
        # Test HTTP request (with timeout)
        with urllib.request.urlopen('https://httpbin.org/get', timeout=5) as response:
            if response.status == 200:
                print("✅ HTTP request")
                return True
            else:
                print(f"❌ HTTP request failed: {response.status}")
                return False
                
    except Exception as e:
        print(f"⚠️  Network access limited: {e}")
        return False

def run_all_tests():
    """Run all environment tests"""
    print("Starting Local Environment Tests...\n")
    
    tests = [
        ("Python Version", test_python_version),
        ("Virtual Environment", test_virtual_environment),
        ("Basic Imports", test_basic_imports),
        ("File Operations", test_file_operations),
        ("Current Directory", test_current_directory),
        ("Pip Availability", test_pip_availability),
        ("Network Access", test_network_access),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your local environment is ready.")
    else:
        print("⚠️  Some tests failed. Check the details above.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
