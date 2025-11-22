# 📊 FINALNE API STRUKTURE (bez External APIs)

## 🎯 GARANTOVANE RESPONSE STRUKTURE

---

## 1️⃣ `/analyze` - Reddit Analiza sa Enrichment-om

**Request:**
```json
POST /analyze
{
  "query": "is crypto-invest a scam?",
  "k": 20  // Optional, default 20
}
```

**Napomena:** Endpoint INTERNO radi search - ne treba slati `search_results`!

**Response:**
```typescript
{
  // META
  "query": string,
  "num_discussions_analyzed": number,
  
  // ENRICHED REDDIT DATA
  "enriched_results": [
    {
      "text": string,                    // Full Reddit text
      "score": number,                   // Similarity score (0-1)
      "metadata": {
        "subreddit": string,
        "title": string,
        "score": number,                 // Post karma
        "num_comments": number,
        "url": string
      },
      
      // ENRICHMENT DATA
      "enrichment": {
        // Post Quality
        "post_quality": {
          "quality_score": number,       // 0-100
          "engagement_level": number,    // Number of comments
          "karma": number,                // Post score
          "content_length": number,      // Character count
          "indicators": string[]          // ["High engagement (10+ comments)", ...]
        },
        
        // Post Author Credibility
        "post_author": {
          "author": string,
          "credibility_score": number,   // 0-100
          "karma_score": number,
          "red_flags": string[],
          "is_deleted": boolean
        },
        
        // Thread Analysis
        "thread_analysis": {
          "thread_depth": number,        // Reply count
          "top_level_count": number,     // Top-level comments
          "reply_ratio": number,         // Replies per top comment
          "avg_comment_score": number,   // Average karma
          "debate_intensity": "low" | "medium" | "high",
          "consensus_level": "strong_agreement" | "controversial" | "active_debate" | "mixed" | "no_comments",
          "top_contributors": [
            {
              "author": string,
              "score": number,
              "text_preview": string     // First 100 chars
            }
          ],
          "total_comments": number
        },
        
        // Scam Mentions Analysis
        "scam_analysis": {
          "scam_mentions": [
            {
              "keyword": string,         // "scam", "fraud", etc.
              "context": string          // Sentence containing keyword
            }
          ],
          "fraud_indicators": string[],  // ["stay away", "red flag", ...]
          "positive_vouches": string[],  // ["legit", "trustworthy", ...]
          "scam_mention_count": number,
          "warning_count": number,
          "positive_count": number
        },
        
        // Overall Scores
        "discussion_credibility": number,     // 0-100
        "avg_comment_credibility": number,    // 0-100
        "total_comments_analyzed": number
      }
    }
    // ... more enriched results
  ],
  
  // AGGREGATE STATISTICS
  "aggregate_stats": {
    "total_discussions": number,
    "avg_discussion_credibility": number,    // 0-100
    "avg_post_quality": number,              // 0-100
    
    "scam_indicators": {
      "total_scam_mentions": number,
      "total_warnings": number,
      "total_positive_vouches": number,
      "scam_to_positive_ratio": number       // Higher = more scam mentions
    },
    
    "consensus": {
      "overall": "strong_community_agreement" | "highly_controversial" | "mixed_opinions",
      "strong_agreement": number,            // Count of strong agreements
      "controversial": number                // Count of controversial threads
    },
    
    "keyword_analysis": {
      "total_red_flags": number,
      "total_green_flags": number,
      "keyword_score": number                // Weighted score from keywords
    }
  },
  
  // GROK LLM ANALYSIS
  "analysis": {
    "scam_score": number,                    // 0-100
    "confidence": number,                    // 0-100
    "summary": string,                       // 2-3 sentence overview
    "red_flags": string[],                   // ["Warning 1", "Warning 2", ...]
    "green_flags": string[],                 // ["Positive 1", ...]
    "key_points": string[],                  // Important findings
    "recommendation": "AVOID" | "HIGH_CAUTION" | "INVESTIGATE" | "LOW_RISK" | "LIKELY_SAFE",
    "reasoning": string                      // Detailed explanation
  }
}
```

---

## 2️⃣ `/analyze-html` - HTML + Reddit Analiza

**Request:**
```json
POST /analyze-html
{
  "html_content": "<html>...</html>",
  "k": 20  // Optional, default 20
}
```

**Response:**
```typescript
{
  // META
  "query": string,                          // Generated search query
  "num_discussions_analyzed": number,
  
  // HTML ANALYSIS
  "html_analysis": {
    "company_info": {
      "company_name": string,
      "products_services": string[],
      "industry_keywords": string[]
    },
    
    "extracted_data": {
      "title": string,
      "description": string,
      "headings_count": number,
      "links_count": number
    },
    
    "algorithmic_score": number,             // 0-100 from keyword detection
    
    "keyword_findings": {
      "red_flags": string[],                 // Top 10 scam keywords found
      "green_flags": string[]                // Top 10 trust signals found
    }
  },
  
  // REDDIT ANALYSIS (ista struktura kao /analyze)
  "reddit_analysis": {
    "discussions_found": boolean,
    
    "enriched_results": [
      {
        "text": string,
        "score": number,
        "metadata": {...},
        "enrichment": {
          "post_quality": {...},
          "post_author": {...},
          "thread_analysis": {...},
          "scam_analysis": {...},
          "discussion_credibility": number,
          "avg_comment_credibility": number,
          "total_comments_analyzed": number
        }
      }
    ],
    
    "aggregate_stats": {
      "total_discussions": number,
      "avg_discussion_credibility": number,
      "avg_post_quality": number,
      "scam_indicators": {...},
      "consensus": {...},
      "keyword_analysis": {...}
    },
    
    "llm_summary": string                    // Grok summary of Reddit discussions
  },
  
  // COMBINED VERDICT
  "combined_verdict": {
    "overall_scam_score": number,            // 0-100 (final score)
    "verdict": "AVOID" | "HIGH_CAUTION" | "INVESTIGATE" | "LOW_RISK" | "LIKELY_SAFE",
    "confidence": number,                    // 0-1 (e.g., 0.85 = 85%)
    "reasoning": string,                     // Combined reasoning
    
    "red_flags": string[],                   // Max 15, from all sources
    "green_flags": string[],                 // Max 15, from all sources
    "key_points": string[],                  // Max 15, important findings
    
    "breakdown": {
      "html_score": number,                  // HTML algorithmic score
      "reddit_score": number | null,         // null if no Reddit data
      "weight_strategy": string              // "60% HTML + 40% Reddit" or "100% HTML (no Reddit data)"
    }
  }
}
```

---

## 📋 KLJUČNE RAZLIKE

| Feature | `/analyze` | `/analyze-html` |
|---------|-----------|-----------------|
| **Input** | Query + Reddit search results | HTML content |
| **HTML Parsing** | ❌ | ✅ |
| **Keyword Detection** | ✅ (from Reddit text) | ✅ (from HTML) |
| **Reddit Enrichment** | ✅ | ✅ |
| **Aggregate Stats** | ✅ | ✅ |
| **Company Info** | ❌ | ✅ |
| **Combined Score** | ❌ (samo Reddit) | ✅ (HTML + Reddit) |
| **Response Time** | ~2-3s | ~3-5s |

---

## 🎨 ENRICHMENT KOMPONENTE

### Post Quality (0-100 score):
- **Engagement:** Broj komentara (10+, 7+, 4+, 2+)
- **Karma:** Post score (50+, 20+, 10+, 5+)
- **Content Length:** Dužina teksta (1000+, 500+, <50)
- **Title Quality:** ALL CAPS detection, exclamation marks
- **Removed/Deleted:** Marker za obrisane postove

### Author Credibility (0-100 score):
- **Deleted Check:** Author = [deleted] / [removed]
- **Downvotes:** Score < -2 (heavy), < 0 (mild)
- **Karma Tiers:** 20+, 10+, 5+, >0

### Thread Analysis:
- **Depth:** Koliko replies ima
- **Debate Intensity:** low/medium/high (based on reply ratio)
- **Consensus:** strong_agreement / controversial / mixed / no_comments
- **Top Contributors:** Top 3 komentara po score-u

### Scam Analysis:
- **Direct Mentions:** "scam", "fraud", "fake", "phishing"
- **Warning Phrases:** "stay away", "red flag", "suspicious"
- **Positive Vouches:** "legit", "trustworthy", "worked for me"

---

## 💡 FRONTEND USAGE

### Prikaz `/analyze` rezultata (JEDNOSTAVNIJI - jedan poziv!):
```typescript
// STARI način (2 poziva):
// 1. const searchResults = await fetch('/search', {query: "..."})
// 2. const analysis = await fetch('/analyze', {query: "...", search_results: searchResults})

// NOVI način (1 poziv):
const response = await fetch('/analyze', {
  method: 'POST',
  body: JSON.stringify({
    query: "is crypto-invest a scam?",
    k: 20  // optional
  })
});

const data = await response.json();
// Check if data exists
if (response.enriched_results.length > 0) {
  const firstDiscussion = response.enriched_results[0];
  
  // Display credibility
  const credibility = firstDiscussion.enrichment.discussion_credibility;
  showCredibilityBadge(credibility);  // 0-100 score
  
  // Display consensus
  const consensus = firstDiscussion.enrichment.thread_analysis.consensus_level;
  if (consensus === "strong_agreement") {
    showWarning("Community strongly agrees this is suspicious");
  }
  
  // Display scam mentions
  const scamMentions = firstDiscussion.enrichment.scam_analysis.scam_mention_count;
  if (scamMentions > 3) {
    showAlert(`${scamMentions} direct scam mentions found`);
  }
}

// Aggregate stats
const stats = response.aggregate_stats;
const ratio = stats.scam_indicators.scam_to_positive_ratio;
if (ratio > 2) {
  showWarning("Scam mentions significantly outweigh positive reviews");
}

// Final verdict
const verdict = response.analysis.recommendation;
showVerdict(verdict, response.analysis.scam_score);
```

### Prikaz `/analyze-html` rezultata:
```typescript
// HTML Findings
const htmlScore = response.html_analysis.algorithmic_score;
const redFlags = response.html_analysis.keyword_findings.red_flags;

showHTMLAnalysis({
  score: htmlScore,
  company: response.html_analysis.company_info.company_name,
  redFlags: redFlags
});

// Reddit Community Feedback
if (response.reddit_analysis.discussions_found) {
  const avgCredibility = response.reddit_analysis.aggregate_stats.avg_discussion_credibility;
  showCommunityFeedback(avgCredibility);
}

// Combined Verdict
const verdict = response.combined_verdict;
showFinalVerdict({
  score: verdict.overall_scam_score,
  verdict: verdict.verdict,
  confidence: verdict.confidence,
  breakdown: verdict.breakdown
});
```

---

## ⚠️ NULL vs EMPTY HANDLING

**Pravilo:**
- **Arrays:** Uvek `[]` (prazan) ako nema podataka, NIKAD `null`
- **Numbers:** Može biti `null` samo ako se ne može izračunati (npr. `reddit_score` bez Reddit data)
- **Strings:** Konkretna poruka ("No Reddit discussions found"), ne `null`
- **Booleans:** Uvek `true` ili `false`, NIKAD `null`

**Primeri:**
```typescript
✅ "enriched_results": []                    // OK - prazan array
✅ "reddit_score": null                      // OK - nema Reddit podataka
✅ "llm_summary": "No discussions found"     // OK - poruka
✅ "discussions_found": false                // OK - boolean

❌ "enriched_results": null                  // LOŠE - array mora biti []
❌ "reddit_score": 0                         // LOŠE - 0 znači score=0, ne "nema"
❌ "discussions_found": null                 // LOŠE - boolean ne može null
```

---

## 🎯 VERDICT MAPPING

```typescript
const VERDICT_THRESHOLDS = {
  "AVOID": 75,           // 75-100
  "HIGH_CAUTION": 55,    // 55-74
  "INVESTIGATE": 35,     // 35-54
  "LOW_RISK": 20,        // 20-34
  "LIKELY_SAFE": 0       // 0-19
};

const VERDICT_COLORS = {
  "AVOID": "#DC2626",         // Red
  "HIGH_CAUTION": "#EA580C",  // Orange
  "INVESTIGATE": "#EAB308",   // Yellow
  "LOW_RISK": "#22C55E",      // Light Green
  "LIKELY_SAFE": "#16A34A"    // Dark Green
};
```

---

## ✅ TypeScript Interfaces

```typescript
// /analyze Response
interface AnalyzeResponse {
  query: string;
  num_discussions_analyzed: number;
  enriched_results: EnrichedResult[];
  aggregate_stats: AggregateStats;
  analysis: LLMAnalysis;
}

interface EnrichedResult {
  text: string;
  score: number;
  metadata: Metadata;
  enrichment: Enrichment;
}

interface Enrichment {
  post_quality: PostQuality;
  post_author: AuthorCredibility;
  thread_analysis: ThreadAnalysis;
  scam_analysis: ScamAnalysis;
  discussion_credibility: number;
  avg_comment_credibility: number;
  total_comments_analyzed: number;
}

// /analyze-html Response
interface AnalyzeHtmlResponse {
  query: string;
  num_discussions_analyzed: number;
  html_analysis: HtmlAnalysis;
  reddit_analysis: RedditAnalysis;
  combined_verdict: CombinedVerdict;
}

interface CombinedVerdict {
  overall_scam_score: number;
  verdict: "AVOID" | "HIGH_CAUTION" | "INVESTIGATE" | "LOW_RISK" | "LIKELY_SAFE";
  confidence: number;
  reasoning: string;
  red_flags: string[];
  green_flags: string[];
  key_points: string[];
  breakdown: {
    html_score: number;
    reddit_score: number | null;
    weight_strategy: string;
  };
}
```

---

**Frontend dev može koristiti ove strukture kao fiksne - NEĆE SE MENJATI!** 🎯
