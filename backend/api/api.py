from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from embedding.search_embeddings import search_similar_documents
from embedding.llm_analysis import analyze_with_grok
from calculate_stats import extract_statistics
from analyze_html import analyze_html_endpoint

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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"❌ VALIDATION ERROR:")
    print(f"   URL: {request.url}")
    print(f"   Method: {request.method}")
    print(f"   Errors: {exc.errors()}")
    print(f"   Body: {await request.body()}")
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body_received": str(await request.body()),
            "help": "Check if Content-Type is 'application/json' and body is valid JSON"
        }
    )


class SearchRequest(BaseModel):
    query: str
    k: Optional[int] = 20 
    
    class Config:
        extra = "ignore"  # Ignoriši extra fields
        json_schema_extra = {
            "example": {
                "query": "is this crypto investment a scam?",
                "k": 20
            }
        }


class AnalyzeRequest(BaseModel):
    query: str
    k: Optional[int] = 20
    
    class Config:
        extra = "ignore"  # Ignoriši extra fields iz frontend-a
        json_schema_extra = {
            "example": {
                "query": "is this crypto investment a scam?",
                "k": 20
            }
        }


class HtmlAnalyzeRequest(BaseModel):
    html_content: str
    k: Optional[int] = 20
    
    class Config:
        extra = "ignore"  # Ignoriši extra fields
        json_schema_extra = {
            "example": {
                "html_content": "<html><body><h1>Amazing Investment Opportunity!</h1></body></html>",
                "k": 20
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
            "/search": "POST - semantic search (returns raw results)",
            "/analyze": "POST - complete analysis (search + enrichment + LLM)",
            "/analyze-html": "POST - analyze HTML page for scam indicators",
            "/stats": "POST - extract statistics (search + stats)",
            "/full-analysis": "POST - legacy endpoint (use /analyze instead)",
            "/health": "GET - health check",
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
        # 1. Interno radi search (ne zahteva search_results)
        search_results = search_similar_documents(
            query=request.query,
            index_dir="data/index",
            k=request.k
        )
        
        if not search_results:
            raise HTTPException(
                status_code=404,
                detail="No Reddit discussions found for this query"
            )
        
        # 2. Import preprocessing
        from embedding.preprocessing import preprocess_reddit_data
        
        # 3. Preprocess Reddit data (enrichment)
        preprocessed = preprocess_reddit_data(search_results, request.query)
        
        # 4. Grok analysis sa enrichment-om
        analysis = analyze_with_grok(
            request.query, 
            search_results,
            use_preprocessing=True
        )
        
        return {
            "query": request.query,
            "num_discussions_analyzed": len(search_results),
            "enriched_results": preprocessed['enriched_results'],
            "aggregate_stats": preprocessed['aggregate_stats'],
            "analysis": analysis
        }
    
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Index fajlovi ne postoje. Prvo pokreni build_embeddings.py! Error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Greška: {str(e)}"
        )


@app.post("/stats")
def stats(request: AnalyzeRequest):
    try:
        # Interno radi search
        search_results = search_similar_documents(
            query=request.query,
            index_dir="data/index",
            k=request.k
        )
        
        if not search_results:
            raise HTTPException(
                status_code=404,
                detail="No Reddit discussions found"
            )
        
        statistics = extract_statistics(search_results)
        
        return {
            "query": request.query,
            "statistics": statistics
        }
    
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Index fajlovi ne postoje. Prvo pokreni build_embeddings.py! Error: {str(e)}"
        )
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


@app.post("/analyze-html")
def analyze_html(request: HtmlAnalyzeRequest):
    return analyze_html_endpoint(request.html_content, request.k)


if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0", 
        port=8000,
        reload=True
    )
