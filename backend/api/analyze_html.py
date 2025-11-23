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
        html_context = _build_html_context(extracted_data, html_keywords, preprocessed['aggregate_stats'])
        
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


def _build_html_context(extracted_data: Dict[str, Any], html_keywords: Dict[str, Any], reddit_stats: Dict[str, Any]) -> str:
    """
    Kreira dodatni kontekst iz HTML-a za Grok LLM.
    Ovo se dodaje uz Reddit diskusije kao DODATNI KONTEKST.
    """
    context = "\n" + "="*80 + "\n"
    context += "SUPPLEMENTARY WEBSITE INFO (context for analysis):\n"
    context += "="*80 + "\n\n"
    
    # Page info
    title = extracted_data.get('title', 'N/A')
    if len(title) > 100:
        title = title[:100] + "..."
    
    description = extracted_data.get('description', 'N/A')
    if len(description) > 150:
        description = description[:150] + "..."
    
    context += f"Website: {title}\n"
    if description != 'N/A':
        context += f"Description: {description}\n"
    context += "\n"
    
    # Main headings - pokazuje content structure
    headings = extracted_data.get('headings', [])
    if headings:
        truncated_headings = [h[:60] for h in headings[:6]]  # Top 6
        context += f"Page Headings: {', '.join(truncated_headings)}\n\n"
    
    # SVE red flags (critical + high risk + suspicious)
    red_flags = html_keywords.get('red_flags', [])
    if red_flags:
        context += f"Website Warning Signs ({len(red_flags)} detected):\n"
        for flag in red_flags[:10]:  # Top 10
            clean_flag = flag.replace('🚨 CRITICAL: ', '').replace('⚠️ HIGH RISK: ', '').replace('⚠️ SUSPICIOUS: ', '')
            context += f"  • {clean_flag}\n"
        context += "\n"
    
    # SVE green flags
    green_flags = html_keywords.get('green_flags', [])
    if green_flags:
        context += f"Website Trust Signals ({len(green_flags)} found):\n"
        for flag in green_flags[:8]:  # Top 8
            clean_flag = flag.replace('✅ TRUST: ', '')
            context += f"  • {clean_flag}\n"
        context += "\n"
    
    # Algorithmic score
    algo_score = html_keywords.get('algorithmic_score', 0)
    context += f"Technical Analysis Score: {algo_score}/100\n\n"
    
    context += "="*80 + "\n\n"
    
    # Safety check - max 3000 chars
    if len(context) > 3000:
        context = context[:3000] + "\n[Truncated]\n"
    
    return context