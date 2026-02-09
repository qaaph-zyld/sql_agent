#!/usr/bin/env python3
"""
Comprehensive test runner for SQL Agent
Runs all tests and provides detailed feedback
"""

import subprocess
import sys
import os
from pathlib import Path
import time

def run_test_script():
    """Run the main test script"""
    print("🧪 Running basic tests...")
    
    try:
        result = subprocess.run([sys.executable, "test_agent.py"], 
                              capture_output=True, text=True, timeout=60)
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ Tests timed out")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def test_ollama_connection():
    """Test Ollama connection"""
    print("\n🔍 Testing Ollama connection...")
    
    try:
        # Check if Ollama is running
        result = subprocess.run(["ollama", "list"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Ollama is running")
            
            # Check for llama3 model
            if "llama3" in result.stdout:
                print("✅ Llama3 model is available")
                return True
            else:
                print("⚠️  Llama3 model not found")
                print("Available models:")
                print(result.stdout)
                return False
        else:
            print("❌ Ollama is not running or not installed")
            print("Please install Ollama from https://ollama.ai/")
            return False
            
    except FileNotFoundError:
        print("❌ Ollama command not found")
        print("Please install Ollama from https://ollama.ai/")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Ollama connection timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing Ollama: {e}")
        return False

def test_training_data_extraction():
    """Test training data extraction"""
    print("\n📚 Testing training data extraction...")
    
    try:
        result = subprocess.run([sys.executable, "training_data_extractor.py"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Training data extraction successful")
            print(result.stdout)
            return True
        else:
            print("❌ Training data extraction failed")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Training data extraction timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing training data extraction: {e}")
        return False

def test_streamlit_syntax():
    """Test Streamlit app syntax"""
    print("\n🌐 Testing Streamlit app syntax...")
    
    try:
        # Just check if the file can be parsed
        result = subprocess.run([sys.executable, "-m", "py_compile", "streamlit_app.py"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Streamlit app syntax is valid")
            return True
        else:
            print("❌ Streamlit app has syntax errors")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error testing Streamlit syntax: {e}")
        return False

def check_dependencies():
    """Check if all dependencies are installed"""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        "pandas", "sqlalchemy", "streamlit", "plotly", 
        "python-dotenv", "pathlib"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - not installed")
            missing_packages.append(package)
    
    # Check optional packages
    optional_packages = ["vanna", "chromadb", "ollama"]
    
    print("\nOptional packages:")
    for package in optional_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"⚠️  {package} - not installed (will be installed during setup)")
    
    return len(missing_packages) == 0

def performance_test():
    """Run basic performance tests"""
    print("\n⚡ Running performance tests...")
    
    try:
        # Test import time
        start_time = time.time()
        import pandas as pd
        import sqlalchemy
        import_time = time.time() - start_time
        
        print(f"✅ Import time: {import_time:.2f}s")
        
        # Test basic operations
        start_time = time.time()
        df = pd.DataFrame({"test": [1, 2, 3, 4, 5]})
        df_time = time.time() - start_time
        
        print(f"✅ DataFrame creation: {df_time:.4f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 SQL Agent Comprehensive Test Suite")
    print("=" * 60)
    
    tests = [
        ("Dependencies Check", check_dependencies),
        ("Basic Tests", run_test_script),
        ("Ollama Connection", test_ollama_connection),
        ("Training Data Extraction", test_training_data_extraction),
        ("Streamlit Syntax", test_streamlit_syntax),
        ("Performance Tests", performance_test)
    ]
    
    results = {}
    start_time = time.time()
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    total_time = time.time() - start_time
    
    # Final Summary
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
    
    print(f"\nTotal time: {total_time:.2f}s")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nYour SQL Agent is ready to use!")
        print("\n📋 Next steps:")
        print("1. Ensure Ollama is running: ollama serve")
        print("2. Start the web interface: streamlit run streamlit_app.py")
        print("3. Or use command line: python sql_agent.py")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        print("\n🔧 Troubleshooting:")
        
        if not results.get("Dependencies Check", True):
            print("- Install missing dependencies: pip install -r requirements.txt")
        
        if not results.get("Ollama Connection", True):
            print("- Install and start Ollama: https://ollama.ai/")
            print("- Pull the model: ollama pull llama3")
        
        if not results.get("Training Data Extraction", True):
            print("- Check if existing_repo directory exists")
            print("- Verify QADEE2798 documentation files are present")
        
        print("\nRun individual tests for more details.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
