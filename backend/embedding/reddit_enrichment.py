
from typing import Dict, Any, List
import re


def analyze_reddit_user(comment_or_post: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analizira kredibilitet na osnovu score-a.
    OPTIMIZED: Prilagođeno za score 1-20 (ne 100+).
    """
    author = comment_or_post.get('author', '[deleted]')
    score = comment_or_post.get('score', 0)
    
    # Red flags
    red_flags = []
    credibility_score = 50  # Start neutral
    
    # 1. Deleted/Removed user
    if author in ['[deleted]', '[removed]', 'AutoModerator']:
        red_flags.append("User deleted/removed")
        credibility_score -= 30
    
    # 2. Low karma post (downvoted)
    if score < -2:
        red_flags.append(f"Heavily downvoted (score: {score})")
        credibility_score -= 20
    elif score < 0:
        red_flags.append(f"Downvoted (score: {score})")
        credibility_score -= 10
    
    # 3. High karma (ADJUSTED: max ~20 u realnim podacima)
    if score >= 20:
        credibility_score += 25
    elif score >= 10:
        credibility_score += 20
    elif score >= 5:
        credibility_score += 15
    elif score > 0:
        credibility_score += 10
    
    return {
        "author": author,
        "credibility_score": max(0, min(100, credibility_score)),
        "karma_score": score,
        "red_flags": red_flags,
        "is_deleted": author in ['[deleted]', '[removed]']
    }


def analyze_post_quality(post: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analizira kvalitet Reddit posta.
    OPTIMIZED: Prilagođeno za num_comments 1-10 i score 1-50 (ne 100+).
    """
    title = post.get('title', '')
    text = post.get('text', '')
    score = post.get('score', 0)
    num_comments = post.get('num_comments', 0)
    
    quality_score = 50
    indicators = []
    
    # 1. Engagement level (ADJUSTED: max ~10 komentara u realnim podacima)
    if num_comments >= 10:
        quality_score += 20
        indicators.append("High engagement (10+ comments)")
    elif num_comments >= 7:
        quality_score += 15
        indicators.append("Good engagement (7+ comments)")
    elif num_comments >= 4:
        quality_score += 10
        indicators.append("Moderate engagement (4+ comments)")
    elif num_comments >= 2:
        quality_score += 5
        indicators.append("Some engagement (2-3 comments)")
    elif num_comments < 2:
        quality_score -= 10
        indicators.append("Low engagement (<2 comments)")
    
    # 2. Post score (ADJUSTED: max ~50 u realnim podacima)
    if score >= 50:
        quality_score += 20
        indicators.append("Highly upvoted (50+ karma)")
    elif score >= 20:
        quality_score += 15
        indicators.append("Well received (20+ karma)")
    elif score >= 10:
        quality_score += 10
        indicators.append("Positively received (10+ karma)")
    elif score >= 5:
        quality_score += 5
        indicators.append("Some upvotes (5+ karma)")
    elif score < 0:
        quality_score -= 15
        indicators.append("Downvoted post")
    elif score == 0:
        quality_score -= 5
        indicators.append("No upvotes")
    
    # 3. Content length (longer = more effort)
    content_length = len(title) + len(text)
    if content_length > 1000:
        quality_score += 10
        indicators.append("Detailed post (1000+ chars)")
    elif content_length > 500:
        quality_score += 5
        indicators.append("Substantial post (500+ chars)")
    elif content_length < 50:
        quality_score -= 10
        indicators.append("Very short post (<50 chars)")
    
    # 4. Title quality
    if title.upper() == title and len(title) > 10:
        quality_score -= 10
        indicators.append("ALL CAPS title (spam indicator)")
    
    if title.count('!') > 3:
        quality_score -= 5
        indicators.append("Multiple exclamation marks")
    
    # 5. Removed/deleted
    if '[removed]' in text or '[deleted]' in text:
        quality_score -= 20
        indicators.append("Content removed/deleted")
    
    return {
        "quality_score": max(0, min(100, quality_score)),
        "engagement_level": num_comments,
        "karma": score,
        "content_length": content_length,
        "indicators": indicators
    }


def analyze_comment_thread(comments: List[Dict[str, Any]], post_id: str) -> Dict[str, Any]:
    """
    Analizira thread struktur i dinamiku diskusije.
    OPTIMIZED: U realnim podacima SVI komentari su top-level (parent_id = post_id).
    """
    if not comments:
        return {
            "thread_depth": 0,
            "top_level_count": 0,
            "consensus_level": "no_comments",
            "top_contributors": [],
            "total_comments": 0
        }
    
    # U našim podacima SVI komentari su top-level
    top_level = [c for c in comments if c.get('parent_id') == post_id]
    replies = [c for c in comments if c.get('parent_id') != post_id]
    
    # Analiza debate-a (reply ratio)
    reply_ratio = len(replies) / max(len(top_level), 1) if top_level else 0
    
    # Consensus detection (da li se svi slažu ili ima debate)
    scores = [c.get('score', 0) for c in comments]
    positive_scores = [s for s in scores if s > 2]
    negative_scores = [s for s in scores if s < 0]
    
    if len(positive_scores) > len(comments) * 0.7:
        consensus = "strong_agreement"
    elif len(negative_scores) > len(comments) * 0.3:
        consensus = "controversial"
    elif reply_ratio > 1:
        consensus = "active_debate"
    else:
        consensus = "mixed"
    
    # Top contributors (highest karma comments)
    sorted_comments = sorted(comments, key=lambda x: x.get('score', 0), reverse=True)
    top_contributors = [
        {
            "author": c.get('author', 'unknown'),
            "score": c.get('score', 0),
            "text_preview": c.get('text', '')[:100]
        }
        for c in sorted_comments[:3]
    ]
    
    # Prosečan score komentara
    avg_score = sum(scores) / len(scores) if scores else 0
    
    return {
        "thread_depth": len(replies),
        "top_level_count": len(top_level),
        "reply_ratio": round(reply_ratio, 2),
        "avg_comment_score": round(avg_score, 2),
        "debate_intensity": "high" if reply_ratio > 1.5 else "medium" if reply_ratio > 0.5 else "low",
        "consensus_level": consensus,
        "top_contributors": top_contributors,
        "total_comments": len(comments)
    }


def extract_scam_mentions(text: str) -> Dict[str, Any]:
    """
    Ekstraktuje direktne mention-e scam-ova, prevara, fraud-a iz teksta.
    """
    text_lower = text.lower()
    
    scam_mentions = []
    fraud_indicators = []
    
    # Direct scam accusations
    scam_words = ['scam', 'fraud', 'fake', 'phishing', 'ponzi', 'pyramid', 'con artist', 
                  'rip off', 'ripoff', 'swindler', 'thief', 'stolen money']
    
    for word in scam_words:
        if word in text_lower:
            # Extract context (sentence containing the word)
            sentences = text.split('.')
            for sentence in sentences:
                if word in sentence.lower():
                    scam_mentions.append({
                        "keyword": word,
                        "context": sentence.strip()[:150]
                    })
                    break
    
    # Warning phrases
    warning_phrases = [
        'stay away', 'avoid this', 'don\'t trust', 'be careful',
        'red flag', 'warning sign', 'suspicious', 'sketchy',
        'seems fishy', 'too good to be true', 'run away'
    ]
    
    for phrase in warning_phrases:
        if phrase in text_lower:
            fraud_indicators.append(phrase)
    
    # Positive vouches
    positive_phrases = [
        'legit', 'legitimate', 'trustworthy', 'reliable',
        'safe to use', 'worked for me', 'no problems', 'recommended'
    ]
    
    positive_mentions = [phrase for phrase in positive_phrases if phrase in text_lower]
    
    return {
        "scam_mentions": scam_mentions,
        "fraud_indicators": fraud_indicators,
        "positive_vouches": positive_mentions,
        "scam_mention_count": len(scam_mentions),
        "warning_count": len(fraud_indicators),
        "positive_count": len(positive_mentions)
    }


def enrich_reddit_discussion(discussion: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main funkcija - obogaćuje jedan Reddit discussion sa svim analizama.
    """
    post = discussion.get('post', {})
    comments = discussion.get('comments', [])
    
    # 1. Analyze post quality
    post_quality = analyze_post_quality(post)
    
    # 2. Analyze post author
    post_author_analysis = analyze_reddit_user(post)
    
    # 3. Analyze comments
    comment_analyses = [analyze_reddit_user(c) for c in comments]
    avg_comment_credibility = sum(ca['credibility_score'] for ca in comment_analyses) / max(len(comment_analyses), 1)
    
    # 4. Thread analysis
    thread_analysis = analyze_comment_thread(comments, post.get('id'))
    
    # 5. Extract scam mentions from all text
    all_text = f"{post.get('title', '')} {post.get('text', '')} " + ' '.join([c.get('text', '') for c in comments])
    scam_analysis = extract_scam_mentions(all_text)
    
    # 6. Calculate overall discussion credibility
    discussion_credibility = (
        post_quality['quality_score'] * 0.4 +
        post_author_analysis['credibility_score'] * 0.3 +
        avg_comment_credibility * 0.3
    )
    
    return {
        "post_quality": post_quality,
        "post_author": post_author_analysis,
        "thread_analysis": thread_analysis,
        "scam_analysis": scam_analysis,
        "discussion_credibility": round(discussion_credibility, 2),
        "avg_comment_credibility": round(avg_comment_credibility, 2),
        "total_comments_analyzed": len(comments)
    }


def enrich_all_discussions(search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Obogaćuje sve Reddit diskusije sa dodatnim analizama.
    """
    enriched = []
    
    for result in search_results:
        full_doc = result.get('full_doc', {})
        enrichment = enrich_reddit_discussion(full_doc)
        
        # Add enrichment to result
        result['enrichment'] = enrichment
        enriched.append(result)
    
    return enriched
