CREATE TABLE IF NOT EXISTS recordings (
    id TEXT PRIMARY KEY,
    title TEXT,
    date TIMESTAMP,
    duration INTEGER,
    download_url TEXT,
    transcript_url TEXT,
    user_id TEXT,
    metadata JSONB
); 