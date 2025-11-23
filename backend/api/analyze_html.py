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
    Analizira HTML stranicu - ISTI PIPELINE kao /analyze!
    
    Razlika:
    1. Kreira OPTIMIZOVAN query iz HTML-a (ekstraktuje domain, title, keywords)
    2. Koristi ISTI pipeline kao /analyze - BEZ dodatnog HTML context-a
    3. Vraća metadata iz HTML-a (extracted_info) kao dodatnu informaciju
    """
    try:
        # 1. Parse HTML i generiši OPTIMIZOVAN search query
        extracted_data = extract_text_from_html(html_content)
        html_keywords = detect_scam_patterns(extracted_data)
        company_info = extract_company_info(extracted_data)
        search_query = build_search_query(extracted_data, company_info, html_keywords)
        
        # 2. ISTI PIPELINE KAO /analyze - Reddit search
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
        
        # 4. Grok analysis - ISTI KAO /analyze (bez HTML context-a!)
        analysis = analyze_with_grok(
            search_query, 
            search_results,
            use_preprocessing=True,
            additional_context=None  # NE šaljemo HTML context
        )
        
        # 5. OUTPUT - ISTI kao /analyze + dodatni HTML metadata
        return {
            "query": search_query,  # Generisan iz HTML-a
            "num_discussions_analyzed": len(search_results),
            "enriched_results": preprocessed['enriched_results'],
            "aggregate_stats": preprocessed['aggregate_stats'],
            "analysis": analysis,  # Isti format kao /analyze
            "extracted_info": {  # BONUS: HTML metadata
                "title": extracted_data.get('title', ''),
                "description": extracted_data.get('description', ''),
                "company_name": company_info.get('company_name', ''),
                "algorithmic_score": html_keywords.get('algorithmic_score', 0),
                "critical_flags_count": len([f for f in html_keywords.get('red_flags', []) if '🚨 CRITICAL' in f]),
                "trust_signals_count": len(html_keywords.get('green_flags', []))
            }
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
    
    VAŽNO: Ako Reddit pokazuje da je ovo LEGITIMNA kompanija (mali scam_score, 
    visok positive_vouches), HTML context treba biti MINIMAL i pozitivan.
    """
    # Proveri šta Reddit kaže - da li je ovo poznata legit kompanija?
    scam_mentions = reddit_stats.get('scam_indicators', {}).get('total_scam_mentions', 0)
    positive_vouches = reddit_stats.get('scam_indicators', {}).get('total_positive_vouches', 0)
    scam_ratio = reddit_stats.get('scam_indicators', {}).get('scam_to_positive_ratio', 0)
    num_discussions = reddit_stats.get('total_discussions', 0)
    
    # Detektuj POZNATE LEGITIMNE kompanije
    title_lower = extracted_data.get('title', '').lower()
    known_legit_keywords = ['amazon', 'google', 'microsoft', 'facebook', 'apple', 
                            'ebay', 'paypal', 'netflix', 'spotify', 'adobe',
                            'linkedin', 'instagram', 'twitter', 'youtube', 'reddit',
                            'walmart', 'target', 'bestbuy', 'github', 'stackoverflow']
    
    is_known_company = any(keyword in title_lower for keyword in known_legit_keywords)
    is_likely_legit = (positive_vouches >= 5 and scam_ratio < 0.5) or (positive_vouches >= 10 and scam_mentions <= 2)
    
    context = "\n" + "="*80 + "\n"
    
    # Ako je poznata kompanija ILI Reddit pokazuje legitimnost - KRATAK pozitivan kontekst
    if is_known_company or is_likely_legit:
        context += "WEBSITE CONTEXT (well-known/verified company):\n"
        context += "="*80 + "\n\n"
        
        title = extracted_data.get('title', 'N/A')
        if len(title) > 100:
            title = title[:100] + "..."
        
        context += f"Website: {title}\n"
        
        # Samo trust signals, bez red flags
        green_flags = html_keywords.get('green_flags', [])
        if green_flags:
            context += f"\nTrust Signals Found: {len(green_flags)}\n"
            for flag in green_flags[:4]:
                clean_flag = flag.replace('✅ TRUST: ', '')
                context += f"  • {clean_flag}\n"
        
        context += f"\n⚠️ NOTE: This appears to be a well-known legitimate company.\n"
        context += f"Reddit shows {positive_vouches} positive vouches, {scam_mentions} scam mentions.\n"
        context += f"Prioritize Reddit community consensus over technical details.\n"
        context += "="*80 + "\n\n"
        return context
    
    # Za nepoznate/sumnjive sajtove - PUNI HTML kontekst
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
    
    # Main headings
    headings = extracted_data.get('headings', [])
    if headings:
        truncated_headings = [h[:60] for h in headings[:6]]
        context += f"Page Headings: {', '.join(truncated_headings)}\n\n"
    
    # SVE red flags (critical + high risk + suspicious)
    red_flags = html_keywords.get('red_flags', [])
    if red_flags:
        context += f"Website Warning Signs ({len(red_flags)} detected):\n"
        for flag in red_flags[:10]:
            clean_flag = flag.replace('🚨 CRITICAL: ', '').replace('⚠️ HIGH RISK: ', '').replace('⚠️ SUSPICIOUS: ', '')
            context += f"  • {clean_flag}\n"
        context += "\n"
    
    # SVE green flags
    green_flags = html_keywords.get('green_flags', [])
    if green_flags:
        context += f"Website Trust Signals ({len(green_flags)} found):\n"
        for flag in green_flags[:8]:
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