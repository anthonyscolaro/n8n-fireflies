"""
Streamlit app for browsing Fireflies recordings

Install requirements:
    pip install streamlit psycopg2-binary pandas

Run the app:
    streamlit run fireflies_streamlit_app.py
"""
import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import os

# Database connection settings
DB_SETTINGS = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 5432)),
    'user': os.environ.get('DB_USER', 'firefliesuser'),
    'password': os.environ.get('DB_PASSWORD', 'firefliespass'),
    'dbname': os.environ.get('DB_NAME', 'firefliesdb')
}

def get_recordings():
    conn = psycopg2.connect(**DB_SETTINGS)
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM recordings ORDER BY date DESC;")
            rows = cur.fetchall()
            return pd.DataFrame(rows)
    finally:
        conn.close()

st.title("Fireflies Recordings Browser")

df = get_recordings()

if df.empty:
    st.info("No recordings found in the database.")
    st.stop()

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    title_filter = st.text_input("Title contains")
    date_filter = st.date_input("Date (on or after)", value=None)

filtered_df = df.copy()
if title_filter:
    filtered_df = filtered_df[filtered_df['title'].str.contains(title_filter, case=False, na=False)]
if date_filter:
    filtered_df = filtered_df[pd.to_datetime(filtered_df['date']).dt.date >= date_filter]

st.write(f"Showing {len(filtered_df)} of {len(df)} recordings.")
st.dataframe(filtered_df[['id', 'title', 'date', 'duration', 'download_url', 'transcript_url']])

# Show full metadata for a selected recording
st.subheader("Recording Details")
selected_id = st.selectbox("Select a recording ID", filtered_df['id'])
selected_row = filtered_df[filtered_df['id'] == selected_id].iloc[0]
st.json(selected_row['metadata'])

# --- Cline Memory Bank Feature ---
st.header("Cline Memory Bank 🧠")

def get_memory_bank():
    conn = psycopg2.connect(**DB_SETTINGS)
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM memory_bank ORDER BY created_at DESC;")
            rows = cur.fetchall()
            return pd.DataFrame(rows)
    finally:
        conn.close()

def add_memory_note(title, content):
    conn = psycopg2.connect(**DB_SETTINGS)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO memory_bank (title, content) VALUES (%s, %s);",
                (title, content)
            )
            conn.commit()
    finally:
        conn.close()

with st.form("Add Memory Note"):
    new_title = st.text_input("Title")
    new_content = st.text_area("Content")
    submitted = st.form_submit_button("Add Note")
    if submitted and new_title and new_content:
        add_memory_note(new_title, new_content)
        st.success("Note added!")

search_title = st.text_input("Search notes by title")
notes_df = get_memory_bank()
if search_title:
    notes_df = notes_df[notes_df['title'].str.contains(search_title, case=False, na=False)]

if notes_df.empty:
    st.info("No notes found in the memory bank.")
else:
    st.write(f"Showing {len(notes_df)} notes.")
    st.dataframe(notes_df[['id', 'title', 'created_at', 'content']]) 