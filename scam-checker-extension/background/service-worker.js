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
  console.log('[Scam Checker BG] Analyzing URL:', data.domain);

  // Skip API call for now, use mock data immediately
  console.log('[Scam Checker BG] Using mock data (API not configured)');
  return { success: true, data: generateMockAnalysis(data) };

  /* Commented out API call - enable when backend is ready
  try {
    const apiUrl = 'http://localhost:8000/api/analyze';

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);

    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        url: data.url,
        domain: data.domain,
        content: data.content,
        timestamp: data.timestamp
      }),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (response.ok) {
      const result = await response.json();
      return { success: true, data: result };
    } else {
      throw new Error('API request failed');
    }
  } catch (apiError) {
    console.log('[Scam Checker BG] API not available, using mock data');
    return { success: true, data: generateMockAnalysis(data) };
  }
  */
}

// Generate mock analysis data for demonstration/fallback
function generateMockAnalysis(data) {
  const domain = data.domain || 'unknown';
  const riskScore = Math.floor(Math.random() * 50) + 20; // 20-70 range

  return {
    analysisId: `analysis-${Date.now()}`,
    url: data.url,
    domain: domain,
    riskScore: riskScore,
    sentiment: {
      scam: riskScore / 100,
      legit: 1 - (riskScore / 100)
    },
    metrics: {
      postsAnalyzed: Math.floor(Math.random() * 200) + 50,
      commentsReviewed: Math.floor(Math.random() * 500) + 100,
      positiveSentiment: Math.floor(100 - riskScore),
      negativeSentiment: riskScore
    },
    indicators: {
      positive: [
        'Active community discussions found',
        'Multiple verified user testimonials',
        'Consistent positive feedback across threads',
        'Good customer service response mentioned',
        'Transparent business practices noted'
      ].slice(0, Math.floor(Math.random() * 3) + 2),
      warning: [
        'Some refund complaints reported',
        'Mixed reviews on customer support',
        'Payment processing delays mentioned',
        'Limited company information available',
        'Recent negative experiences shared'
      ].slice(0, Math.floor(Math.random() * 3) + 2)
    },
    riskFactors: [
      {
        severity: riskScore >= 50 ? 'HIGH' : 'MEDIUM',
        percentage: Math.floor(Math.random() * 30) + 40,
        description: 'Customer service response time concerns'
      },
      {
        severity: 'MEDIUM',
        percentage: Math.floor(Math.random() * 20) + 30,
        description: 'Refund policy complaints'
      },
      {
        severity: 'LOW',
        percentage: Math.floor(Math.random() * 20) + 15,
        description: 'Website transparency issues'
      }
    ],
    recommendations: [
      {
        type: 'do',
        text: 'Use credit card for payment protection'
      },
      {
        type: 'do',
        text: 'Screenshot all transaction confirmations'
      },
      {
        type: 'do',
        text: 'Verify seller credentials independently'
      },
      {
        type: 'warning',
        text: 'Read terms and conditions carefully'
      },
      {
        type: 'warning',
        text: 'Be prepared for potential support delays'
      },
      {
        type: 'warning',
        text: 'Check return/refund policy before purchase'
      }
    ],
    redditPosts: [
      {
        id: '1',
        title: `Has anyone used ${domain}? Looking for reviews`,
        subreddit: 'AskReddit',
        score: Math.floor(Math.random() * 200) + 50,
        numComments: Math.floor(Math.random() * 50) + 10
      },
      {
        id: '2',
        title: `${domain} - Legit or Scam?`,
        subreddit: 'Reviews',
        score: Math.floor(Math.random() * 150) + 30,
        numComments: Math.floor(Math.random() * 40) + 8
      },
      {
        id: '3',
        title: `My experience with ${domain}`,
        subreddit: 'Ecommerce',
        score: Math.floor(Math.random() * 100) + 20,
        numComments: Math.floor(Math.random() * 30) + 5
      }
    ],
    timestamp: data.timestamp || new Date().toISOString()
  };
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
