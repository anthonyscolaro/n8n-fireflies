#!/usr/bin/env python3
"""
Query the Pinecone vector database with text input.
This script embeds the query text and searches for similar vectors in the Pinecone index.
"""
import os
import argparse
import logging
from dotenv import load_dotenv
import pinecone
import openai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def setup_openai():
    """Set up OpenAI API with key from environment variables."""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    openai.api_key = openai_api_key
    logger.info("OpenAI API configured")
    return openai.api_key

def setup_pinecone():
    """Set up Pinecone with API key and index from environment variables."""
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    pinecone_index = os.getenv("PINECONE_INDEX")
    
    if not pinecone_api_key:
        raise ValueError("PINECONE_API_KEY environment variable not set")
    if not pinecone_index:
        raise ValueError("PINECONE_INDEX environment variable not set")
    
    # Initialize Pinecone
    pc = pinecone.Pinecone(api_key=pinecone_api_key)
    
    # Connect to the index
    index = pc.Index(pinecone_index)
    logger.info(f"Connected to Pinecone index: {pinecone_index}")
    
    return index

def generate_embedding(text):
    """Generate an embedding for the given text using OpenAI."""
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=text,
        dimensions=1024,
    )
    return response.data[0].embedding

def search_vectors(index, query_vector, namespace, top_k=5):
    """Search for vectors in the Pinecone index."""
    results = index.query(
        vector=query_vector,
        top_k=top_k,
        namespace=namespace,
        include_metadata=True,
    )
    return results.matches

def format_results(results):
    """Format search results with appropriate output."""
    if not results:
        return "No results found"
    
    output = []
    for i, match in enumerate(results):
        result = f"\nResult #{i+1} (Score: {match.score:.4f}):"
        result += f"\nTranscript ID: {match.metadata.get('transcript_id')}"
        result += f"\nTitle: {match.metadata.get('title')}"
        result += f"\nChunk {match.metadata.get('chunk_index')} of {match.metadata.get('total_chunks')}"
        
        # Try different approaches to get the text content
        text = None
        if hasattr(match, 'text'):
            text = match.text
        elif 'text' in match.metadata:
            text = match.metadata['text']
        elif 'content' in match.metadata:
            text = match.metadata['content']
        
        # If we still don't have text, check if we can access metadata directly
        if not text and hasattr(match, 'metadata'):
            metadata_dict = match.metadata
            if isinstance(metadata_dict, dict) and 'content' in metadata_dict:
                text = metadata_dict['content']
        
        # If we still don't have text, we need to try to fetch it
        if not text:
            result += f"\nText: [Text not found in metadata. Content may be stored separately.]"
        else:
            result += f"\nText: {text}"
        
        output.append(result)
    
    return "\n".join(output)

def main():
    """Main function to run the query."""
    parser = argparse.ArgumentParser(description="Query Pinecone vector database with text")
    parser.add_argument("query", type=str, help="Text query to search for")
    parser.add_argument("--namespace", type=str, default="fireflies", help="Pinecone namespace to search in")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results to return")
    parser.add_argument("--describe-index", action="store_true", help="Describe the index before searching")
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Set up OpenAI and Pinecone
    setup_openai()
    index = setup_pinecone()
    
    # Describe the index if requested
    if args.describe_index:
        try:
            # Get index stats
            stats = index.describe_index_stats()
            logger.info(f"Index stats: {stats}")
            
            # Fetch a sample vector to examine its structure
            sample_result = index.query(
                vector=[0.1] * 1024,
                top_k=1,
                namespace=args.namespace,
                include_metadata=True
            )
            if sample_result.matches:
                logger.info(f"Sample vector fields: {dir(sample_result.matches[0])}")
                logger.info(f"Sample metadata keys: {sample_result.matches[0].metadata.keys() if sample_result.matches[0].metadata else 'No metadata'}")
            else:
                logger.info("No vectors found in index for sampling")
        except Exception as e:
            logger.error(f"Error describing index: {str(e)}")
    
    # Generate embedding for query
    logger.info(f"Generating embedding for query: '{args.query}'")
    query_vector = generate_embedding(args.query)
    
    # Search for similar vectors
    logger.info(f"Searching for similar vectors in namespace '{args.namespace}'")
    results = search_vectors(index, query_vector, args.namespace, args.top_k)
    
    # Print results
    logger.info(f"Found {len(results)} results:")
    formatted_results = format_results(results)
    print(formatted_results)

if __name__ == "__main__":
    main() 