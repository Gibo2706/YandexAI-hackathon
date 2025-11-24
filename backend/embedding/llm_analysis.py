import os
import json
from openai import OpenAI
from typing import List, Dict, Any
from dotenv import load_dotenv
from .preprocessing import preprocess_for_analysis

load_dotenv()

# OpenAI client and model configuration
# NOTE: We keep function name analyze_with_grok for backward compatibility, but it now uses OpenAI.
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")


def truncate_text(text: str, max_chars: int = 500) -> str:
    """Skraćuje tekst na max_chars karaktera"""
    if not text or len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."


def build_thread_structure(doc: Dict[str, Any], max_comments: int = None) -> str:
    post = doc.get("post", {})
    comments = doc.get("comments", [])
    
    # Skrati post tekst
    thread_text = f"POST [{post.get('id')}] (↑{post.get('score', 0)}, 💬{post.get('num_comments', 0)}):\n"
    thread_text += f"Title: {truncate_text(post.get('title', 'N/A'), 200)}\n"
    if post.get('text'):
        thread_text += f"Text: {truncate_text(post.get('text'), 400)}\n"
    thread_text += "\n"
    
    top_level = []  
    replies = {} 
    
    for comment in comments:
        parent_id = comment.get('parent_id')
        if parent_id == post.get('id'):
            top_level.append(comment)
        else:
            if parent_id not in replies:
                replies[parent_id] = []
            replies[parent_id].append(comment)
    
    # Sortiraj komentare po score-u
    top_level.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    # Limitiraj samo ako je max_comments postavljen
    if max_comments:
        top_level = top_level[:max_comments]
    
    for comment in top_level:
        comment_id = comment.get('id')
        comment_text = truncate_text(comment.get('text', ''), 300)
        thread_text += f"  └─ COMMENT [{comment_id}] (↑{comment.get('score', 0)}): {comment_text}\n"
        
        # Uzmi sve reply-ove, sortirane po score-u
        if comment_id in replies:
            top_replies = sorted(replies[comment_id], key=lambda x: x.get('score', 0), reverse=True)
            for reply in top_replies:
                reply_text = truncate_text(reply.get('text', ''), 200)
                thread_text += f"     └─ REPLY [{reply.get('id')}] (↑{reply.get('score', 0)}): {reply_text}\n"
        
        thread_text += "\n"
    
    return thread_text


def prepare_analysis_context(query: str, search_results: List[Dict[str, Any]]) -> str:

    context = f"USER QUERY: {query}\n\n"
    context += "="*80 + "\n"
    context += "RELEVANT REDDIT DISCUSSIONS (sorted by similarity):\n"
    context += "="*80 + "\n\n"
    
    for i, result in enumerate(search_results, 1):
        similarity = result.get('similarity_score', 0)
        subreddit = result.get('subreddit', 'unknown')
        full_doc = result.get('full_doc', {})
        
        context += f"--- DISCUSSION {i} (similarity: {similarity:.3f}, r/{subreddit}) ---\n"
        context += build_thread_structure(full_doc)  # Svi komentari
        context += "\n"
    
    return context


def analyze_with_grok(
    query: str, 
    search_results: List[Dict[str, Any]], 
    use_preprocessing: bool = True,
    additional_context: str = None
) -> Dict[str, Any]:
    """
    Analizira Reddit diskusije sa Grok LLM-om.
    
    Args:
        query: User query
        search_results: Lista Reddit diskusija
        use_preprocessing: Ako True, koristi advanced preprocessing (default: True)
        additional_context: Extra kontekst (npr. HTML analysis) koji se dodaje uz Reddit
    """
    
    # PREPROCESSING: Obogati podatke pre slanja LLM-u
    if use_preprocessing:
        preprocessed = preprocess_for_analysis(query, search_results)
        context = preprocessed['enriched_context']
        preprocessing_stats = preprocessed['preprocessed_data']['aggregate_stats']
    else:
        # Legacy mode (bez preprocessinga)
        context = prepare_analysis_context(query, search_results)
        preprocessing_stats = None
    
    # Dodaj additional_context ako postoji (npr. HTML keyword findings)
    if additional_context:
        context = additional_context + context
    
    system_prompt = """You are a fraud detection analyst evaluating websites based on Reddit community discussions.

Analyze the provided Reddit discussions and statistics to determine if something is a scam or legitimate.

Return JSON:
{
  "scam_score": 0-100 (0=legitimate, 100=definite scam),
  "confidence": 0-100 (based on evidence strength),
  "summary": "2-3 sentence overview",
  "red_flags": ["warning 1", "warning 2", ...],
  "green_flags": ["positive 1", ...],
  "key_points": ["finding 1", "finding 2", ...],
  "recommendation": "AVOID/HIGH_CAUTION/INVESTIGATE/LOW_RISK/LIKELY_SAFE",
  "debate_summary": "summary of any disagreements",
  "reasoning": "detailed explanation of your verdict"
}

IMPORTANT:
- Look at the AGGREGATE STATS provided - scam mentions, positive vouches, credibility scores
- If you see clear consensus (e.g., 15+ scam mentions, 0 positive) → HIGH confidence (80-90)
- If you see positive consensus (e.g., 10+ vouches, 0-2 complaints) → HIGH confidence (80-90)
- If mixed or limited data → LOWER confidence (40-60)
- Use the preprocessed credibility scores - high credibility discussions are more reliable
- Community consensus level (strong_agreement vs controversial) is KEY
"""
    
    try:
        # Proceni veličinu konteksta (približno 4 chars = 1 token)
        estimated_tokens = len(context) / 4
        
        # LIMIT: OpenAI gpt-4o ima veliki prozor (~128K); ostavi konzervativnu marginu
        MAX_TOKENS = 80000  # Safe limit sa marginom za response
        
        # Ako je kontekst prevelik, podeli na 2 dela i analiziraj odvojeno
        if estimated_tokens > MAX_TOKENS:
            mid_point = len(search_results) // 2
            
            # Analiza prvog dela
            context_part1 = prepare_analysis_context(query, search_results[:mid_point])
            response1 = openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt + "\n\nNote: This is PART 1 of 2. Analyze these discussions and provide preliminary findings."},
                    {"role": "user", "content": context_part1}
                ],
                temperature=0.3,
                response_format={"type": "json_object"} 
            )
            result1 = json.loads(response1.choices[0].message.content)
            
            # Analiza drugog dela SA KONTEKSTOM iz Part 1
            part1_summary = f"""
PREVIOUS ANALYSIS (PART 1 - first {mid_point} discussions):
- Scam Score: {result1.get('scam_score', 0)}/100
- Confidence: {result1.get('confidence', 0)}/100
- Key Red Flags: {', '.join(result1.get('red_flags', [])[:5])}
- Key Green Flags: {', '.join(result1.get('green_flags', [])[:5])}
- Preliminary Verdict: {result1.get('recommendation', 'INVESTIGATE')}
- Summary: {result1.get('summary', '')}

Now analyze PART 2 and provide a FINAL assessment considering both parts:
"""
            
            context_part2 = prepare_analysis_context(query, search_results[mid_point:])
            response2 = openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt + "\n\nNote: This is PART 2 of 2. You have context from Part 1. Provide FINAL analysis combining both parts."},
                    {"role": "user", "content": part1_summary + "\n" + context_part2}
                ],
                temperature=0.3,
                response_format={"type": "json_object"} 
            )
            result2 = json.loads(response2.choices[0].message.content)
            
            # Vrati result2 kao finalni (jer on već kombinuje obe analize)
            # Ali dodaj metadata da se zna da je bilo split
            result2['was_split_analysis'] = True
            result2['part1_score'] = result1.get('scam_score', 0)
            result2['part2_score'] = result2.get('scam_score', 0)
            
            return result2
        
        # Ako je kontekst OK veličine, uradi normalnu analizu
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context}
            ],
            temperature=0.3,
            response_format={"type": "json_object"} 
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Dodaj preprocessing stats u rezultat (ako postoje)
        if preprocessing_stats:
            result['preprocessing_insights'] = {
                "avg_discussion_credibility": preprocessing_stats.get('avg_discussion_credibility'),
                "total_scam_mentions": preprocessing_stats['scam_indicators']['total_scam_mentions'],
                "community_consensus": preprocessing_stats['consensus']['overall'],
                "keyword_risk_score": preprocessing_stats['keyword_analysis']['keyword_score']
            }
        
        return result
    
    except Exception as e:
        return {
            "scam_score": -1,
            "confidence": 0,
            "summary": f"Error during analysis: {str(e)}",
            "red_flags": [],
            "green_flags": [],
            "key_points": [],
            "recommendation": "ERROR",
            "debate_summary": "",
            "reasoning": f"LLM analysis failed: {str(e)}"
        }
