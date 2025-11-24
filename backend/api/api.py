from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
import os
import sys
import time
import uuid
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Logging setup (must be before app instantiation for uvicorn loggers)
try:
    from logging_config import setup_logging, set_request_id, request_id_var
    setup_logging()
except Exception as _log_exc:  # Fail safe: print basic error, do not crash app
    print(f"Logging setup failed: {_log_exc}")
    import logging as _fallback_logging
    _fallback_logging.basicConfig(level=_fallback_logging.INFO)
    request_id_var = None  # minimal mode
    def set_request_id(_rid: str):
        pass

logger = logging.getLogger("app")

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
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    body = await request.body()
    logger.warning(
        "VALIDATION_ERROR path=%s method=%s errors=%s body_len=%d",
        request.url.path,
        request.method,
        exc.errors(),
        len(body) if body else 0,
    )
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body_received": body.decode(errors="ignore") if body else "",
            "help": "Check if Content-Type is 'application/json' and body is valid JSON"
        }
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Avoid full stack trace spam; concise origin info
    tb = exc.__traceback__
    last_tb = tb
    while last_tb and last_tb.tb_next:
        last_tb = last_tb.tb_next
    if last_tb:
        filename = os.path.basename(last_tb.tb_frame.f_code.co_filename)
        lineno = last_tb.tb_lineno
    else:
        filename = "-"
        lineno = -1
    logger.error(
        "UNHANDLED %s msg=%s file=%s line=%d path=%s method=%s",
        exc.__class__.__name__,
        str(exc),
        filename,
        lineno,
        request.url.path,
        request.method,
    )
    return JSONResponse(status_code=500, content={"detail": "Internal server error", "request_id": request_id_var.get() if request_id_var else "-"})


# Request logging middleware
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    rid = uuid.uuid4().hex[:8]
    set_request_id(rid)
    start = time.perf_counter()
    xff = request.headers.get("x-forwarded-for")
    client_ip = (xff.split(",")[0].strip() if xff else (request.client.host if request.client else "-"))
    user_agent = request.headers.get("user-agent", "-")
    logger.info(
        "REQ_START id=%s method=%s path=%s ip=%s ua=%s", rid, request.method, request.url.path, client_ip, user_agent
    )
    try:
        response = await call_next(request)
        # propagate request id for upstream correlation
        try:
            response.headers["X-Request-ID"] = rid
        except Exception:
            pass
        duration_ms = (time.perf_counter() - start) * 1000
        status = response.status_code
        slow_threshold = float(os.getenv("SLOW_REQ_THRESHOLD", "2000"))  # ms
        level_func = logger.info
        if status >= 500:
            level_func = logger.error
        elif status >= 400:
            level_func = logger.warning
        msg_prefix = "REQ_END"
        if duration_ms > slow_threshold:
            msg_prefix = "REQ_SLOW"
        level_func(
            "%s id=%s method=%s path=%s status=%d dur=%.1fms ip=%s", msg_prefix, rid, request.method, request.url.path, status, duration_ms, client_ip
        )
        return response
    except Exception as e:
        duration_ms = (time.perf_counter() - start) * 1000
        logger.error(
            "REQ_FAIL id=%s method=%s path=%s dur=%.1fms ip=%s err=%s", rid, request.method, request.url.path, duration_ms, client_ip, str(e)
        )
        raise


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
    t0 = time.perf_counter()
    try:
        logger.info("SEARCH start query='%s' k=%s", request.query, request.k)
        results = search_similar_documents(
            query=request.query,
            index_dir="data/index",
            k=request.k
        )
        logger.info("SEARCH done count=%d dur=%.1fms", len(results), (time.perf_counter() - t0) * 1000)
        return results
    except FileNotFoundError as e:
        logger.warning("SEARCH missing_index query='%s' err=%s", request.query, str(e))
        raise HTTPException(
            status_code=404,
            detail=f"Index fajlovi ne postoje. Prvo pokreni build_embeddings.py! Error: {str(e)}"
        )
    except Exception as e:
        logger.error("SEARCH fail query='%s' err=%s", request.query, str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Greška pri pretrazi: {str(e)}"
        )


@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    stage_t0 = time.perf_counter()
    try:
        logger.info("ANALYZE start query='%s' k=%s", request.query, request.k)
        # 1. Search
        t_search = time.perf_counter()
        search_results = search_similar_documents(
            query=request.query,
            index_dir="data/index",
            k=request.k
        )
        logger.info("ANALYZE search_done count=%d dur=%.1fms", len(search_results), (time.perf_counter() - t_search) * 1000)
        if not search_results:
            logger.info("ANALYZE no_results query='%s'", request.query)
            raise HTTPException(
                status_code=404,
                detail="No Reddit discussions found for this query"
            )
        # 2. Preprocessing import + run
        from embedding.preprocessing import preprocess_reddit_data
        t_prep = time.perf_counter()
        preprocessed = preprocess_reddit_data(search_results, request.query)
        logger.info(
            "ANALYZE preprocess_done enriched=%d dur=%.1fms",
            len(preprocessed.get('enriched_results', [])),
            (time.perf_counter() - t_prep) * 1000,
        )
        # 3. LLM analysis
        t_llm = time.perf_counter()
        analysis = analyze_with_grok(
            request.query,
            search_results,
            use_preprocessing=True
        )
        logger.info("ANALYZE llm_done dur=%.1fms", (time.perf_counter() - t_llm) * 1000)
        total_ms = (time.perf_counter() - stage_t0) * 1000
        logger.info("ANALYZE complete total=%.1fms", total_ms)
        return {
            "query": request.query,
            "num_discussions_analyzed": len(search_results),
            "enriched_results": preprocessed['enriched_results'],
            "aggregate_stats": preprocessed['aggregate_stats'],
            "analysis": analysis
        }
    except FileNotFoundError as e:
        logger.warning("ANALYZE missing_index query='%s' err=%s", request.query, str(e))
        raise HTTPException(
            status_code=404,
            detail=f"Index fajlovi ne postoje. Prvo pokreni build_embeddings.py! Error: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("ANALYZE fail query='%s' err=%s", request.query, str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Greška: {str(e)}"
        )


@app.post("/stats")
def stats(request: AnalyzeRequest):
    t0 = time.perf_counter()
    try:
        logger.info("STATS start query='%s' k=%s", request.query, request.k)
        search_results = search_similar_documents(
            query=request.query,
            index_dir="data/index",
            k=request.k
        )
        if not search_results:
            logger.info("STATS no_results query='%s'", request.query)
            raise HTTPException(
                status_code=404,
                detail="No Reddit discussions found"
            )
        statistics = extract_statistics(search_results)
        logger.info("STATS done dur=%.1fms", (time.perf_counter() - t0) * 1000)
        return {"query": request.query, "statistics": statistics}
    except FileNotFoundError as e:
        logger.warning("STATS missing_index query='%s' err=%s", request.query, str(e))
        raise HTTPException(
            status_code=404,
            detail=f"Index fajlovi ne postoje. Prvo pokreni build_embeddings.py! Error: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("STATS fail query='%s' err=%s", request.query, str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Greška: {str(e)}"
        )


@app.post("/full-analysis")
def full_analysis(request: SearchRequest):
    t0 = time.perf_counter()
    try:
        logger.info("FULL_ANALYSIS start query='%s' k=%s", request.query, request.k)
        search_results = search_similar_documents(
            query=request.query,
            index_dir="data/index",
            k=request.k
        )
        if not search_results:
            logger.info("FULL_ANALYSIS no_results query='%s'", request.query)
            raise HTTPException(status_code=404, detail="Nema rezultata")
        statistics = extract_statistics(search_results)
        llm_analysis = analyze_with_grok(request.query, search_results)
        logger.info(
            "FULL_ANALYSIS done count=%d dur=%.1fms",
            len(search_results),
            (time.perf_counter() - t0) * 1000,
        )
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error("FULL_ANALYSIS fail query='%s' err=%s", request.query, str(e))
        raise HTTPException(status_code=500, detail=f"Greška: {str(e)}")


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
    t0 = time.perf_counter()
    logger.info("HTML_ANALYZE start len_html=%d k=%s", len(request.html_content), request.k)
    result = analyze_html_endpoint(request.html_content, request.k)
    logger.info("HTML_ANALYZE done dur=%.1fms", (time.perf_counter() - t0) * 1000)
    return result


if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0", 
        port=8000,
        reload=True
    )
