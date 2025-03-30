#!/usr/bin/env python3
"""
Export Fireflies transcripts to Pinecone-ready format using GraphQL API.
"""

import os
import sys
import json
import time
import uuid
import argparse
import logging
import requests
import traceback
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("fireflies_export.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def create_embedding(text: str, model: str = "text-embedding-3-small", dimensions: int = 1024) -> List[float]:
    """Create an embedding for the given text."""
    import openai
    
    try:
        response = openai.embeddings.create(
            model=model,
            input=text,
            dimensions=dimensions  # Use 1024 dimensions to match Pinecone index
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error creating embedding: {str(e)}")
        # Add retry logic for resilience
        time.sleep(2)
        try:
            response = openai.embeddings.create(
                model=model,
                input=text,
                dimensions=dimensions
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error creating embedding after retry: {str(e)}")
            raise

def fetch_transcripts_graphql(
    api_key: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100
) -> List[str]:
    """
    Fetch transcript IDs using the GraphQL API.
    
    Args:
        api_key: Fireflies API key
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
        limit: Maximum number of transcripts to fetch
        
    Returns:
        List of transcript IDs
    """
    logger.debug("Starting fetch_transcripts_graphql function")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Updated GraphQL query with correct fields
    query = """
    query {
        transcripts {
            id
            title
            date
        }
    }
    """
    
    # Add date filters as variables if provided
    variables = {}
    if start_date or end_date:
        # Note: Fireflies GraphQL API doesn't directly support date filtering in the same way
        # as the REST API. We'll filter the results in post-processing.
        logger.info(f"Using date filters: start_date={start_date}, end_date={end_date}")
    
    graphql_url = "https://api.fireflies.ai/graphql"
    payload = {
        "query": query,
        "variables": variables
    }
    
    logger.debug(f"GraphQL request: {json.dumps(payload)}")
    
    try:
        response = requests.post(graphql_url, headers=headers, json=payload)
        logger.debug(f"GraphQL response status: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"Error fetching transcripts: {response.status_code} {response.text}")
            return []
        
        data = response.json()
        logger.debug(f"GraphQL response data: {json.dumps(data)[:500]}...")
        
        # Check for GraphQL errors
        if "errors" in data:
            logger.error(f"GraphQL errors: {json.dumps(data['errors'])}")
            return []
        
        # Extract transcript IDs
        transcripts = data.get("data", {}).get("transcripts", [])
        logger.debug(f"Found {len(transcripts)} transcripts in GraphQL response")
        
        # Apply date filtering manually if needed
        if start_date or end_date:
            filtered_transcripts = []
            start_timestamp = datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000 if start_date else None
            end_timestamp = datetime.strptime(end_date, "%Y-%m-%d").timestamp() * 1000 if end_date else None
            
            for transcript in transcripts:
                recording_time = transcript.get("date")
                if not recording_time:
                    continue
                    
                # Convert to timestamp for comparison
                try:
                    # The date is already a timestamp in milliseconds
                    recording_timestamp = recording_time
                    
                    # Apply filters
                    if start_timestamp and recording_timestamp < start_timestamp:
                        continue
                    if end_timestamp and recording_timestamp > end_timestamp:
                        continue
                    
                    filtered_transcripts.append(transcript)
                except Exception as e:
                    logger.warning(f"Error parsing date for transcript {transcript.get('id')}: {str(e)}")
            
            transcripts = filtered_transcripts
            logger.debug(f"After date filtering: {len(transcripts)} transcripts")
            
        # Limit results if needed
        if limit and len(transcripts) > limit:
            transcripts = transcripts[:limit]
            logger.debug(f"After applying limit: {len(transcripts)} transcripts")
            
        # Extract just the IDs
        transcript_ids = [t.get("id") for t in transcripts if t.get("id")]
        logger.debug(f"Returning {len(transcript_ids)} transcript IDs")
        return transcript_ids
        
    except Exception as e:
        logger.error(f"Error fetching transcripts: {str(e)}")
        logger.error(traceback.format_exc())
        return []

def fetch_transcript_details_graphql(api_key: str, transcript_id: str) -> Dict[str, Any]:
    """
    Fetch detailed transcript information using the GraphQL API.
    
    Args:
        api_key: Fireflies API key
        transcript_id: Transcript ID to fetch
        
    Returns:
        Dictionary with transcript details
    """
    logger.debug(f"Starting fetch_transcript_details_graphql for transcript {transcript_id}")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Updated GraphQL query for detailed transcript info with correct field names
    query = """
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
    
    variables = {
        "id": transcript_id
    }
    
    graphql_url = "https://api.fireflies.ai/graphql"
    payload = {
        "query": query,
        "variables": variables
    }
    
    logger.debug(f"GraphQL request for transcript details: {json.dumps(payload)}")
    
    try:
        response = requests.post(graphql_url, headers=headers, json=payload)
        logger.debug(f"GraphQL response status for transcript details: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"Error fetching transcript details: {response.status_code} {response.text}")
            return {}
        
        data = response.json()
        
        # Check for GraphQL errors
        if "errors" in data:
            logger.error(f"GraphQL errors: {json.dumps(data['errors'])}")
            return {}
        
        # Extract transcript details
        transcript = data.get("data", {}).get("transcript", {})
        logger.debug(f"Transcript details retrieved successfully: {transcript.get('id')}")
        return transcript
        
    except Exception as e:
        logger.error(f"Error fetching transcript details: {str(e)}")
        logger.error(traceback.format_exc())
        return {}

def process_transcript(transcript: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Process a transcript into chunks for embedding.
    
    Args:
        transcript: Transcript data from the API
        
    Returns:
        List of chunks with text and metadata
    """
    chunks = []
    
    # Extract metadata
    transcript_id = transcript.get("id", "")
    title = transcript.get("title", "")
    date = transcript.get("date", "")
    duration = transcript.get("duration", 0)
    
    logger.debug(f"Processing transcript: {transcript_id} - {title}")
    
    # Extract participants - now a string array directly
    participants = transcript.get("participants", [])
    logger.debug(f"Found {len(participants)} participants")
    
    # Process sentences
    sentences = transcript.get("sentences", [])
    logger.debug(f"Found {len(sentences)} sentences")
    
    # Group sentences by speaker
    speaker_blocks = []
    current_speaker = None
    current_block = []
    
    for sentence in sentences:
        speaker_id = sentence.get("speaker_id", 0)
        speaker_name = f"Speaker {speaker_id}"
        
        if current_speaker != speaker_name and current_block:
            # Save the current block and start a new one
            speaker_blocks.append({
                "speaker": current_speaker,
                "sentences": current_block
            })
            current_block = []
        
        current_speaker = speaker_name
        current_block.append(sentence)
    
    # Add the last block
    if current_block:
        speaker_blocks.append({
            "speaker": current_speaker,
            "sentences": current_block
        })
    
    logger.debug(f"Created {len(speaker_blocks)} speaker blocks")
    
    # Create chunks from the speaker blocks
    for i, block in enumerate(speaker_blocks):
        # Get context (previous and next speakers) - handle null values for Pinecone
        prev_speaker = speaker_blocks[i-1]["speaker"] if i > 0 else "None"
        next_speaker = speaker_blocks[i+1]["speaker"] if i < len(speaker_blocks)-1 else "None"
        
        # Combine sentences into a single text
        text = " ".join([s.get("text", "") for s in block["sentences"]])
        
        # Create chunk
        chunk = {
            "text": text,
            "metadata": {
                "transcript_id": transcript_id,
                "title": title,
                "speaker": block["speaker"],
                "prev_speaker": prev_speaker,
                "next_speaker": next_speaker,
                "participants": participants,
                "recording_date": date,
                "duration": duration,
                "chunk_index": i,
                "total_chunks": len(speaker_blocks),
                "source": "fireflies"
            }
        }
        
        chunks.append(chunk)
    
    logger.debug(f"Created {len(chunks)} chunks")
    return chunks

def main():
    """Main function to export Fireflies transcripts."""
    logger.info("Starting Fireflies export script")
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Export Fireflies transcripts to Pinecone-ready format')
    parser.add_argument('--output', type=str, default='fireflies_export.jsonl', help='Output file path')
    parser.add_argument('--format', type=str, choices=['jsonl', 'json'], default='jsonl', help='Output format')
    parser.add_argument('--batch-size', type=int, default=100, help='Batch size for API requests')
    parser.add_argument('--rate-limit-pause', type=float, default=1.0, help='Pause between API calls (seconds)')
    parser.add_argument('--start-date', type=str, help='Start date for transcript filtering (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='End date for transcript filtering (YYYY-MM-DD)')
    parser.add_argument('--resume-from', type=str, help='Resume from specified transcript ID')
    parser.add_argument('--namespace', type=str, help='Pinecone namespace to use (optional)')
    parser.add_argument('--force', action='store_true', help='Force processing of already processed transcripts')
    args = parser.parse_args()
    
    # Get API keys
    fireflies_api_key = os.getenv("FIREFLIES_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    
    if not fireflies_api_key:
        logger.error("FIREFLIES_API_KEY not found in environment variables")
        sys.exit(1)
    
    if not openai_api_key:
        logger.error("OPENAI_API_KEY not found in environment variables")
        sys.exit(1)
    
    if not pinecone_api_key:
        logger.error("PINECONE_API_KEY not found in environment variables")
        sys.exit(1)
    
    # Check for previously processed transcripts
    processed_ids = []
    if os.path.exists("processed_transcripts.txt"):
        with open("processed_transcripts.txt", "r") as f:
            processed_ids = [line.strip() for line in f.readlines()]
        logger.info(f"Found {len(processed_ids)} previously processed transcripts")
    
    # Fetch all transcript IDs using GraphQL API
    logger.info("Fetching all transcript IDs...")
    try:
        transcript_ids = fetch_transcripts_graphql(
            fireflies_api_key,
            start_date=args.start_date,
            end_date=args.end_date,
            limit=args.batch_size
        )
        logger.info(f"Found {len(transcript_ids)} transcripts")
        logger.info(f"Transcript IDs: {transcript_ids}")
        
        # Filter out already processed transcripts
        unprocessed_ids = [
            tid for tid in transcript_ids if tid not in processed_ids or args.force
        ]
        logger.info(f"Found {len(unprocessed_ids)} unprocessed transcripts")
        logger.info(f"Unprocessed transcript IDs: {unprocessed_ids}")
        
        # Handle resume-from
        if args.resume_from:
            try:
                resume_index = unprocessed_ids.index(args.resume_from)
                unprocessed_ids = unprocessed_ids[resume_index:]
                logger.info(f"Resuming from transcript {args.resume_from} ({len(unprocessed_ids)} remaining)")
            except ValueError:
                logger.warning(f"Resume point {args.resume_from} not found in transcript list")
        
        # Initialize Pinecone if needed
        pinecone_index = None
        if args.namespace:
            # Updated Pinecone initialization using current API
            import pinecone
            
            pc = pinecone.Pinecone(api_key=pinecone_api_key)
            index_name = os.getenv("PINECONE_INDEX", "conversation-archive")
            pinecone_index = pc.Index(index_name)
            
            logger.info(f"Connected to Pinecone index: {index_name}")
            logger.info(f"Using namespace: {args.namespace}")
        
        # Process transcripts
        count = 0
        with open(args.output, "a") as f:
            for transcript_id in unprocessed_ids:
                try:
                    # Fetch transcript details
                    logger.info(f"Processing transcript {transcript_id}")
                    transcript = fetch_transcript_details_graphql(fireflies_api_key, transcript_id)
                    
                    if not transcript:
                        logger.warning(f"Failed to fetch transcript {transcript_id}")
                        continue
                    
                    # Process transcript into chunks
                    chunks = process_transcript(transcript)
                    
                    if not chunks:
                        logger.warning(f"No chunks generated for transcript {transcript_id}")
                        continue
                    
                    logger.info(f"Generated {len(chunks)} chunks for transcript {transcript_id}")
                    
                    # Process each chunk
                    for chunk in chunks:
                        # Generate embedding
                        try:
                            embedding = create_embedding(chunk["text"])
                            
                            # Prepare output
                            output = {
                                "id": f"fireflies_{transcript_id}_{chunk['metadata']['chunk_index']}",
                                "values": embedding,
                                "metadata": chunk["metadata"],
                                "text": chunk["text"]
                            }
                            
                            # Write to file
                            f.write(json.dumps(output) + "\n")
                            
                            # Upsert to Pinecone if requested
                            if pinecone_index and args.namespace:
                                try:
                                    # Include text in the metadata for easier retrieval
                                    metadata_with_text = output["metadata"].copy()
                                    metadata_with_text["content"] = output["text"]
                                    
                                    pinecone_index.upsert(
                                        vectors=[{
                                            "id": output["id"],
                                            "values": output["values"],
                                            "metadata": metadata_with_text
                                        }],
                                        namespace=args.namespace
                                    )
                                except Exception as e:
                                    logger.error(f"Error upserting to Pinecone: {str(e)}")
                            
                        except Exception as e:
                            logger.error(f"Error processing chunk: {str(e)}")
                    
                    # Mark as processed
                    with open("processed_transcripts.txt", "a") as pf:
                        pf.write(f"{transcript_id}\n")
                    
                    count += 1
                    
                    # Rate limiting
                    time.sleep(args.rate_limit_pause)
                    
                except Exception as e:
                    logger.error(f"Error processing transcript {transcript_id}: {str(e)}")
                    logger.error(traceback.format_exc())
        
        logger.info(f"Exported {count} transcripts to {args.output}")
        logger.info(f"Total processed: {count}")
        logger.info("You can now import this data into Pinecone")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main() 