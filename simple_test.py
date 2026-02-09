#!/usr/bin/env python3
"""
Simple test script for SQL Agent core functionality
"""

import sys
import json
from pathlib import Path

def test_basic_setup():
    """Test basic project setup"""
    print("Testing basic project setup...")
    
    # Check if required files exist
    required_files = [
        "requirements.txt",
        "config.json", 
        "sql_agent.py",
        "streamlit_app.py",
        "training_data_extractor.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"FAIL: Missing files: {', '.join(missing_files)}")
        return False
    
    print("PASS: All required files present")
    return True

def test_config_loading():
    """Test configuration loading"""
    print("Testing configuration loading...")
    
    try:
        with open("config.json", 'r') as f:
            config = json.load(f)
        
        if "database" not in config or "vanna" not in config:
            print("FAIL: Missing required config sections")
            return False
        
        print("PASS: Configuration loaded successfully")
        return True
    except Exception as e:
        print(f"FAIL: Error loading config: {e}")
        return False

def test_training_data_extractor():
    """Test training data extractor"""
    print("Testing training data extractor...")
    
    try:
        # Import the module
        import importlib.util
        spec = importlib.util.spec_from_file_location("training_data_extractor", "training_data_extractor.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Test the class
        extractor = module.TrainingDataExtractor()
        
        if not extractor.repo_path.exists():
            print("FAIL: Repository path not found")
            return False
        
        print("PASS: Training data extractor works")
        return True
    except Exception as e:
        print(f"FAIL: Training data extractor error: {e}")
        return False

def test_sql_agent_module():
    """Test SQL Agent module loading"""
    print("Testing SQL Agent module...")
    
    try:
        # Try to parse the file
        import ast
        with open("sql_agent.py", 'r') as f:
            content = f.read()
        
        # Parse to check syntax
        ast.parse(content)
        
        print("PASS: SQL Agent module syntax is valid")
        return True
    except Exception as e:
        print(f"FAIL: SQL Agent module error: {e}")
        return False

def main():
    """Run all tests"""
    print("SQL Agent Simple Test Suite")
    print("=" * 40)
    
    tests = [
        test_basic_setup,
        test_config_loading,
        test_training_data_extractor,
        test_sql_agent_module
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"FAIL: Test crashed: {e}")
            results.append(False)
        print()
    
    passed = sum(results)
    total = len(results)
    
    print("=" * 40)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: All tests passed!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install pandas sqlalchemy streamlit plotly python-dotenv")
        print("2. Install Ollama from https://ollama.ai/")
        print("3. Pull model: ollama pull llama3")
        print("4. Run: streamlit run streamlit_app.py")
    else:
        print("Some tests failed. Please check the output above.")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
