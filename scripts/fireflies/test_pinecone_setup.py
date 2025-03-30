#!/usr/bin/env python3
"""
Test script to verify Pinecone and OpenAI API setup.
This creates a simple test vector and queries it to ensure everything is working.
"""

import os
import sys
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import time
import json
import requests

# Load environment variables
load_dotenv(Path(__file__).parent / '.env')

# Verify API keys
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.environ.get("PINECONE_ENVIRONMENT")
PINECONE_INDEX = os.environ.get("PINECONE_INDEX")
PINECONE_HOST = os.environ.get("PINECONE_HOST")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

missing_keys = []
if not PINECONE_API_KEY: missing_keys.append("PINECONE_API_KEY")
if not PINECONE_HOST: missing_keys.append("PINECONE_HOST")
if not OPENAI_API_KEY: missing_keys.append("OPENAI_API_KEY")

if missing_keys:
    print(f"Error: Missing environment variables: {', '.join(missing_keys)}")
    print("Please ensure all required keys are set in the .env file.")
    sys.exit(1)

print("✅ All required API keys found in .env file")

# Test OpenAI API connection
print("\nTesting OpenAI API connection...")
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.embeddings.create(
        input="This is a test message to verify the OpenAI API connection.",
        model="text-embedding-3-small",
        dimensions=1536
    )
    embedding = response.data[0].embedding
    
    print(f"✅ Successfully generated embedding with {len(embedding)} dimensions")
except Exception as e:
    print(f"❌ Error connecting to OpenAI API: {e}")
    sys.exit(1)

# Test Pinecone API connection
print("\nTesting Pinecone API connection...")

# Print the settings we're using
print(f"Index: {PINECONE_INDEX}")
print(f"Host: {PINECONE_HOST}")

# Use the full host URL from the environment
api_url = f"{PINECONE_HOST}/vectors/upsert"
print(f"Using URL: {api_url}")

# Pinecone expects the API key in the "Api-Key" header (note the capitalization)
headers = {
    "Api-Key": PINECONE_API_KEY,
    "Content-Type": "application/json"
}

print(f"API Key prefix: {PINECONE_API_KEY[:10]}...")

# Create test vector using the embedding we just generated
test_vector = {
    "vectors": [{
        "id": "test_vector_" + str(int(time.time())),
        "values": embedding,
        "metadata": {
            "source_type": "test",
            "title": "Test Vector",
            "description": "This is a test vector to verify Pinecone connection"
        }
    }]
}

# Insert test vector
try:
    print(f"Connecting to: {api_url}")
    print("Headers: Api-Key: [MASKED], Content-Type: application/json")
    
    # Try both header formats (some Pinecone services expect different capitalization)
    response = requests.post(api_url, headers=headers, data=json.dumps(test_vector))
    
    if response.status_code == 401:
        print("Trying alternate header format...")
        alt_headers = {
            "api-key": PINECONE_API_KEY,
            "content-type": "application/json"
        }
        response = requests.post(api_url, headers=alt_headers, data=json.dumps(test_vector))
    
    response.raise_for_status()
    print(f"✅ Successfully inserted test vector into Pinecone index '{PINECONE_INDEX}'")
except Exception as e:
    print(f"❌ Error connecting to Pinecone API: {e}")
    if hasattr(response, 'text'):
        print(f"Response: {response.text}")
    sys.exit(1)

# Test query - use the same URL format as above but with /query endpoint
query_url = api_url.replace('/vectors/upsert', '/query')

query_data = {
    "vector": embedding,
    "topK": 1,
    "includeMetadata": True
}

try:
    # Use same headers that worked for upsert
    response = requests.post(query_url, headers=headers, data=json.dumps(query_data))
    response.raise_for_status()
    result = response.json()
    
    if result.get('matches') and len(result['matches']) > 0:
        match = result['matches'][0]
        print(f"✅ Successfully queried Pinecone and found test vector with score: {match.get('score', 'N/A')}")
    else:
        print("⚠️ Query successful but no matching vectors found")
    
except Exception as e:
    print(f"❌ Error querying Pinecone: {e}")
    if hasattr(response, 'text'):
        print(f"Response: {response.text}")
    sys.exit(1)

print("\n🎉 All tests passed! Your setup is correctly configured.")
print("You can now run the export script to process your Fireflies transcripts.")
print("\nNext step: Run the export with:")
print("python export_to_pinecone.py") 