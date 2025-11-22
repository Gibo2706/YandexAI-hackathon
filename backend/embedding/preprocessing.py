
from typing import Dict, Any, List
from .reddit_enrichment import enrich_all_discussions, extract_scam_mentions
from .scam_keywords import get_category_matches, SEVERITY_WEIGHTS


def analyze_with_advanced_keywords(text: str) -> Dict[str, Any]:
    """
    Analizira tekst kroz advanced keyword categories.
    """
    matches = get_category_matches(text)
    
    # Calculate weighted score
    score = 0
    detailed_findings = []
    
    # Financial scams (critical weight)
    for category, keywords in matches['financial_scams'].items():
        if keywords:
            score += SEVERITY_WEIGHTS['critical'] * len(keywords)
            detailed_findings.append({
                "category": f"FINANCIAL_SCAM: {category}",
                "severity": "critical",
                "keywords": keywords,
                "weight": SEVERITY_WEIGHTS['critical']
            })
    
    # E-commerce scams (high weight)
    for category, keywords in matches['ecommerce_scams'].items():
        if keywords:
            score += SEVERITY_WEIGHTS['high'] * len(keywords)
            detailed_findings.append({
                "category": f"ECOMMERCE_SCAM: {category}",
                "severity": "high",
                "keywords": keywords,
                "weight": SEVERITY_WEIGHTS['high']
            })
    
    # Employment scams (high weight)
    for category, keywords in matches['employment_scams'].items():
        if keywords:
            score += SEVERITY_WEIGHTS['high'] * len(keywords)
            detailed_findings.append({
                "category": f"EMPLOYMENT_SCAM: {category}",
                "severity": "high",
                "keywords": keywords,
                "weight": SEVERITY_WEIGHTS['high']
            })
    
    # Pressure tactics (medium weight)
    for category, keywords in matches['pressure_tactics'].items():
        if keywords:
            score += SEVERITY_WEIGHTS['medium'] * len(keywords)
            detailed_findings.append({
                "category": f"PRESSURE_TACTIC: {category}",
                "severity": "medium",
                "keywords": keywords,
                "weight": SEVERITY_WEIGHTS['medium']
            })
    
    # Linguistic flags (medium weight)
    for category, keywords in matches['linguistic_flags'].items():
        if keywords:
            score += SEVERITY_WEIGHTS['medium'] * len(keywords)
            detailed_findings.append({
                "category": f"LINGUISTIC_FLAG: {category}",
                "severity": "medium",
                "keywords": keywords,
                "weight": SEVERITY_WEIGHTS['medium']
            })
    
    # Trust signals (negative weight - reduces score)
    for category, keywords in matches['trust_signals'].items():
        if keywords:
            score += SEVERITY_WEIGHTS['trust_major'] * len(keywords)
            detailed_findings.append({
                "category": f"TRUST_SIGNAL: {category}",
                "severity": "positive",
                "keywords": keywords,
                "weight": SEVERITY_WEIGHTS['trust_major']
            })
    
    return {
        "keyword_score": max(0, min(100, score)),
        "total_red_flags": sum(len(kws) for cat in [matches['financial_scams'], matches['ecommerce_scams'], 
                                                      matches['employment_scams'], matches['pressure_tactics'], 
                                                      matches['linguistic_flags']] 
                               for kws in cat.values()),
        "total_green_flags": sum(len(kws) for kws in matches['trust_signals'].values()),
        "detailed_findings": detailed_findings,
        "category_matches": matches
    }


def preprocess_reddit_data(search_results: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
    """
    Kompletno pre-procesiranje Reddit podataka pre LLM analize.
    
    Steps:
    1. Enrich discussions (user credibility, thread analysis, scam mentions)
    2. Advanced keyword matching
    3. URL analysis (ako ima linkova)
    4. Aggregate statistics
    """
    if not search_results:
        return {
            "enriched_results": [],
            "aggregate_stats": {},
            "preprocessing_summary": "No Reddit data to process"
        }
    
    # STEP 1: Enrich all discussions
    enriched_results = enrich_all_discussions(search_results)
    
    # STEP 2: Advanced keyword analysis na celom text corpus-u
    all_text = ""
    for result in enriched_results:
        full_doc = result.get('full_doc', {})
        post = full_doc.get('post', {})
        comments = full_doc.get('comments', [])
        
        all_text += f"{post.get('title', '')} {post.get('text', '')} "
        all_text += ' '.join([c.get('text', '') for c in comments])
    
    keyword_analysis = analyze_with_advanced_keywords(all_text)
    
    # STEP 3: Aggregate statistics
    avg_discussion_credibility = sum(r['enrichment']['discussion_credibility'] for r in enriched_results) / len(enriched_results)
    avg_post_quality = sum(r['enrichment']['post_quality']['quality_score'] for r in enriched_results) / len(enriched_results)
    
    total_scam_mentions = sum(r['enrichment']['scam_analysis']['scam_mention_count'] for r in enriched_results)
    total_warnings = sum(r['enrichment']['scam_analysis']['warning_count'] for r in enriched_results)
    total_positive_vouches = sum(r['enrichment']['scam_analysis']['positive_count'] for r in enriched_results)
    
    # Consensus detection
    consensus_levels = [r['enrichment']['thread_analysis']['consensus_level'] for r in enriched_results]
    strong_agreement_count = consensus_levels.count('strong_agreement')
    controversial_count = consensus_levels.count('controversial')
    
    if strong_agreement_count > len(enriched_results) * 0.6:
        overall_consensus = "strong_community_agreement"
    elif controversial_count > len(enriched_results) * 0.4:
        overall_consensus = "highly_controversial"
    else:
        overall_consensus = "mixed_opinions"
    
    aggregate_stats = {
        "total_discussions": len(enriched_results),
        "avg_discussion_credibility": round(avg_discussion_credibility, 2),
        "avg_post_quality": round(avg_post_quality, 2),
        "scam_indicators": {
            "total_scam_mentions": total_scam_mentions,
            "total_warnings": total_warnings,
            "total_positive_vouches": total_positive_vouches,
            "scam_to_positive_ratio": round(total_scam_mentions / max(total_positive_vouches, 1), 2)
        },
        "consensus": {
            "overall": overall_consensus,
            "strong_agreement": strong_agreement_count,
            "controversial": controversial_count
        },
        "keyword_analysis": {
            "total_red_flags": keyword_analysis['total_red_flags'],
            "total_green_flags": keyword_analysis['total_green_flags'],
            "keyword_score": keyword_analysis['keyword_score']
        }
    }
    
    return {
        "enriched_results": enriched_results,
        "aggregate_stats": aggregate_stats,
        "keyword_analysis": keyword_analysis,
        "preprocessing_summary": f"Processed {len(enriched_results)} discussions with {total_scam_mentions} scam mentions"
    }


def build_enriched_context_for_llm(query: str, preprocessed_data: Dict[str, Any]) -> str:
    """
    Kreira obogaćeni kontekst za Grok LLM sa svim pre-procesiranim podacima.
    """
    enriched_results = preprocessed_data['enriched_results']
    aggregate_stats = preprocessed_data['aggregate_stats']
    keyword_analysis = preprocessed_data['keyword_analysis']
    
    context = f"USER QUERY: {query}\n\n"
    context += "="*80 + "\n"
    context += "PREPROCESSED ANALYSIS SUMMARY\n"
    context += "="*80 + "\n\n"
    
    # Aggregate statistics
    context += f" AGGREGATE STATISTICS:\n"
    context += f"  • Total Discussions Analyzed: {aggregate_stats['total_discussions']}\n"
    context += f"  • Average Discussion Credibility: {aggregate_stats['avg_discussion_credibility']}/100\n"
    context += f"  • Average Post Quality: {aggregate_stats['avg_post_quality']}/100\n"
    context += f"  • Community Consensus: {aggregate_stats['consensus']['overall']}\n\n"
    
    # Scam indicators
    scam = aggregate_stats['scam_indicators']
    context += f" SCAM INDICATORS:\n"
    context += f"  • Direct Scam Mentions: {scam['total_scam_mentions']}\n"
    context += f"  • Warning Phrases: {scam['total_warnings']}\n"
    context += f"  • Positive Vouches: {scam['total_positive_vouches']}\n"
    context += f"  • Scam/Positive Ratio: {scam['scam_to_positive_ratio']} (higher = more scam mentions)\n\n"
    
    # Keyword analysis
    kw = aggregate_stats['keyword_analysis']
    context += f" ADVANCED KEYWORD DETECTION:\n"
    context += f"  • Red Flags Found: {kw['total_red_flags']}\n"
    context += f"  • Trust Signals Found: {kw['total_green_flags']}\n"
    context += f"  • Keyword Risk Score: {kw['keyword_score']}/100\n\n"
    
    # Top keyword findings
    if keyword_analysis['detailed_findings']:
        context += f" TOP KEYWORD FINDINGS:\n"
        for finding in keyword_analysis['detailed_findings'][:10]:
            severity_emoji = "🚨" if finding['severity'] == "critical" else "⚠️" if finding['severity'] == "high" else "✅"
            context += f"  {severity_emoji} {finding['category']}: {', '.join(finding['keywords'][:3])}\n"
        context += "\n"
    
    context += "="*80 + "\n"
    context += "REDDIT DISCUSSIONS (ENRICHED)\n"
    context += "="*80 + "\n\n"
    
    # Individual discussions with enrichment
    for i, result in enumerate(enriched_results, 1):
        similarity = result.get('similarity_score', 0)
        subreddit = result.get('subreddit', 'unknown')
        enrichment = result['enrichment']
        full_doc = result.get('full_doc', {})
        post = full_doc.get('post', {})
        
        context += f"--- DISCUSSION {i} ---\n"
        context += f"Similarity: {similarity:.3f} | Subreddit: r/{subreddit}\n"
        context += f"Discussion Credibility: {enrichment['discussion_credibility']}/100\n"
        context += f"Post Quality: {enrichment['post_quality']['quality_score']}/100 ({', '.join(enrichment['post_quality']['indicators'][:2])})\n"
        context += f"Thread Consensus: {enrichment['thread_analysis']['consensus_level']}\n"
        context += f"Scam Mentions: {enrichment['scam_analysis']['scam_mention_count']} | Warnings: {enrichment['scam_analysis']['warning_count']}\n\n"
        
        # Post content (skraćeno)
        context += f"POST: {post.get('title', '')}\n"
        if post.get('text'):
            context += f"{post['text'][:300]}...\n\n"
        
        # Top comments (samo najkvalitetniji)
        top_contributors = enrichment['thread_analysis']['top_contributors'][:2]
        if top_contributors:
            context += f"TOP COMMENTS:\n"
            for contrib in top_contributors:
                context += f"  • [{contrib['author']}] (↑{contrib['score']}): {contrib['text_preview']}\n"
        
        context += "\n"
    
    return context


def preprocess_for_analysis(query: str, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Main funkcija: kompletno pre-procesiranje za LLM analizu.
    
    Returns:
        Dict sa preprocessed_data i enriched_context za LLM
    """
    preprocessed_data = preprocess_reddit_data(search_results, query)
    enriched_context = build_enriched_context_for_llm(query, preprocessed_data)
    
    return {
        "preprocessed_data": preprocessed_data,
        "enriched_context": enriched_context,
        "context_length": len(enriched_context),
        "estimated_tokens": len(enriched_context) // 4
    }
