#!/usr/bin/env python3
import subprocess
import sys
import os

def install_watsonx():
    """Install IBM Watsonx AI package directly"""
    try:
        # Try installing with pip directly
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "ibm-watsonx-ai", "--quiet"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Successfully installed ibm-watsonx-ai")
            return True
        else:
            print(f"Failed to install: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Installation error: {e}")
        return False

if __name__ == "__main__":
    install_watsonx()