#!/usr/bin/env python3
"""
Fireflies to Pinecone Export Script

This script exports all Fireflies transcripts and prepares them for import into Pinecone.
It handles pagination, rate limits, and formats the data with OpenAI embeddings.
"""

import requests
import json
import time
import os
from openai import OpenAI
from datetime import datetime
import argparse
import sys
from dotenv import load_dotenv
from pathlib import Path
import logging
import uuid

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("fireflies_export.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(Path(__file__).parent / '.env')

# Command line arguments
parser = argparse.ArgumentParser(description='Export Fireflies transcripts to Pinecone-ready format')
parser.add_argument('--output', default='fireflies_export.jsonl', help='Output file path')
parser.add_argument('--format', choices=['jsonl', 'json'], default='jsonl', help='Output format')
parser.add_argument('--batch-size', type=int, default=10, help='Batch size for API requests')
parser.add_argument('--rate-limit-pause', type=float, default=1.0, help='Pause between API calls (seconds)')
parser.add_argument('--start-date', help='Start date for transcript filtering (YYYY-MM-DD)')
parser.add_argument('--end-date', help='End date for transcript filtering (YYYY-MM-DD)')
parser.add_argument('--resume-from', help='Resume from specified transcript ID')
parser.add_argument('--namespace', default='', help='Pinecone namespace to use (optional)')
args = parser.parse_args()

# API Keys from environment variables
FIREFLIES_API_KEY = os.environ.get("FIREFLIES_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Validate API keys
if not FIREFLIES_API_KEY:
    logger.error("FIREFLIES_API_KEY environment variable not set")
    sys.exit(1)
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY environment variable not set")
    sys.exit(1)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Headers for Fireflies API
headers = {
    "Authorization": f"Bearer {FIREFLIES_API_KEY}",
    "Content-Type": "application/json"
}

def get_all_transcript_ids():
    """Fetch all transcript IDs from Fireflies with pagination"""
    logger.info("Fetching all transcript IDs...")
    
    all_transcripts = []
    page = 1
    per_page = 100  # Maximum allowed by Fireflies API
    
    # Construct query parameters
    params = {
        "limit": per_page,
        "page": page
    }
    
    # Add date filters if specified
    if args.start_date:
        params["start_date"] = args.start_date
    if args.end_date:
        params["end_date"] = args.end_date
    
    while True:
        try:
            response = requests.get(
                "https://api.fireflies.ai/v1/transcripts",
                headers=headers,
                params=params
            )
            
            response.raise_for_status()
            data = response.json()
            
            page_transcripts = data.get('data', [])
            all_transcripts.extend(page_transcripts)
            
            # Check if we've reached the last page
            total = data.get('meta', {}).get('total', 0)
            current_count = len(all_transcripts)
            logger.info(f"Fetched {current_count}/{total} transcripts")
            
            if current_count >= total or not page_transcripts:
                break
                
            # Move to next page
            page += 1
            params["page"] = page
            time.sleep(args.rate_limit_pause)  # Respect rate limits
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching transcripts page {page}: {e}")
            # Retry after a longer pause if rate limited
            if hasattr(e.response, 'status_code') and e.response.status_code == 429:
                logger.info("Rate limited, pausing for 10 seconds...")
                time.sleep(10)
                continue
            else:
                break
    
    return [t['id'] for t in all_transcripts]

def get_transcript_details(transcript_id):
    """Fetch detailed transcript information"""
    try:
        response = requests.get(
            f"https://api.fireflies.ai/v1/transcripts/{transcript_id}",
            headers=headers
        )
        
        response.raise_for_status()
        return response.json().get('data')
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching transcript {transcript_id}: {e}")
        return None

def get_participants(transcript_id):
    """Fetch participants for a transcript"""
    try:
        response = requests.get(
            f"https://api.fireflies.ai/v1/transcripts/{transcript_id}/participants",
            headers=headers
        )
        
        response.raise_for_status()
        return response.json().get('data', [])
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching participants for {transcript_id}: {e}")
        return []

def create_embedding(text):
    """Create embedding using OpenAI API with retries"""
    if not text:
        text = "Empty transcript"
    
    # Truncate if too long (OpenAI has token limits)
    if len(text) > 8000:
        text = text[:8000]
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.embeddings.create(
                input=text,
                model="text-embedding-3-small",  # Updated to match your Pinecone configuration
                dimensions=1024  # Set to match Pinecone index dimensions
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error creating embedding (attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                # Exponential backoff
                time.sleep(2 ** attempt)
            else:
                return None

def format_date(date_str):
    """Format date to ISO 8601 format for consistent filtering"""
    if not date_str:
        return None
    try:
        # Handle different input formats and normalize to ISO 8601
        # This allows for consistent date filtering across data sources
        if 'T' in date_str:  # Already ISO format with time
            return date_str
        else:  # Just date, add time
            return f"{date_str}T00:00:00Z"
    except Exception as e:
        logger.warning(f"Error formatting date {date_str}: {e}")
        return date_str

def extract_topics(summary, title):
    """Extract potential topics from summary and title"""
    topics = []
    
    # Extract from title if available
    if title:
        # Simple extraction of keywords from title
        title_words = title.lower().split()
        topics.extend([word for word in title_words if len(word) > 3 and word not in ['with', 'and', 'for', 'the', 'this', 'that']])
    
    # Extract from summary if available
    if summary and len(summary) > 10:
        # Very simple keyword extraction - could be improved with NLP
        # Extract phrases that might indicate topics
        potential_topics = []
        for phrase in ["discussed", "talked about", "focused on", "regarding", "about"]:
            if phrase in summary.lower():
                idx = summary.lower().find(phrase) + len(phrase)
                potential_topics.append(summary[idx:idx+50].strip())
        
        if potential_topics:
            topics.extend(potential_topics)
    
    # Clean up topics
    clean_topics = []
    for topic in topics:
        # Remove punctuation at end
        while topic and topic[-1] in '.,;:':
            topic = topic[:-1]
        if topic and len(topic) > 2:
            clean_topics.append(topic)
    
    return list(set(clean_topics))[:5]  # Limit to 5 unique topics

def process_transcript(transcript_id):
    """Process a single transcript"""
    logger.info(f"Processing transcript {transcript_id}")
    
    # Get transcript details
    transcript = get_transcript_details(transcript_id)
    if not transcript:
        return None
    
    # Get participants
    participants = get_participants(transcript_id)
    
    # Extract key information
    transcript_data = {
        "id": transcript_id,
        "title": transcript.get('title', 'No Title'),
        "date": format_date(transcript.get('date')),
        "summary": transcript.get('summary', ''),
        "transcript": transcript.get('transcript', ''),
        "duration": transcript.get('duration', 0),
        "participants": [
            {
                "name": p.get('name', 'Unknown'),
                "email": p.get('email', ''),
                "role": p.get('role', '')
            }
            for p in participants
        ]
    }
    
    # Extract participant information for searchable format
    participant_names = [p.get('name', 'Unknown') for p in participants]
    participant_emails = [p.get('email', '') for p in participants if p.get('email')]
    
    # Create text for embedding
    participant_text = ", ".join([
        f"{p.get('name', 'Unknown')} ({p.get('email', '')})"
        for p in participants
    ])
    
    embedding_text = f"Title: {transcript_data['title']}. "
    
    if transcript_data['summary']:
        embedding_text += f"Summary: {transcript_data['summary']}. "
    
    embedding_text += f"Participants: {participant_text}. "
    
    # Add some transcript content if available
    if transcript_data['transcript']:
        # Get first ~1000 chars of transcript for context
        embedding_text += f"Transcript excerpt: {transcript_data['transcript'][:1000]}..."
    
    # Get embedding
    embedding = create_embedding(embedding_text)
    if not embedding:
        logger.warning(f"Could not create embedding for {transcript_id}, skipping")
        return None
    
    # Extract topics
    topics = extract_topics(transcript_data["summary"], transcript_data["title"])
    
    # Generate unique vector ID with source prefix
    vector_id = f"fireflies_{transcript_id}"
    
    # Format for Pinecone with improved metadata structure
    pinecone_format = {
        "id": vector_id,
        "values": embedding,
        "metadata": {
            # Source information
            "source_type": "fireflies",
            "source_id": transcript_id,
            "source_url": f"https://app.fireflies.ai/transcript/{transcript_id}",
            
            # Content metadata
            "title": transcript_data["title"],
            "date": transcript_data["date"],
            "summary": transcript_data["summary"],
            "transcript_excerpt": transcript_data["transcript"][:1000] if transcript_data["transcript"] else "",
            "duration_seconds": transcript_data["duration"],
            
            # Participant information (searchable format)
            "participant_names": participant_names,
            "participant_emails": participant_emails,
            
            # Topics for better searchability
            "topics": topics,
            
            # Processing metadata
            "processed_date": datetime.now().isoformat(),
            "embedding_model": "text-embedding-3-small"
        }
    }
    
    # Add namespace if specified
    if args.namespace:
        pinecone_format["namespace"] = args.namespace
    
    return pinecone_format

def save_checkpoint(processed_ids):
    """Save checkpoint of processed IDs"""
    with open("fireflies_export_checkpoint.json", "w") as f:
        json.dump({"processed_ids": processed_ids}, f)
    logger.info(f"Saved checkpoint with {len(processed_ids)} processed transcripts")

def load_checkpoint():
    """Load checkpoint of processed IDs"""
    try:
        with open("fireflies_export_checkpoint.json", "r") as f:
            data = json.load(f)
            return set(data.get("processed_ids", []))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def main():
    # Get all transcript IDs
    transcript_ids = get_all_transcript_ids()
    logger.info(f"Found {len(transcript_ids)} transcripts")
    
    # Load previously processed IDs
    processed_ids = load_checkpoint()
    logger.info(f"Found {len(processed_ids)} previously processed transcripts")
    
    # Filter out already processed IDs
    if processed_ids:
        remaining_ids = [id for id in transcript_ids if id not in processed_ids]
        logger.info(f"{len(remaining_ids)} transcripts remain to be processed")
        transcript_ids = remaining_ids
    
    # Resume from specific ID if requested
    if args.resume_from:
        try:
            resume_index = transcript_ids.index(args.resume_from)
            transcript_ids = transcript_ids[resume_index:]
            logger.info(f"Resuming from {args.resume_from}, {len(transcript_ids)} transcripts remaining")
        except ValueError:
            logger.warning(f"Resume ID {args.resume_from} not found in transcript list")
    
    # Process transcripts in batches
    results = []
    batch_size = args.batch_size
    
    try:
        for i in range(0, len(transcript_ids), batch_size):
            batch = transcript_ids[i:i+batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(transcript_ids) + batch_size - 1)//batch_size}")
            
            batch_results = []
            for transcript_id in batch:
                result = process_transcript(transcript_id)
                if result:
                    batch_results.append(result)
                    processed_ids.add(transcript_id)
                    
                time.sleep(args.rate_limit_pause)  # Respect rate limits
            
            # Append batch results
            results.extend(batch_results)
            
            # Update checkpoint after each batch
            save_checkpoint(list(processed_ids))
            
            # Append to output file after each batch
            if batch_results:
                if args.format == 'jsonl':
                    with open(args.output, 'a') as f:
                        for item in batch_results:
                            f.write(json.dumps(item) + '\n')
                # For JSON format, we'll write the complete file at the end
    
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(f"Error during processing: {e}", exc_info=True)
    finally:
        # Save final results for JSON format
        if args.format == 'json' and results:
            with open(args.output, 'w') as f:
                json.dump({"vectors": results}, f)
        
        logger.info(f"Exported {len(results)} transcripts to {args.output}")
        logger.info(f"Total processed: {len(processed_ids)}")
        logger.info("You can now import this data into Pinecone")

if __name__ == "__main__":
    main() 