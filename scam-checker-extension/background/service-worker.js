// Background Service Worker - handles API communication
chrome.runtime.onInstalled.addListener(() => {
  console.log('[Scam Checker BG] Extension installed');
});

// Listen for messages from content script and popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('[Scam Checker BG] Message received:', request.action);

  if (request.action === 'analyzeUrl') {
    handleAnalyzeUrl(request.data)
      .then(result => {
        console.log('[Scam Checker BG] Sending response:', result);
        sendResponse(result);
      })
      .catch(error => {
        console.error('[Scam Checker BG] Error:', error);
        sendResponse({ success: false, error: error.message });
      });
    return true; // Keep channel open for async response
  }

  if (request.action === 'openPopup') {
    chrome.action.openPopup();
    sendResponse({ success: true });
    return false;
  }
});

// Handle URL analysis
async function handleAnalyzeUrl(data) {
  console.log('[Scam Checker BG] ========== STARTING ANALYSIS ==========');
  console.log('[Scam Checker BG] Analyzing URL:', data.domain);
  console.log('[Scam Checker BG] Full data:', JSON.stringify(data, null, 2));

  try {
    // STEP 1: Call /search endpoint
    const searchUrl = 'https://www.check-mate.systems/api/search';
    const searchQuery = `${data.domain} reviews scam legit trustworthy experiences`;

    console.log('[Scam Checker BG] Step 1: Calling /search endpoint');
    console.log('[Scam Checker BG] Search URL:', searchUrl);
    console.log('[Scam Checker BG] Search query:', searchQuery);

    const searchController = new AbortController();
    const searchTimeoutId = setTimeout(() => searchController.abort(), 20000);

    const searchResponse = await fetch(searchUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: searchQuery,
        k: 20
      }),
      signal: searchController.signal
    });

    clearTimeout(searchTimeoutId);

    console.log('[Scam Checker BG] Search response status:', searchResponse.status);
    console.log('[Scam Checker BG] Search response headers:', JSON.stringify([...searchResponse.headers.entries()]));

    if (!searchResponse.ok) {
      const errorText = await searchResponse.text();
      console.error('[Scam Checker BG] Search API error response:', errorText);
      throw new Error(`Search API returned ${searchResponse.status}: ${errorText}`);
    }

    const searchResults = await searchResponse.json();
    console.log('[Scam Checker BG] ✅ Search results received!');
    console.log('[Scam Checker BG] Number of results:', searchResults.length);
    console.log('[Scam Checker BG] First result sample:', JSON.stringify(searchResults[0], null, 2));
    console.log('[Scam Checker BG] All search results:', JSON.stringify(searchResults, null, 2));

    if (!searchResults || searchResults.length === 0) {
      console.warn('[Scam Checker BG] ⚠️ No search results found for query');
      throw new Error('No search results found');
    }

    // STEP 2: Call /analyze endpoint with search results
    const analyzeUrl = 'https://www.check-mate.systems/api/analyze';

    console.log('[Scam Checker BG] Step 2: Calling /analyze endpoint');
    console.log('[Scam Checker BG] Analyze URL:', analyzeUrl);
    console.log('[Scam Checker BG] Sending', searchResults.length, 'results to analyze');

    const analyzeController = new AbortController();
    const analyzeTimeoutId = setTimeout(() => analyzeController.abort(), 30000);

    const analyzeResponse = await fetch(analyzeUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: searchQuery,
        search_results: searchResults
      }),
      signal: analyzeController.signal
    });

    clearTimeout(analyzeTimeoutId);

    console.log('[Scam Checker BG] Analyze response status:', analyzeResponse.status);
    console.log('[Scam Checker BG] Analyze response headers:', JSON.stringify([...analyzeResponse.headers.entries()]));

    if (!analyzeResponse.ok) {
      const errorText = await analyzeResponse.text();
      console.error('[Scam Checker BG] Analyze API error response:', errorText);
      throw new Error(`Analyze API returned ${analyzeResponse.status}: ${errorText}`);
    }

    const analyzeResults = await analyzeResponse.json();
    console.log('[Scam Checker BG] ✅ Analyze results received!');
    console.log('[Scam Checker BG] Analysis data:', JSON.stringify(analyzeResults, null, 2));

    // STEP 3: Call /stats endpoint for statistics
    const statsUrl = 'https://www.check-mate.systems/api/stats';

    console.log('[Scam Checker BG] Step 3: Calling /stats endpoint');
    console.log('[Scam Checker BG] Stats URL:', statsUrl);

    const statsController = new AbortController();
    const statsTimeoutId = setTimeout(() => statsController.abort(), 20000);

    const statsResponse = await fetch(statsUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: searchQuery,
        search_results: searchResults
      }),
      signal: statsController.signal
    });

    clearTimeout(statsTimeoutId);

    console.log('[Scam Checker BG] Stats response status:', statsResponse.status);

    if (!statsResponse.ok) {
      const errorText = await statsResponse.text();
      console.error('[Scam Checker BG] Stats API error response:', errorText);
      throw new Error(`Stats API returned ${statsResponse.status}: ${errorText}`);
    }

    const statsResults = await statsResponse.json();
    console.log('[Scam Checker BG] ✅ Stats results received!');
    console.log('[Scam Checker BG] Statistics data:', JSON.stringify(statsResults, null, 2));

    // STEP 4: Transform combined results
    console.log('[Scam Checker BG] Step 4: Transforming combined results');

    const transformedData = transformBackendResponse({
      search_results: searchResults,
      llm_analysis: analyzeResults.analysis,
      statistics: statsResults.statistics
    }, data);

    console.log('[Scam Checker BG] ✅ Transformation complete!');
    console.log('[Scam Checker BG] Final transformed data:', JSON.stringify(transformedData, null, 2));
    console.log('[Scam Checker BG] ========== ANALYSIS COMPLETE ==========');

    return { success: true, data: transformedData };

  } catch (error) {
    console.error('[Scam Checker BG] ❌ ERROR:', error);
    console.error('[Scam Checker BG] Error name:', error.name);
    console.error('[Scam Checker BG] Error message:', error.message);
    console.error('[Scam Checker BG] Error stack:', error.stack);

    // NO MOCK DATA FALLBACK - show error to user
    throw error;
  }
}

// Transform backend response to match extension format
function transformBackendResponse(backendData, requestData) {
  const stats = backendData.statistics || {};
  const sentiment = stats.sentiment_indicators || {};
  const engagement = stats.engagement_stats || {};

  // Calculate risk score based on sentiment
  const positiveComments = sentiment.positive_comments || 0;
  const negativeComments = sentiment.negative_comments || 0;
  const totalComments = sentiment.total_comments || 1;

  const negativeRatio = negativeComments / totalComments;
  const riskScore = Math.min(100, Math.max(0, Math.round(negativeRatio * 100)));

  // Extract top posts from search results
  const topPosts = (backendData.search_results || []).slice(0, 5).map(result => {
    const doc = result.full_doc || {};
    const post = doc.post || {};
    return {
      id: post.id || result.submission_id,
      title: post.title || result.title,
      subreddit: post.subreddit || result.subreddit,
      score: post.score || result.score || 0,
      numComments: post.num_comments || result.num_comments || 0
    };
  });

  // Extract positive and warning indicators from LLM analysis
  const llmAnalysis = backendData.llm_analysis || '';
  const indicators = extractIndicators(llmAnalysis, sentiment);

  return {
    analysisId: `backend-${Date.now()}`,
    url: requestData.url,
    domain: requestData.domain,
    riskScore: riskScore,
    sentiment: {
      scam: negativeRatio,
      legit: 1 - negativeRatio
    },
    metrics: {
      postsAnalyzed: stats.total_discussions || 0,
      commentsReviewed: totalComments,
      positiveSentiment: Math.round((positiveComments / totalComments) * 100),
      negativeSentiment: Math.round((negativeComments / totalComments) * 100)
    },
    indicators: indicators,
    riskFactors: generateRiskFactors(sentiment, riskScore),
    recommendations: generateRecommendations(riskScore),
    redditPosts: topPosts,
    llmAnalysis: llmAnalysis,
    timestamp: new Date().toISOString()
  };
}

// Extract indicators from LLM analysis and sentiment data
function extractIndicators(llmAnalysis, sentiment) {
  const positive = [];
  const warning = [];

  const avgPostScore = sentiment.avg_post_score || 0;
  const avgCommentScore = sentiment.avg_comment_score || 0;
  const positiveComments = sentiment.positive_comments || 0;
  const negativeComments = sentiment.negative_comments || 0;

  // Positive indicators
  if (avgPostScore > 10) {
    positive.push('High community engagement and upvotes');
  }
  if (positiveComments > negativeComments * 2) {
    positive.push('Majority of comments are positive');
  }
  if (avgCommentScore > 5) {
    positive.push('Well-received community discussions');
  }

  // Parse LLM analysis for key points
  if (llmAnalysis.toLowerCase().includes('legit') || llmAnalysis.toLowerCase().includes('trustworthy')) {
    positive.push('Community indicates legitimacy');
  }
  if (llmAnalysis.toLowerCase().includes('good experience') || llmAnalysis.toLowerCase().includes('positive')) {
    positive.push('Positive user experiences reported');
  }

  // Warning indicators
  if (negativeComments > positiveComments) {
    warning.push('More negative than positive feedback');
  }
  if (avgPostScore < 5) {
    warning.push('Low community engagement');
  }
  if (llmAnalysis.toLowerCase().includes('scam') || llmAnalysis.toLowerCase().includes('fraud')) {
    warning.push('Scam concerns mentioned in discussions');
  }
  if (llmAnalysis.toLowerCase().includes('avoid') || llmAnalysis.toLowerCase().includes('warning')) {
    warning.push('Community warnings detected');
  }

  // Defaults if empty
  if (positive.length === 0) {
    positive.push('Community discussions found', 'Multiple perspectives available');
  }
  if (warning.length === 0) {
    warning.push('Limited community feedback', 'Proceed with caution');
  }

  return { positive, warning };
}

// Generate risk factors based on sentiment
function generateRiskFactors(sentiment, riskScore) {
  const factors = [];

  const negativeComments = sentiment.negative_comments || 0;
  const totalComments = sentiment.total_comments || 1;
  const negativePercent = Math.round((negativeComments / totalComments) * 100);

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
      description: 'Mixed community sentiment detected'
    });
  }

  if (sentiment.avg_comment_score < 0) {
    factors.push({
      severity: 'MEDIUM',
      percentage: 40,
      description: 'Below-average comment ratings'
    });
  }

  if (totalComments < 10) {
    factors.push({
      severity: 'LOW',
      percentage: 25,
      description: 'Limited community discussion available'
    });
  }

  return factors.length > 0 ? factors : [{
    severity: 'LOW',
    percentage: 20,
    description: 'General caution recommended'
  }];
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
