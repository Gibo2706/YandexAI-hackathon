from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from embedding.search_embeddings import search_similar_documents
from embedding.llm_analysis import analyze_with_grok
from calculate_stats import extract_statistics

app = FastAPI(
    title="Reddit Embeddings Search API",
    description="Semantic search preko Reddit diskusija",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    query: str
    k: Optional[int] = 20 
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "is this crypto investment a scam?",
                "k": 20
            }
        }


class AnalyzeRequest(BaseModel):
    search_results: List[Dict[str, Any]]
    query: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "is this crypto investment a scam?",
                "search_results": []
            }
        }


class SearchResult(BaseModel):
    similarity_score: float
    submission_id: Optional[str]
    subreddit: Optional[str]
    title: Optional[str]
    score: Optional[int]
    num_comments: Optional[int]
    full_doc: dict  


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Reddit Embeddings Search API",
        "endpoints": {
            "/search": "POST - semantic search",
            "/docs": "Swagger UI dokumentacija"
        }
    }


@app.post("/search", response_model=list[SearchResult])
def search(request: SearchRequest):
    try:
        results = search_similar_documents(
            query=request.query,
            index_dir="data/index",
            k=request.k
        )
        return results
    
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Index fajlovi ne postoje. Prvo pokreni build_embeddings.py! Error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Greška pri pretrazi: {str(e)}"
        )


@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    try:
        if not request.search_results:
            raise HTTPException(
                status_code=400,
                detail="Nema search_results - prvo pozovi /search"
            )
        
        analysis = analyze_with_grok(request.query, request.search_results)
        
        return {
            "query": request.query,
            "num_discussions_analyzed": len(request.search_results),
            "analysis": analysis
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Greška: {str(e)}"
        )


@app.post("/stats")
def stats(request: AnalyzeRequest):
    try:
        if not request.search_results:
            raise HTTPException(
                status_code=400,
                detail="Nema search_results - prvo pozovi /search"
            )
        
        statistics = extract_statistics(request.search_results)
        
        return {
            "query": request.query,
            "statistics": statistics
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Greška: {str(e)}"
        )


@app.post("/full-analysis")
def full_analysis(request: SearchRequest):
    try:
        search_results = search_similar_documents(
            query=request.query,
            index_dir="data/index",
            k=request.k
        )
        
        if not search_results:
            raise HTTPException(
                status_code=404,
                detail="Nema rezultata"
            )
        
        statistics = extract_statistics(search_results)
        
        llm_analysis = analyze_with_grok(request.query, search_results)
        
        return {
            "query": request.query,
            "search_results": search_results,
            "statistics": statistics,
            "llm_analysis": llm_analysis,
            "metadata": {
                "num_discussions": len(search_results),
                "avg_similarity": statistics.get("avg_similarity", 0),
                "timestamp": "2025-11-22"
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Greška: {str(e)}"
        )


@app.get("/health")
def health():
    
    index_exists = os.path.exists("data/index/embeddings.index")
    metadata_exists = os.path.exists("data/index/metadata.pkl")
    groq_key_exists = bool(os.getenv("GROQ_API_KEY"))
    
    return {
        "status": "healthy" if (index_exists and metadata_exists and groq_key_exists) else "degraded",
        "index_ready": index_exists and metadata_exists,
        "groq_ready": groq_key_exists,
        "files": {
            "embeddings.index": index_exists,
            "metadata.pkl": metadata_exists
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0", 
        port=8000,
        reload=True
    )
