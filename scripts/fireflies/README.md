# Fireflies Transcription Export to Pinecone

This folder contains scripts to export Fireflies transcription data to Pinecone vector database for semantic search.

## Setup

1. Set up a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Create a `.env` file based on the `.env.example` file:

```bash
cp .env.example .env
```

3. Fill in the environment variables in `.env`:

```
FIREFLIES_API_KEY=your_fireflies_api_key
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX=your_pinecone_index_name
```

## Scripts

### Export Transcriptions to Pinecone

The main script `export_to_pinecone_graphql.py` exports Fireflies transcriptions to Pinecone:

```bash
python export_to_pinecone_graphql.py --namespace fireflies --batch-size 10
```

Options:
- `--namespace`: Pinecone namespace to use (default: "fireflies")
- `--batch-size`: Number of transcripts to process in a batch (default: 10)
- `--force`: Force processing of already processed transcripts
- `--output`: Output file name (default: "fireflies_export.jsonl")
- `--resume-from`: Resume from specified transcript ID
- `--rate-limit-pause`: Pause between transcript processing in seconds (default: 1)

The script:
1. Fetches available transcript IDs from Fireflies
2. Filters out already processed transcripts
3. Processes each transcript:
   - Fetches the full transcript from Fireflies
   - Splits it into chunks
   - Creates embeddings using OpenAI
   - Uploads the embeddings to Pinecone
4. Tracks processed transcripts in `processed_transcripts.txt`

### Search Transcriptions

The `query_vectors.py` script allows you to search for relevant transcriptions:

```bash
python query_vectors.py "What was discussed about WordPress?"
```

Options:
- `--namespace`: Pinecone namespace to search in (default: "fireflies")
- `--top-k`: Number of results to return (default: 5)
- `--describe-index`: Show index stats and structure before searching

The search script:
1. Creates an embedding for your query text using the same OpenAI model
2. Searches the Pinecone index for similar vectors
3. Returns the most relevant transcript chunks with metadata

## Testing

You can run tests to verify your setup:

```bash
python test_pinecone_sdk.py  # Test Pinecone connection
python test_graphql.py       # Test Fireflies API connection
```

## Troubleshooting

- If you see an error about the Pinecone API, make sure your API key is correct and your index exists.
- If embeddings aren't working, check your OpenAI API key and make sure you have billing enabled.
- If no transcripts are found, check your Fireflies API key and ensure you have transcriptions in your account.
- To reprocess transcripts, use the `--force` flag or edit `processed_transcripts.txt`. 