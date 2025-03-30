#!/usr/bin/env python3
"""
Setup script for Fireflies to Pinecone export tool.
This script helps create the .env file with API keys.
"""

import os
import sys
from pathlib import Path

def main():
    print("=== Fireflies to Pinecone Export Tool Setup ===")
    print("\nThis script will help you set up your API keys.\n")
    
    env_path = Path(__file__).parent / '.env'
    
    # Check if .env already exists
    if env_path.exists():
        overwrite = input(".env file already exists. Overwrite? (y/n): ").lower()
        if overwrite != 'y':
            print("Setup cancelled. Your existing .env file was not modified.")
            return
    
    # Get API keys
    fireflies_api_key = input("\nEnter your Fireflies API key: ").strip()
    openai_api_key = input("Enter your OpenAI API key: ").strip()
    
    # Optional Pinecone keys
    use_pinecone = input("\nDo you want to set up direct Pinecone import? (y/n): ").lower()
    
    if use_pinecone == 'y':
        pinecone_api_key = input("Enter your Pinecone API key: ").strip()
        pinecone_env = input("Enter your Pinecone environment: ").strip()
        pinecone_index = input("Enter your Pinecone index name: ").strip()
    else:
        pinecone_api_key = pinecone_env = pinecone_index = None
    
    # Create .env file
    with open(env_path, 'w') as f:
        f.write(f"# Fireflies API credentials\n")
        f.write(f"FIREFLIES_API_KEY={fireflies_api_key}\n\n")
        
        f.write(f"# OpenAI API credentials\n")
        f.write(f"OPENAI_API_KEY={openai_api_key}\n\n")
        
        if use_pinecone == 'y':
            f.write(f"# Pinecone Direct Import\n")
            f.write(f"PINECONE_API_KEY={pinecone_api_key}\n")
            f.write(f"PINECONE_ENVIRONMENT={pinecone_env}\n")
            f.write(f"PINECONE_INDEX={pinecone_index}\n")
    
    print("\n.env file created successfully!")
    print(f"Location: {env_path.absolute()}")
    
    # Make export script executable
    export_script = Path(__file__).parent / 'export_to_pinecone.py'
    if export_script.exists():
        try:
            # Make the script executable (Unix/Linux/MacOS)
            if sys.platform != 'win32':
                os.chmod(export_script, 0o755)
                print("\nThe export script has been made executable.")
            
            print("\nYou can now run the export with:")
            print(f"python {export_script.name}")
        except Exception as e:
            print(f"Note: Could not make script executable due to: {e}")
    
    print("\nSetup complete!")

if __name__ == "__main__":
    main() 