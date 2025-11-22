from fastapi import HTTPException
from typing import Dict, Any
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from embedding.html_analyzer import analyze_html_page
from embedding.search_embeddings import search_similar_documents
from embedding.llm_analysis import analyze_with_grok
from embedding.preprocessing import preprocess_reddit_data


def analyze_html_endpoint(html_content: str, k: int = 20) -> Dict[str, Any]:
    try:
        # 1. HTML analiza
        html_analysis = analyze_html_page(html_content)
        search_query = html_analysis['search_query']

        # 2. Reddit search
        search_results = search_similar_documents(
            query=search_query,
            index_dir="data/index",
            k=k
        )

        # 3. Preprocess Reddit data (enrichment)
        if search_results:
            preprocessed = preprocess_reddit_data(search_results, search_query)
            enriched_results = preprocessed['enriched_results']
            aggregate_stats = preprocessed['aggregate_stats']
            
            # 4. Grok LLM analiza sa enrichment-om
            reddit_analysis = analyze_with_grok(
                search_query, 
                search_results,
                use_preprocessing=True
            )
        else:
            enriched_results = []
            aggregate_stats = {}
            reddit_analysis = {
                "scam_score": -1,
                "confidence": 0,
                "summary": "No similar Reddit discussions found",
                "red_flags": [],
                "green_flags": [],
                "key_points": [],
                "recommendation": "INVESTIGATE",
                "reasoning": "Insufficient Reddit data for comparison"
            }

        # 5. Combine analyses
        combined_result = _combine_analyses(
            html_analysis, 
            reddit_analysis, 
            enriched_results,
            aggregate_stats
        )
        
        return combined_result
    
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Index fajlovi ne postoje. Prvo pokreni build_embeddings.py! Error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Greška pri analizi HTML-a: {str(e)}"
        )


def _combine_analyses(
    html_analysis: Dict[str, Any], 
    reddit_analysis: Dict[str, Any], 
    enriched_results: list,
    aggregate_stats: Dict[str, Any]
) -> Dict[str, Any]:
    """Kombinuje HTML i Reddit analizu sa enrichment podacima"""
    
    html_score = html_analysis['llm_preliminary_analysis'].get('scam_score', 50)
    reddit_score = reddit_analysis.get('scam_score', 50)
    
    if reddit_score < 0:
        combined_score = html_score
        weight_info = "100% HTML analysis (no Reddit data)"
    else:
        combined_score = int(html_score * 0.6 + reddit_score * 0.4)
        weight_info = f"60% HTML (score={html_score}) + 40% Reddit (score={reddit_score})"
    
    combined_red_flags = list(set(
        html_analysis['algorithmic_analysis']['red_flags'] +
        html_analysis['llm_preliminary_analysis'].get('red_flags', []) +
        reddit_analysis.get('red_flags', [])
    ))
    
    combined_green_flags = list(set(
        html_analysis['algorithmic_analysis']['green_flags'] +
        html_analysis['llm_preliminary_analysis'].get('green_flags', []) +
        reddit_analysis.get('green_flags', [])
    ))
    
    recommendation = _get_recommendation(combined_score)
    
    return {
        "query": html_analysis['search_query'],
        "num_discussions_analyzed": len(enriched_results),
        
        # HTML ANALYSIS
        "html_analysis": {
            "company_info": html_analysis['company_info'],
            "extracted_data": html_analysis['extracted_data'],
            "algorithmic_score": html_analysis['algorithmic_analysis']['algorithmic_score'],
            "keyword_findings": {
                "red_flags": html_analysis['algorithmic_analysis']['red_flags'][:10],
                "green_flags": html_analysis['algorithmic_analysis']['green_flags'][:10]
            }
        },
        
        # REDDIT ANALYSIS (sa enrichment-om)
        "reddit_analysis": {
            "discussions_found": len(enriched_results) > 0,
            "enriched_results": enriched_results,
            "aggregate_stats": aggregate_stats,
            "llm_summary": reddit_analysis.get('summary', '')
        },
        
        # COMBINED VERDICT
        "combined_verdict": {
            "overall_scam_score": combined_score,
            "verdict": recommendation,
            "confidence": reddit_analysis.get('confidence', 70) / 100,
            "reasoning": f"Combined analysis ({weight_info}). {reddit_analysis.get('reasoning', '')}",
            "red_flags": combined_red_flags[:15],
            "green_flags": combined_green_flags[:15],
            "key_points": (
                html_analysis['llm_preliminary_analysis'].get('key_points', []) +
                reddit_analysis.get('key_points', [])
            )[:15],
            "breakdown": {
                "html_score": html_score,
                "reddit_score": reddit_score if reddit_score >= 0 else None,
                "weight_strategy": weight_info
            }
        }
    }


def _get_recommendation(score: int) -> str:
    """Određuje preporuku na osnovu scam score-a"""
    if score >= 75:
        return "AVOID"
    elif score >= 55:
        return "HIGH_CAUTION"
    elif score >= 35:
        return "INVESTIGATE"
    elif score >= 20:
        return "LOW_RISK"
    else:
        return "LIKELY_SAFE"


def _build_summary(html_analysis: Dict[str, Any], reddit_analysis: Dict[str, Any]) -> str:
    """Kreira sažetak koji kombinuje HTML i Reddit analizu"""
    html_summary = html_analysis['llm_preliminary_analysis'].get('summary', 'N/A')
    reddit_summary = reddit_analysis.get('summary', 'N/A')
    
    if reddit_summary == "No similar Reddit discussions found":
        return f"Website Analysis: {html_summary}"
    else:
        return f"Website: {html_summary} | Reddit Community: {reddit_summary}"
