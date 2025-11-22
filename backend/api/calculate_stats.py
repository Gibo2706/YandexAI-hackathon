from typing import List, Dict, Any


def extract_statistics(search_results: List[Dict[str, Any]]) -> Dict[str, Any]:

    if not search_results:
        return {}
    
    total = len(search_results)
    similarities = [r.get('similarity_score', 0) for r in search_results]
    
    subreddit_counts = {}
    for r in search_results:
        sub = r.get('subreddit', 'unknown')
        subreddit_counts[sub] = subreddit_counts.get(sub, 0) + 1
    
    post_scores = []
    comment_scores = []
    total_comments = 0
    
    for r in search_results:
        post_scores.append(r.get('score', 0))
        
        full_doc = r.get('full_doc', {})
        comments = full_doc.get('comments', [])
        total_comments += len(comments)
        
        for comment in comments:
            comment_scores.append(comment.get('score', 0))

    max_depth = 0
    total_top_level = 0
    total_replies = 0
    
    for r in search_results:
        full_doc = r.get('full_doc', {})
        post_id = full_doc.get('post', {}).get('id')
        comments = full_doc.get('comments', [])
        
        for comment in comments:
            if comment.get('parent_id') == post_id:
                total_top_level += 1
            else:
                total_replies += 1
    
    return {
        "total_discussions": total,
        "avg_similarity": sum(similarities) / len(similarities) if similarities else 0,
        "min_similarity": min(similarities) if similarities else 0,
        "max_similarity": max(similarities) if similarities else 0,
        "subreddit_distribution": subreddit_counts,
        "sentiment_indicators": {
            "avg_post_score": sum(post_scores) / len(post_scores) if post_scores else 0,
            "avg_comment_score": sum(comment_scores) / len(comment_scores) if comment_scores else 0,
            "total_comments": total_comments,
            "positive_comments": len([s for s in comment_scores if s > 0]),
            "negative_comments": len([s for s in comment_scores if s < 0])
        },
        "engagement_stats": {
            "avg_comments_per_post": total_comments / total if total > 0 else 0,
            "total_engagement": sum(post_scores) + sum(comment_scores)
        },
        "thread_depth": {
            "top_level_comments": total_top_level,
            "reply_comments": total_replies,
            "debate_ratio": total_replies / total_top_level if total_top_level > 0 else 0
        }
    }
