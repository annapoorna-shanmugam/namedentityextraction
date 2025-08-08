#!/usr/bin/env python3
"""
Healthcare NER and Event Extraction System
Run script for the web application

Usage: python3 run_application.py
"""

import sys
import os
import subprocess

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    return True

def install_requirements():
    """Install required packages"""
    try:
        print("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install requirements")
        return False

def test_imports():
    """Test if all modules can be imported"""
    try:
        from healthcare_entity_extractor import HealthcareEntityExtractor
        from event_extractor import HealthcareEventExtractor
        from healthcare_tokenizer import HealthcareTokenizer
        import flask
        print("✓ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def run_flask_app():
    """Run the Flask application"""
    try:
        print("\n" + "="*50)
        print("Healthcare NER & Event Extraction System")
        print("="*50)
        print("Starting Flask application...")
        print("Access the application at: http://localhost:5000")
        print("Press Ctrl+C to stop the server")
        print("="*50 + "\n")
        
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except ImportError as e:
        print(f"✗ Failed to import Flask app: {e}")
        return False
    except Exception as e:
        print(f"✗ Failed to start Flask app: {e}")
        return False

def main():
    """Main execution function"""
    print("Healthcare NER System - Setup and Launch")
    print("-" * 40)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Install requirements
    if not install_requirements():
        return 1
    
    # Test imports
    if not test_imports():
        return 1
    
    # Run the application
    run_flask_app()
    return 0

if __name__ == "__main__":
    sys.exit(main())