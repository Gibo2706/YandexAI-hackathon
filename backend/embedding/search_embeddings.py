import pickle
import numpy as np
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

EMBEDDING_MODEL = "text-embedding-3-large"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

_INDEX_CACHE = {}
_METADATA_CACHE = {}


def load_index_and_metadata(index_dir="data/index"):
    global _INDEX_CACHE, _METADATA_CACHE
    
    if index_dir in _INDEX_CACHE:
        return _INDEX_CACHE[index_dir], _METADATA_CACHE[index_dir]
    
    try:
        import faiss
        index = faiss.read_index(f"{index_dir}/embeddings.index")
    except ImportError:
        raise ImportError("FAISS nije instaliran. Instaliraj: pip install faiss-cpu")
    except FileNotFoundError:
        raise FileNotFoundError(f"Index fajl ne postoji: {index_dir}/embeddings.index")
    
    with open(f"{index_dir}/metadata.pkl", "rb") as f:
        metadata = pickle.load(f)
    
    _INDEX_CACHE[index_dir] = index
    _METADATA_CACHE[index_dir] = metadata
    
    return index, metadata


def get_embedding(text):
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return np.array(response.data[0].embedding, dtype=np.float32)


def search_similar_documents(query, index_dir="data/index", k=20):

    index, metadata = load_index_and_metadata(index_dir)
    
    query_emb = get_embedding(query)
    query_emb = query_emb.reshape(1, -1)
    
    import faiss
    faiss.normalize_L2(query_emb)
    
    scores, indices = index.search(query_emb, k)
    
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < len(metadata) and idx >= 0:
            meta = metadata[idx]
            result = {
                "similarity_score": float(score),
                "full_doc": meta["full_doc"],
                "submission_id": meta.get("submission_id"),
                "subreddit": meta.get("subreddit"),
                "title": meta.get("title"),
                "score": meta.get("score"),
                "num_comments": meta.get("num_comments")
            }
            results.append(result)
    
    return results


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print(" OPENAI_API_KEY nije postavljen!")
        exit(1)
    
    query = "is this crypto investment a scam?"
    results = search_similar_documents(query, index_dir="data/index", k=20)
    
    print(f"Pronađeno {len(results)} rezultata")
    for i, r in enumerate(results[:3], 1):
        print(f"{i}. [{r['similarity_score']:.3f}] r/{r['subreddit']} - {r['title'][:60]}...")
