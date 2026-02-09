#!/usr/bin/env python3
"""
Setup script for SQL Agent
Installs dependencies and prepares the environment
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_ollama():
    """Check if Ollama is installed and running"""
    print("\n🔍 Checking Ollama installation...")
    
    # Check if ollama command exists
    try:
        result = subprocess.run("ollama --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is installed")
            
            # Check if llama3 model is available
            result = subprocess.run("ollama list", shell=True, capture_output=True, text=True)
            if "llama3" in result.stdout:
                print("✅ Llama3 model is available")
                return True
            else:
                print("⚠️  Llama3 model not found. Pulling model...")
                return run_command("ollama pull llama3", "Pulling Llama3 model")
        else:
            print("❌ Ollama not found")
            return False
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up SQL Agent Environment")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Install Python dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("❌ Failed to install dependencies. Please check requirements.txt")
        sys.exit(1)
    
    # Check Ollama
    if not check_ollama():
        print("\n⚠️  Ollama setup incomplete. Please:")
        print("1. Install Ollama from https://ollama.ai/")
        print("2. Run: ollama pull llama3")
        print("3. Re-run this setup script")
        
        # Continue setup anyway for other components
    
    # Create necessary directories
    directories = ["logs", "chroma_db", "data"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Extract training data
    print("\n📚 Extracting training data...")
    try:
        from training_data_extractor import TrainingDataExtractor
        extractor = TrainingDataExtractor()
        training_data = extractor.save_training_data("data/training_data.json")
        print("✅ Training data extracted successfully")
    except Exception as e:
        print(f"⚠️  Training data extraction failed: {e}")
        print("You can extract training data later by running: python training_data_extractor.py")
    
    # Create .env file template
    env_file = Path(".env")
    if not env_file.exists():
        env_content = """# Database Configuration
DB_SERVER=a265m001
DB_NAME=QADEE2798
DB_USERNAME=PowerBI
DB_PASSWORD=P0werB1
DB_DRIVER=ODBC Driver 17 for SQL Server

# Ollama Configuration
OLLAMA_MODEL=llama3
OLLAMA_TEMPERATURE=0.1

# ChromaDB Configuration
CHROMA_PATH=./chroma_db
"""
        env_file.write_text(env_content)
        print("✅ Created .env file template")
    
    print("\n🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Update .env file with your database credentials if needed")
    print("2. Ensure Ollama is running: ollama serve")
    print("3. Test the agent: python sql_agent.py")
    print("4. Start the web interface: streamlit run streamlit_app.py")

if __name__ == "__main__":
    main()
