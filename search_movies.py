from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models
from dotenv import load_dotenv
import os

load_dotenv()

client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))

encoder = SentenceTransformer("all-MiniLM-L6-v2")

collection_name = "day1_semantic_search"


def compare_search_results(query):
    """Compare search results across all chunking strategies"""
    print(f"Query: '{query}'\n")

    for strategy in ["fixed", "sentence", "paragraph"]:
        results = client.query_points(
            collection_name=collection_name,
            query=encoder.encode(query).tolist(),
            using=strategy,
            limit=3,
        )

        print(f"--- {strategy.upper()} CHUNKING ---")
        for i, point in enumerate(results.points, 1):
            print(f"{i}. {point.payload['title']}")
            print(f"   Score: {point.score:.3f}")
            print(f"   Chunk: {point.payload['chunk'][:80]}...")
        print()


# Test with movie-related queries
test_queries = [
    "a hero seeking revenge for the murder of his family",
    "time travel and its consequences on relationships",
    "psychological thriller with a plot twist ending",
]

for query in test_queries:
    compare_search_results(query)


# --- Chunking Strategy Analysis ---

def analyze_chunking_effectiveness():
    """Analyze which chunking strategy works best for your domain"""

    print("CHUNKING STRATEGY ANALYSIS")
    print("=" * 40)

    # Get chunk statistics for each strategy
    for strategy in ["fixed", "sentence", "paragraph"]:
        # Count chunks per strategy
        results = client.scroll(
            collection_name=collection_name,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="chunk_strategy", match=models.MatchValue(value=strategy)
                    )
                ]
            ),
            limit=100,
        )

        chunks = results[0]
        chunk_sizes = [len(chunk.payload["chunk"]) for chunk in chunks]

        print(f"\n{strategy.upper()} STRATEGY:")
        print(f"  Total chunks: {len(chunks)}")
        print(f"  Avg chunk size: {sum(chunk_sizes)/len(chunk_sizes):.0f} chars")
        print(f"  Size range: {min(chunk_sizes)}-{max(chunk_sizes)} chars")


analyze_chunking_effectiveness()
