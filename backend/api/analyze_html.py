from fastapi import HTTPException
from typing import Dict, Any
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from embedding.html_analyzer import (
    extract_text_from_html, 
    detect_scam_patterns, 
    extract_company_info,
    build_search_query
)
from embedding.search_embeddings import search_similar_documents
from embedding.preprocessing import preprocess_reddit_data
from embedding.llm_analysis import analyze_with_grok


def analyze_html_endpoint(html_content: str, k: int = 20) -> Dict[str, Any]:
    """
    Analizira HTML stranicu - IDENTIČAN output kao /analyze!
    
    Jedina razlika:
    1. Generiše query iz HTML-a (umesto da ga user šalje)
    2. Šalje HTML context Groku kao additional_context
    """
    try:
        # 1. Parse HTML i generiši search query
        extracted_data = extract_text_from_html(html_content)
        html_keywords = detect_scam_patterns(extracted_data)
        company_info = extract_company_info(extracted_data)
        search_query = build_search_query(extracted_data, company_info, html_keywords)
        
        # 2. ISTI PIPELINE KAO /analyze
        search_results = search_similar_documents(
            query=search_query,
            index_dir="data/index",
            k=k
        )
        
        if not search_results:
            raise HTTPException(
                status_code=404,
                detail="No Reddit discussions found for this query"
            )
        
        # 3. Preprocess Reddit data (enrichment)
        preprocessed = preprocess_reddit_data(search_results, search_query)
        
        # 4. Build HTML context za Grok (additional info)
        html_context = _build_html_context(extracted_data, html_keywords)
        
        # 5. Grok analysis sa HTML kontekstom
        analysis = analyze_with_grok(
            search_query, 
            search_results,
            use_preprocessing=True,
            additional_context=html_context  # Extra info iz HTML-a
        )
        
        # 6. IDENTIČAN OUTPUT KAO /analyze
        return {
            "query": search_query,  # Generisan iz HTML-a
            "num_discussions_analyzed": len(search_results),
            "enriched_results": preprocessed['enriched_results'],
            "aggregate_stats": preprocessed['aggregate_stats'],
            "analysis": analysis  # Isti format kao /analyze
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


def _build_html_context(extracted_data: Dict[str, Any], html_keywords: Dict[str, Any]) -> str:
    """
    Kreira dodatni kontekst iz HTML-a za Grok LLM.
    Ovo se dodaje uz Reddit diskusije.
    
    LIMITIRAN na ~500 tokena (~2000 chars) da ne preoptereti context.
    """
    context = "\n" + "="*80 + "\n"
    context += "ADDITIONAL CONTEXT FROM WEBSITE HTML:\n"
    context += "="*80 + "\n\n"
    
    # Page info (skraćeno)
    title = extracted_data.get('title', 'N/A')
    if len(title) > 100:
        title = title[:100] + "..."
    
    description = extracted_data.get('description', 'N/A')
    if len(description) > 150:
        description = description[:150] + "..."
    
    context += f"Website Title: {title}\n"
    context += f"Meta Description: {description}\n\n"
    
    # Main headings (TOP 5, skraćeno)
    headings = extracted_data.get('headings', [])
    if headings:
        truncated_headings = [h[:50] for h in headings[:5]]  # Max 50 chars svaki
        context += f"Main Headings: {', '.join(truncated_headings)}\n\n"
    
    # HTML keyword findings - TOP 8 red flags (ne 10)
    red_flags = html_keywords.get('red_flags', [])
    if red_flags:
        context += f"WEBSITE RED FLAGS DETECTED ({len(red_flags)} total):\n"
        for flag in red_flags[:8]:  # Top 8 (ne 10)
            context += f"  • {flag}\n"
        context += "\n"
    
    # Green flags - TOP 5 (ne 10)
    green_flags = html_keywords.get('green_flags', [])
    if green_flags:
        context += f"WEBSITE TRUST SIGNALS ({len(green_flags)} total):\n"
        for flag in green_flags[:5]:  # Top 5 (ne 10)
            context += f"  • {flag}\n"
        context += "\n"
    
    context += f"HTML Algorithmic Score: {html_keywords.get('algorithmic_score', 0)}/100\n"
    context += "="*80 + "\n\n"
    
    # Safety check - max 2500 chars (~625 tokena)
    if len(context) > 2500:
        context = context[:2500] + "\n[Context truncated due to length]\n"
    
    return context