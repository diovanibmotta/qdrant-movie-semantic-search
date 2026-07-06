import json
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models
from dotenv import load_dotenv
import os

load_dotenv()

client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))

encoder = SentenceTransformer("all-MiniLM-L6-v2")

with open("movies.json", "r", encoding="utf-8") as f:
    movies_dataset = json.load(f)


# --- Chunking Strategies ---

def fixed_size_chunks(text, chunk_size=100, overlap=20):
    """Split text into fixed-size chunks with overlap"""
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i:i + chunk_size]
        if chunk_words:  # Only add non-empty chunks
            chunks.append(' '.join(chunk_words))

    return chunks


def sentence_chunks(text, max_sentences=3):
    """Group sentences into chunks"""
    import re
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    chunks = []
    for i in range(0, len(sentences), max_sentences):
        chunk_sentences = sentences[i:i + max_sentences]
        if chunk_sentences:
            chunks.append('. '.join(chunk_sentences) + '.')

    return chunks


def paragraph_chunks(text):
    """Split by paragraphs or double line breaks"""
    chunks = [chunk.strip() for chunk in text.split('\n\n') if chunk.strip()]
    return chunks if chunks else [text]  # Fallback to full text


# --- Create Collection and Process Data ---

collection_name = "day1_semantic_search"

if client.collection_exists(collection_name=collection_name):
    client.delete_collection(collection_name=collection_name)

# Create a collection with three named vectors
client.create_collection(
    collection_name=collection_name,
    vectors_config={
        "fixed": models.VectorParams(size=384, distance=models.Distance.COSINE),
        "sentence": models.VectorParams(size=384, distance=models.Distance.COSINE),
        "paragraph": models.VectorParams(size=384, distance=models.Distance.COSINE),
    },
)

# Index fields for filtering (more on this on day 2)
client.create_payload_index(
    collection_name=collection_name,
    field_name="chunk_strategy",
    field_schema=models.PayloadSchemaType.KEYWORD,
)

# Process and upload data
points = []
point_id = 0

for item in movies_dataset:
    synopsis = item["synopsis"]

    # Process with each chunking strategy
    strategies = {
        "fixed": fixed_size_chunks(synopsis),
        "sentence": sentence_chunks(synopsis),
        "paragraph": paragraph_chunks(synopsis),
    }

    for strategy_name, chunks in strategies.items():
        for chunk_idx, chunk in enumerate(chunks):
            # Create vectors for this chunk
            vectors = {strategy_name: encoder.encode(chunk).tolist()}

            points.append(
                models.PointStruct(
                    id=point_id,
                    vector=vectors,
                    payload={
                        **item,  # Include all original metadata
                        "chunk": chunk,
                        "chunk_strategy": strategy_name,
                        "chunk_index": chunk_idx,
                    },
                )
            )
            point_id += 1

client.upload_points(collection_name=collection_name, points=points)
print(f"Uploaded {len(points)} chunks across three strategies")
