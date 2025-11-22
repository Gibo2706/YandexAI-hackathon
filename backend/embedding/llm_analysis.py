import os
import json
from openai import OpenAI
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

grok_client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

GROK_MODEL = "llama-3.3-70b-versatile"


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


def analyze_with_grok(query: str, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:

    context = prepare_analysis_context(query, search_results)
    
    system_prompt = """You are an expert fraud detection analyst analyzing Reddit discussions.

Your task:
1. Analyze Reddit threads (including comment debates via parent_id structure)
2. Detect scams, fraud, and suspicious activities
3. Consider comment thread dynamics (debates, disagreements, consensus)
4. Weight evidence by upvotes and reply structure
5. Provide actionable risk assessment

Return JSON with:
{
  "scam_score": 0-100 (0=legitimate, 100=definite scam),
  "confidence": 0-100 (how certain are you based on evidence quality),
  "summary": "2-3 sentence overview",
  "red_flags": ["warning sign 1", "warning sign 2", ...],
  "green_flags": ["positive indicator 1", ...],
  "key_points": ["important finding 1", "important finding 2", ...],
  "recommendation": "AVOID/CAUTION/INVESTIGATE/SAFE",
  "debate_summary": "summary of disagreements in threads",
  "reasoning": "detailed explanation of your assessment"
}

Consider:
- High upvotes on warnings = strong signal
- Debate in replies = controversy (investigate further)
- Consensus across multiple threads = reliable
- Recent vs old discussions
- Subreddit reputation (r/scams vs r/investing)
"""
    
    try:
        # Proceni veličinu konteksta (približno 4 chars = 1 token)
        estimated_tokens = len(context) / 4
        
        # Ako je kontekst prevelik, podeli na 2 dela i analiziraj odvojeno
        if estimated_tokens > 10000:  # Ostavi marginu
            mid_point = len(search_results) // 2
            
            # Analiza prvog dela
            context_part1 = prepare_analysis_context(query, search_results[:mid_point])
            response1 = grok_client.chat.completions.create(
                model=GROK_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt + "\n\nNote: This is PART 1 of 2. Analyze these discussions."},
                    {"role": "user", "content": context_part1}
                ],
                temperature=0.3,
                response_format={"type": "json_object"} 
            )
            result1 = json.loads(response1.choices[0].message.content)
            
            # Analiza drugog dela
            context_part2 = prepare_analysis_context(query, search_results[mid_point:])
            response2 = grok_client.chat.completions.create(
                model=GROK_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt + "\n\nNote: This is PART 2 of 2. Analyze these discussions."},
                    {"role": "user", "content": context_part2}
                ],
                temperature=0.3,
                response_format={"type": "json_object"} 
            )
            result2 = json.loads(response2.choices[0].message.content)
            
            # Kombinuj rezultate
            combined_result = {
                "scam_score": int((result1.get("scam_score", 0) + result2.get("scam_score", 0)) / 2),
                "confidence": int((result1.get("confidence", 0) + result2.get("confidence", 0)) / 2),
                "summary": f"{result1.get('summary', '')} {result2.get('summary', '')}",
                "red_flags": list(set(result1.get("red_flags", []) + result2.get("red_flags", []))),
                "green_flags": list(set(result1.get("green_flags", []) + result2.get("green_flags", []))),
                "key_points": result1.get("key_points", []) + result2.get("key_points", []),
                "recommendation": result1.get("recommendation", "INVESTIGATE"),
                "debate_summary": f"Part 1: {result1.get('debate_summary', '')} | Part 2: {result2.get('debate_summary', '')}",
                "reasoning": f"[PART 1] {result1.get('reasoning', '')} [PART 2] {result2.get('reasoning', '')}"
            }
            return combined_result
        
        # Ako je kontekst OK veličine, uradi normalnu analizu
        response = grok_client.chat.completions.create(
            model=GROK_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context}
            ],
            temperature=0.3,
            response_format={"type": "json_object"} 
        )
        
        result = json.loads(response.choices[0].message.content)
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
