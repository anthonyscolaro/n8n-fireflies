#!/usr/bin/env python3
"""
Test script using the official Pinecone SDK to verify API connection.
"""

import os
import sys
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import time
from pinecone import Pinecone, ServerlessSpec
import uuid

# Load environment variables
load_dotenv(Path(__file__).parent / '.env')

# Verify API keys
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_INDEX = os.environ.get("PINECONE_INDEX")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

missing_keys = []
if not PINECONE_API_KEY: missing_keys.append("PINECONE_API_KEY")
if not PINECONE_INDEX: missing_keys.append("PINECONE_INDEX")
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
        dimensions=1024  # Match Pinecone index dimension
    )
    embedding = response.data[0].embedding
    
    print(f"✅ Successfully generated embedding with {len(embedding)} dimensions")
except Exception as e:
    print(f"❌ Error connecting to OpenAI API: {e}")
    sys.exit(1)

# Test Pinecone API connection
print("\nTesting Pinecone API connection...")
print(f"Using API key prefix: {PINECONE_API_KEY[:10]}...")
print(f"Index name: {PINECONE_INDEX}")

try:
    # Initialize Pinecone
    pc = Pinecone(api_key=PINECONE_API_KEY)
    
    # List indexes to verify connection
    print("Listing available indexes...")
    indexes = pc.list_indexes()
    print(f"Available indexes: {indexes}")
    
    # Check if our index exists
    if any(index.get('name') == PINECONE_INDEX for index in indexes):
        print(f"✅ Found index '{PINECONE_INDEX}'")
        # Get the index details
        index_info = next(index for index in indexes if index.get('name') == PINECONE_INDEX)
        print(f"Index dimension: {index_info.get('dimension')}")
        print(f"Index metric: {index_info.get('metric')}")
        print(f"Index vector type: {index_info.get('vector_type')}")
        
        # Check dimensions match
        if index_info.get('dimension') != len(embedding):
            print(f"⚠️ Warning: Your embedding dimension ({len(embedding)}) doesn't match the index dimension ({index_info.get('dimension')})")
            print("This test will still proceed but you'll need to ensure the dimensions match in your export script.")
    else:
        print(f"⚠️ Index '{PINECONE_INDEX}' not found. Available indexes: {', '.join([idx.get('name', 'unknown') for idx in indexes])}")
        sys.exit(1)
    
    # Connect to the index
    print(f"Connecting to index '{PINECONE_INDEX}'...")
    index = pc.Index(PINECONE_INDEX)
    
    # Generate a unique ID for our test vector
    vector_id = f"test_vector_{uuid.uuid4()}"
    
    # Upsert a test vector
    print("Upserting test vector...")
    index.upsert(
        vectors=[
            {
                "id": vector_id,
                "values": embedding,
                "metadata": {
                    "source_type": "test",
                    "title": "Test Vector",
                    "description": "This is a test vector to verify Pinecone connection"
                }
            }
        ]
    )
    print(f"✅ Successfully inserted test vector with ID '{vector_id}'")
    
    # Query for the vector we just inserted
    print("Querying for test vector...")
    query_response = index.query(
        vector=embedding,
        top_k=1,
        include_metadata=True
    )
    
    if query_response.get('matches') and len(query_response['matches']) > 0:
        match = query_response['matches'][0]
        print(f"✅ Successfully queried Pinecone and found vector with score: {match.get('score', 'N/A')}")
    else:
        print("⚠️ Query successful but no matching vectors found")
    
    # Clean up the test vector
    print("Cleaning up test vector...")
    index.delete(ids=[vector_id])
    print(f"✅ Removed test vector with ID '{vector_id}'")
    
except Exception as e:
    print(f"❌ Error with Pinecone: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n🎉 All tests passed! Your Pinecone setup is correctly configured.")
print("\nIMPORTANT NOTE:")
print("Your Pinecone index is configured for 1024-dimensional vectors.")
print("Make sure to use the same dimensions when exporting your Fireflies data.")
print("\nUpdate your export script with:")
print("  - model: \"text-embedding-3-small\"")
print("  - dimensions: 1024")
print("\nNext step: Run the export with:")
print("python export_to_pinecone.py") 