"""
Test za proveru token limita prilikom slanja Grok-u.

Grok llama-3.3-70b-versatile ima 128k token context limit.
Treba proveriti da li enriched context prelazi ovaj limit.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from embedding.preprocessing import preprocess_for_analysis


def estimate_tokens(text: str) -> int:
    """Aproximacija broja tokena (rough estimate: 4 chars = 1 token)"""
    return len(text) // 4


def test_token_limit():
    """
    Simulira veliki result set i proverava da li context prelazi limit.
    """
    
    # Simulacija search results (10 results sa po 5 komentara)
    mock_results = []
    for i in range(10):
        mock_results.append({
            "text": f"This is a test post about scam detection, lorem ipsum " * 50,
            "score": 0.8 + (i * 0.01),
            "metadata": {
                "subreddit": "scams",
                "title": f"Is X a scam? Discussion {i}",
                "score": 15 + i,
                "num_comments": 5,
                "url": f"https://reddit.com/test{i}"
            },
            "full_doc": {
                "post": {
                    "id": f"post_{i}",
                    "title": f"Is X a scam? Discussion {i}",
                    "text": "Lorem ipsum dolor sit amet " * 100,
                    "score": 15 + i,
                    "num_comments": 5
                },
                "comments": [
                    {
                        "id": f"comment_{i}_{j}",
                        "text": f"This is a test comment about scams " * 20,
                        "score": 3 + j,
                        "subreddit": "scams",
                        "parent_id": f"post_{i}"
                    }
                    for j in range(5)
                ]
            }
        })
    
    query = "Is example.com a scam?"
    
    # Preprocess
    print("🔄 Preprocessing search results...")
    enriched_context = preprocess_for_analysis(query, mock_results)
    
    # Estimate tokens
    chars = len(enriched_context)
    tokens = estimate_tokens(enriched_context)
    
    print(f"\n📊 TOKEN ANALYSIS:")
    print(f"  Characters: {chars:,}")
    print(f"  Estimated tokens: {tokens:,}")
    print(f"  Grok limit: 128,000 tokens")
    print(f"  Usage: {(tokens/128000)*100:.1f}%")
    
    if tokens > 128000:
        print(f"\n❌ WARNING: Context exceeds Grok limit by {tokens - 128000:,} tokens!")
        print(f"\n💡 SOLUTIONS:")
        print(f"  1. Reduce number of search results (currently: {len(mock_results)})")
        print(f"  2. Limit comments per post (currently: 5)")
        print(f"  3. Truncate enrichment data")
        print(f"  4. Summarize preprocessing before sending to Grok")
    elif tokens > 100000:
        print(f"\n⚠️ CAUTION: Context is close to limit (>{100000:,} tokens)")
        print(f"   Consider reducing context to be safe")
    else:
        print(f"\n✅ OK: Context is within safe limits")
    
    # Show sample enriched context
    print(f"\n📄 SAMPLE ENRICHED CONTEXT (first 500 chars):")
    print(f"{enriched_context[:500]}...")
    
    return {
        "chars": chars,
        "tokens": tokens,
        "limit": 128000,
        "safe": tokens < 100000,
        "results_count": len(mock_results)
    }


if __name__ == "__main__":
    test_token_limit()
