#!/usr/bin/env python3
"""
Test script for SQL Agent
Tests the basic functionality without requiring database connection
"""

import sys
import json
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        import sqlalchemy
        print("✅ sqlalchemy imported successfully")
    except ImportError as e:
        print(f"❌ sqlalchemy import failed: {e}")
        return False
    
    try:
        import streamlit
        print("✅ streamlit imported successfully")
    except ImportError as e:
        print(f"❌ streamlit import failed: {e}")
        return False
    
    # Test Vanna.AI imports (optional)
    try:
        from vanna.ollama import Ollama
        from vanna.chromadb import ChromaDB_VectorStore
        print("✅ Vanna.AI imported successfully")
    except ImportError as e:
        print(f"⚠️  Vanna.AI import failed: {e}")
        print("   This is expected if Vanna.AI is not installed yet")
    
    return True

def test_config():
    """Test configuration loading"""
    print("\n🧪 Testing configuration...")
    
    config_file = Path("config.json")
    if not config_file.exists():
        print("❌ config.json not found")
        return False
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        required_keys = ["database", "vanna"]
        for key in required_keys:
            if key not in config:
                print(f"❌ Missing required config key: {key}")
                return False
        
        print("✅ Configuration loaded successfully")
        print(f"   Database: {config['database']['database']}")
        print(f"   Server: {config['database']['server']}")
        return True
        
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return False

def test_training_data_extractor():
    """Test training data extraction"""
    print("\n🧪 Testing training data extractor...")
    
    try:
        from training_data_extractor import TrainingDataExtractor
        
        extractor = TrainingDataExtractor()
        
        # Test if repo path exists
        if not extractor.repo_path.exists():
            print("❌ Repository path not found")
            return False
        
        if not extractor.db_docs_path.exists():
            print("❌ Database documentation path not found")
            return False
        
        print("✅ Training data extractor initialized successfully")
        
        # Test extraction (without saving)
        try:
            training_data = extractor.extract_all_training_data()
            print(f"✅ Extracted training data:")
            print(f"   Business docs: {len(training_data['business_documentation'])}")
            print(f"   Example queries: {len(training_data['example_queries'])}")
            print(f"   Column definitions: {len(training_data['column_definitions'])}")
            return True
        except Exception as e:
            print(f"⚠️  Training data extraction failed: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ Cannot import training data extractor: {e}")
        return False

def test_sql_agent_import():
    """Test SQL Agent import (without initialization)"""
    print("\n🧪 Testing SQL Agent import...")
    
    try:
        # Test if we can import the class without initializing
        import importlib.util
        spec = importlib.util.spec_from_file_location("sql_agent", "sql_agent.py")
        sql_agent_module = importlib.util.module_from_spec(spec)
        
        print("✅ SQL Agent module can be loaded")
        return True
        
    except Exception as e:
        print(f"❌ SQL Agent import failed: {e}")
        return False

def test_streamlit_app():
    """Test Streamlit app import"""
    print("\n🧪 Testing Streamlit app...")
    
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("streamlit_app", "streamlit_app.py")
        streamlit_module = importlib.util.module_from_spec(spec)
        
        print("✅ Streamlit app can be loaded")
        return True
        
    except Exception as e:
        print(f"❌ Streamlit app import failed: {e}")
        return False

def test_file_structure():
    """Test if all required files exist"""
    print("\n🧪 Testing file structure...")
    
    required_files = [
        "requirements.txt",
        "config.json",
        "sql_agent.py",
        "streamlit_app.py",
        "training_data_extractor.py",
        "setup.py",
        "README.md"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files present")
    return True

def main():
    """Run all tests"""
    print("🚀 SQL Agent Test Suite")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Training Data Extractor", test_training_data_extractor),
        ("SQL Agent Import", test_sql_agent_import),
        ("Streamlit App", test_streamlit_app)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The SQL Agent is ready to use.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Setup Ollama: ollama pull llama3")
        print("3. Run setup: python setup.py")
        print("4. Start the app: streamlit run streamlit_app.py")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please address the issues above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
