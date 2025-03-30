#!/usr/bin/env python3
"""
Test script for Fireflies GraphQL API.
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_graphql():
    """Test the GraphQL API."""
    api_key = os.getenv("FIREFLIES_API_KEY")
    if not api_key:
        print("Error: FIREFLIES_API_KEY not found in .env file")
        return False
    
    print(f"Using API key: {api_key[:5]}...{api_key[-5:]}")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    graphql_url = "https://api.fireflies.ai/graphql"
    
    # Query for transcripts
    query = """
    query {
      transcripts {
        title
        id
        date
      }
    }
    """
    
    payload = {
        "query": query
    }
    
    print("Querying transcripts...")
    response = requests.post(graphql_url, headers=headers, json=payload)
    print(f"Status code: {response.status_code}")
    
    # Print response content for debugging
    try:
        print(f"Response content: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response content (raw): {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        transcripts = data.get("data", {}).get("transcripts", [])
        print(f"Found {len(transcripts)} transcripts")
        
        if transcripts:
            transcript_id = transcripts[0]["id"]
            print(f"Testing transcript details for ID: {transcript_id}")
            
            # Query for transcript details - updated with correct fields
            detail_query = """
            query GetTranscript($id: String!) {
                transcript(id: $id) {
                    id
                    title
                    date
                    duration
                    participants
                    sentences {
                        text
                        speaker_id
                        start_time
                        end_time
                    }
                }
            }
            """
            
            detail_payload = {
                "query": detail_query,
                "variables": {
                    "id": transcript_id
                }
            }
            
            detail_response = requests.post(graphql_url, headers=headers, json=detail_payload)
            print(f"Detail status code: {detail_response.status_code}")
            
            # Print detail response content for debugging
            try:
                print(f"Detail response content: {json.dumps(detail_response.json(), indent=2)}")
            except:
                print(f"Detail response content (raw): {detail_response.text}")
            
            if detail_response.status_code == 200:
                detail_data = detail_response.json()
                transcript = detail_data.get("data", {}).get("transcript", {})
                
                if transcript:
                    print(f"Title: {transcript.get('title')}")
                    print(f"Duration: {transcript.get('duration')} seconds")
                    participants = transcript.get('participants', [])
                    print(f"Participants: {len(participants)} people")
                    sentences = transcript.get('sentences', [])
                    print(f"Sentences: {len(sentences)} sentences")
                    return True
    
    return False

if __name__ == "__main__":
    success = test_graphql()
    print("\nGraphQL API test: " + ("SUCCESS" if success else "FAILED"))
