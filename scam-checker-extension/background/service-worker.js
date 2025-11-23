// Background Service Worker - handles API communication

// Keep service worker alive
let keepAliveInterval;

chrome.runtime.onStartup.addListener(() => {
  console.log('[Scam Checker BG] Extension startup');
  startKeepAlive();
});

chrome.runtime.onInstalled.addListener(() => {
  console.log('[Scam Checker BG] Extension installed');
  startKeepAlive();
});

// Keep service worker alive by sending periodic messages
function startKeepAlive() {
  if (keepAliveInterval) clearInterval(keepAliveInterval);

  keepAliveInterval = setInterval(() => {
    chrome.runtime.getPlatformInfo(() => {
      // Just checking platform keeps worker alive
      console.log('[Scam Checker BG] Keepalive ping');
    });
  }, 20000); // Every 20 seconds
}

startKeepAlive();

// Listen for messages from content script and popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('[Scam Checker BG] ========== MESSAGE RECEIVED ==========');
  console.log('[Scam Checker BG] Action:', request.action);
  console.log('[Scam Checker BG] Sender tab:', sender.tab?.id);
  console.log('[Scam Checker BG] Timestamp:', new Date().toISOString());

  // Simple ping test
  if (request.action === 'ping') {
    console.log('[Scam Checker BG] Ping received, sending pong...');
    sendResponse({ success: true, message: 'pong', timestamp: Date.now() });
    return false; // Synchronous response
  }

  if (request.action === 'analyzeUrl') {
    console.log('[Scam Checker BG] Starting handleAnalyzeUrl...');

    // Handle async analysis
    handleAnalyzeUrl(request.data)
      .then(result => {
        console.log('[Scam Checker BG] ✅ Analysis complete, sending response...');
        console.log('[Scam Checker BG] Response success:', result.success);
        try {
          sendResponse(result);
        } catch (e) {
          console.error('[Scam Checker BG] Error sending response:', e);
        }
      })
      .catch(error => {
        console.error('[Scam Checker BG] ❌ Error in handleAnalyzeUrl:', error);
        try {
          sendResponse({ success: false, error: error.message });
        } catch (e) {
          console.error('[Scam Checker BG] Error sending error response:', e);
        }
      });

    return true; // CRITICAL: Keep message channel open for async response
  }

  if (request.action === 'openPopup') {
    chrome.action.openPopup();
    sendResponse({ success: true });
    return false;
  }

  // Unknown action
  console.warn('[Scam Checker BG] Unknown action:', request.action);
  sendResponse({ success: false, error: 'Unknown action' });
  return false;
});

// Handle URL analysis
async function handleAnalyzeUrl(data) {
  console.log('[Scam Checker BG] ========== STARTING ANALYSIS ==========');
  console.log('[Scam Checker BG] Analyzing URL:', data.domain);
  console.log('[Scam Checker BG] HTML content length:', data.htmlContent?.length || 0, 'chars');

  try {
    // MOCK DATA - simulira /analyze-html response
    console.log('[Scam Checker BG] Using MOCK data (API not deployed yet)');

    const mockResponse = generateMockAnalyzeHtmlResponse(data);

    console.log('[Scam Checker BG] ✅ Mock response generated!');

    // Transform to extension format
    const transformedData = transformAnalyzeResponse(mockResponse, data);

    console.log('[Scam Checker BG] ✅ Transformation complete!');
    console.log('[Scam Checker BG] Risk Score:', transformedData.riskScore);
    console.log('[Scam Checker BG] ========== ANALYSIS COMPLETE ==========');

    return { success: true, data: transformedData };

    /*
    // REAL API CALL - aktiviraj kada bude deployovan
    const analyzeHtmlUrl = 'https://www.check-mate.systems/api/analyze-html';

    console.log('[Scam Checker BG] Calling /analyze-html endpoint');
    console.log('[Scam Checker BG] URL:', analyzeHtmlUrl);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000);

    const response = await fetch(analyzeHtmlUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        html_content: data.htmlContent,
        k: 20
      }),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    console.log('[Scam Checker BG] Response status:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('[Scam Checker BG] API error:', errorText);
      throw new Error(`API returned ${response.status}: ${errorText}`);
    }

    const analyzeResults = await response.json();
    console.log('[Scam Checker BG] ✅ API response received!');
    console.log('[Scam Checker BG] Response data:', JSON.stringify(analyzeResults, null, 2));

    // Transform API response to extension format
    const transformedData = transformAnalyzeResponse(analyzeResults, data);

    console.log('[Scam Checker BG] ✅ Transformation complete!');
    console.log('[Scam Checker BG] Final data:', JSON.stringify(transformedData, null, 2));
    console.log('[Scam Checker BG] ========== ANALYSIS COMPLETE ==========');

    return { success: true, data: transformedData };
    */

  } catch (error) {
    console.error('[Scam Checker BG] ❌ ERROR:', error);
    console.error('[Scam Checker BG] Error message:', error.message);

    throw error;
  }
}

// Generate mock response matching /analyze-html format
function generateMockAnalyzeHtmlResponse(data) {
  const domain = data.domain || 'unknown';

  // HARDCODED MOCK DATA - matches exact API format
  return {
    query: `${domain} reviews scam legit trustworthy`,
    num_discussions_analyzed: 15,
    enriched_results: [
      {
        submission_id: "abc123",
        title: `Is ${domain} legit or a scam?`,
        subreddit: "Scams",
        score: 127,
        num_comments: 45,
        similarity_score: 0.92,
        sentiment_label: "negative",
        keyword_matches: ["scam", "fraud", "warning"]
      },
      {
        submission_id: "def456",
        title: `My positive experience with ${domain}`,
        subreddit: "Reviews",
        score: 89,
        num_comments: 23,
        similarity_score: 0.88,
        sentiment_label: "positive",
        keyword_matches: ["legit", "trust", "reliable"]
      },
      {
        submission_id: "ghi789",
        title: `${domain} - mixed reviews, proceed with caution`,
        subreddit: "PersonalFinance",
        score: 156,
        num_comments: 67,
        similarity_score: 0.85,
        sentiment_label: "neutral",
        keyword_matches: ["review", "caution"]
      },
      {
        submission_id: "jkl012",
        title: `Warning: Issues with ${domain} customer service`,
        subreddit: "AskReddit",
        score: 234,
        num_comments: 89,
        similarity_score: 0.81,
        sentiment_label: "negative",
        keyword_matches: ["warning", "issues", "customer service"]
      },
      {
        submission_id: "mno345",
        title: `${domain} delivered as promised - happy customer`,
        subreddit: "Ecommerce",
        score: 67,
        num_comments: 12,
        similarity_score: 0.79,
        sentiment_label: "positive",
        keyword_matches: ["legit", "happy", "delivered"]
      }
    ],
    aggregate_stats: {
      total_discussions: 15,
      total_comments: 236,
      avg_post_score: 134.6,
      avg_comment_score: 4.7,
      sentiment_distribution: {
        positive: 98,
        negative: 118,
        neutral: 20
      },
      keyword_frequency: {
        "scam": 23,
        "legit": 15,
        "trust": 12,
        "fraud": 8,
        "reliable": 10,
        "warning": 19,
        "caution": 7
      },
      top_subreddits: [
        { subreddit: "Scams", count: 5 },
        { subreddit: "Reviews", count: 4 },
        { subreddit: "PersonalFinance", count: 3 },
        { subreddit: "AskReddit", count: 2 },
        { subreddit: "Ecommerce", count: 1 }
      ]
    },
    analysis: `Based on 236 Reddit comments analyzing ${domain}:

**Overall Assessment:** This platform shows mixed signals with notable concerns raised by the community.

**Key Findings:**

✅ **Positive Signals (98 mentions - 42%):**
- 42% of users report successful transactions
- Some verified users share positive experiences
- Product/service delivery confirmed in multiple cases
- Responsive support mentioned by satisfied customers

⚠️ **Warning Signals (118 mentions - 50%):**
- 50% of comments express concerns or negative experiences
- Common complaints: delayed shipping, poor customer service response
- Multiple users report difficulty obtaining refunds
- Payment processing issues mentioned in several threads
- Better Business Bureau complaints referenced

**Community Consensus:**
The Reddit community leans toward caution. While some users have had positive experiences, a significant portion reports problems. The negative-to-positive ratio suggests elevated risk.

**Risk Level:** MODERATE-HIGH - Exercise caution and use protective measures.

**Recommendations:**
1. ⚠️ Use credit card or PayPal for buyer protection
2. 📋 Document all communications and transactions
3. 🔍 Research recent reviews (within last 6 months)
4. 💰 Start with small test order if possible
5. 📞 Verify contact information and customer service availability
6. ⏰ Check return/refund policy carefully before purchase`
  };
}

// Transform /analyze-html response to extension format
function transformAnalyzeResponse(apiResponse, requestData) {
  const stats = apiResponse.aggregate_stats || {};
  const sentiment = stats.sentiment_distribution || { positive: 0, negative: 0 };

  // Calculate risk score
  const totalSentiment = sentiment.positive + sentiment.negative;
  const negativeRatio = totalSentiment > 0 ? sentiment.negative / totalSentiment : 0.5;
  const riskScore = Math.min(100, Math.max(0, Math.round(negativeRatio * 100)));

  // Extract top posts from enriched results
  const topPosts = (apiResponse.enriched_results || []).slice(0, 5).map(result => ({
    id: result.submission_id,
    title: result.title,
    subreddit: result.subreddit,
    score: result.score || 0,
    numComments: result.num_comments || 0,
    similarity: result.similarity_score
  }));

  // Extract indicators from LLM analysis
  const llmAnalysis = apiResponse.analysis || '';
  const indicators = extractIndicatorsFromAnalysis(llmAnalysis, sentiment);

  return {
    analysisId: `analyze-html-${Date.now()}`,
    url: requestData.url,
    domain: requestData.domain,
    riskScore: riskScore,
    sentiment: {
      scam: negativeRatio,
      legit: 1 - negativeRatio
    },
    metrics: {
      postsAnalyzed: apiResponse.num_discussions_analyzed || 0,
      commentsReviewed: stats.total_comments || 0,
      positiveSentiment: totalSentiment > 0 ? Math.round((sentiment.positive / totalSentiment) * 100) : 50,
      negativeSentiment: totalSentiment > 0 ? Math.round((sentiment.negative / totalSentiment) * 100) : 50
    },
    indicators: indicators,
    riskFactors: generateRiskFactorsFromSentiment(sentiment, riskScore),
    recommendations: generateRecommendations(riskScore),
    redditPosts: topPosts,
    llmAnalysis: llmAnalysis,
    aggregateStats: stats,
    timestamp: new Date().toISOString()
  };
}

// Extract indicators from LLM analysis text
function extractIndicatorsFromAnalysis(analysis, sentiment) {
  const positive = [];
  const warning = [];

  const lowerAnalysis = analysis.toLowerCase();

  // Parse positive signals from analysis
  if (lowerAnalysis.includes('positive experiences') || lowerAnalysis.includes('successful transactions')) {
    positive.push('Positive user experiences reported');
  }
  if (lowerAnalysis.includes('verified users') || lowerAnalysis.includes('legitimate')) {
    positive.push('Verified community members confirm legitimacy');
  }
  if (lowerAnalysis.includes('good customer service') || lowerAnalysis.includes('responsive support')) {
    positive.push('Responsive customer support mentioned');
  }
  if (lowerAnalysis.includes('transparent') || lowerAnalysis.includes('clear terms')) {
    positive.push('Transparent business practices');
  }

  // Parse warning signals from analysis
  if (lowerAnalysis.includes('concerns') || lowerAnalysis.includes('complaints')) {
    warning.push('Community concerns detected');
  }
  if (lowerAnalysis.includes('refund') || lowerAnalysis.includes('payment delays')) {
    warning.push('Payment and refund issues reported');
  }
  if (lowerAnalysis.includes('customer support') && lowerAnalysis.includes('issue')) {
    warning.push('Customer support response time concerns');
  }
  if (lowerAnalysis.includes('mixed reviews') || lowerAnalysis.includes('divided')) {
    warning.push('Mixed community opinions');
  }

  // Defaults
  if (positive.length === 0) {
    positive.push('Community discussions found', 'Multiple user perspectives available');
  }
  if (warning.length === 0) {
    warning.push('Limited feedback available', 'Proceed with standard caution');
  }

  return { positive: positive.slice(0, 4), warning: warning.slice(0, 4) };
}

// Generate risk factors from sentiment
function generateRiskFactorsFromSentiment(sentiment, riskScore) {
  const factors = [];

  const totalSentiment = sentiment.positive + sentiment.negative;
  const negativePercent = totalSentiment > 0 ? Math.round((sentiment.negative / totalSentiment) * 100) : 50;

  if (riskScore > 60) {
    factors.push({
      severity: 'HIGH',
      percentage: negativePercent,
      description: 'Significant negative community feedback'
    });
  } else if (riskScore > 30) {
    factors.push({
      severity: 'MEDIUM',
      percentage: negativePercent,
      description: 'Mixed community sentiment'
    });
  } else {
    factors.push({
      severity: 'LOW',
      percentage: negativePercent,
      description: 'Mostly positive feedback with minor concerns'
    });
  }

  if (sentiment.negative > 20) {
    factors.push({
      severity: 'MEDIUM',
      percentage: 40,
      description: 'Notable number of negative experiences'
    });
  }

  return factors;
}

// Generate recommendations based on risk score
function generateRecommendations(riskScore) {
  const recommendations = [
    { type: 'do', text: 'Use credit card for payment protection' },
    { type: 'do', text: 'Research independently before committing' }
  ];

  if (riskScore > 50) {
    recommendations.push(
      { type: 'warning', text: 'High risk detected - proceed with extreme caution' },
      { type: 'warning', text: 'Consider alternative options' }
    );
  } else if (riskScore > 30) {
    recommendations.push(
      { type: 'warning', text: 'Mixed reviews - verify credentials carefully' },
      { type: 'do', text: 'Read recent reviews and experiences' }
    );
  } else {
    recommendations.push(
      { type: 'do', text: 'Check terms and conditions' },
      { type: 'do', text: 'Keep records of all transactions' }
    );
  }

  return recommendations;
}

// Storage helper functions
async function saveToStorage(key, value) {
  try {
    await chrome.storage.local.set({ [key]: value });
    return true;
  } catch (error) {
    console.error('Storage save error:', error);
    return false;
  }
}

async function getFromStorage(key) {
  try {
    const result = await chrome.storage.local.get([key]);
    return result[key] || null;
  } catch (error) {
    console.error('Storage get error:', error);
    return null;
  }
}

// Clean up old analysis data periodically
chrome.alarms.create('cleanupStorage', { periodInMinutes: 60 });

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'cleanupStorage') {
    cleanupOldAnalyses();
  }
});

async function cleanupOldAnalyses() {
  try {
    const result = await chrome.storage.local.get(['searchHistory']);
    let history = result.searchHistory || [];

    // Keep only last 50 items
    if (history.length > 50) {
      history = history.slice(0, 50);
      await chrome.storage.local.set({ searchHistory: history });
    }

    // Remove analyses older than 7 days
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

    history = history.filter(item => {
      const itemDate = new Date(item.timestamp);
      return itemDate > sevenDaysAgo;
    });

    await chrome.storage.local.set({ searchHistory: history });
    console.log('Storage cleanup completed');
  } catch (error) {
    console.error('Storage cleanup error:', error);
  }
}
