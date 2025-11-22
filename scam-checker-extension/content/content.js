// Content script - injected into all web pages
(function() {
  'use strict';

  let floatingButton = null;
  let quickResultsOverlay = null;
  let isAnalyzing = false;

  // Initialize on page load
  function init() {
    createFloatingButton();
    setupMessageListener();
    checkIfEcommerceSite();
  }

  // Create the floating "Check This Page" button
  function createFloatingButton() {
    if (floatingButton) return;

    floatingButton = document.createElement('div');
    floatingButton.id = 'scam-checker-floating-btn';
    floatingButton.innerHTML = `
      <div class="sc-btn-content">
        <span class="sc-icon">🛡️</span>
        <span class="sc-text">Check Page</span>
      </div>
    `;

    floatingButton.addEventListener('click', handleCheckPage);
    document.body.appendChild(floatingButton);

    // Show on hover for e-commerce sites
    if (isEcommerceSite()) {
      floatingButton.classList.add('sc-visible');
    }
  }

  // Check if current site is e-commerce related
  function isEcommerceSite() {
    const domain = window.location.hostname.toLowerCase();
    const ecommerceKeywords = ['shop', 'store', 'buy', 'cart', 'checkout', 'product', 'amazon', 'ebay', 'etsy', 'marketplace'];

    // Check domain
    if (ecommerceKeywords.some(keyword => domain.includes(keyword))) {
      return true;
    }

    // Check for common e-commerce elements
    const hasCartIcon = document.querySelector('[class*="cart"], [id*="cart"]');
    const hasCheckout = document.querySelector('[href*="checkout"], [class*="checkout"]');
    const hasAddToCart = document.querySelector('button[class*="add-to-cart"], button[id*="add-to-cart"]');

    return hasCartIcon || hasCheckout || hasAddToCart;
  }

  function checkIfEcommerceSite() {
    if (isEcommerceSite()) {
      setTimeout(() => {
        if (floatingButton) {
          floatingButton.classList.add('sc-visible');
        }
      }, 2000);
    }
  }

  // Handle button click
  async function handleCheckPage() {
    if (isAnalyzing) return;

    console.log('[Scam Checker] Button clicked, starting analysis...');
    isAnalyzing = true;
    floatingButton.classList.add('sc-analyzing');

    // DIRECT MOCK DATA - bypass background script for now
    setTimeout(() => {
      console.log('[Scam Checker] Showing mock results directly...');
      isAnalyzing = false;
      floatingButton.classList.remove('sc-analyzing');

      const mockData = getMockAnalysis();
      showQuickResults(mockData);

      try {
        chrome.storage.local.set({ currentPageAnalysis: mockData });
      } catch (e) {
        console.log('[Scam Checker] Storage error (non-critical):', e);
      }
    }, 500);
  }

  // Extract relevant page data
  function extractPageData() {
    const title = document.title;
    const metaDescription = document.querySelector('meta[name="description"]')?.content || '';

    // Get main content (simplified)
    let content = '';
    const mainContent = document.querySelector('main, article, [role="main"]');
    if (mainContent) {
      content = mainContent.innerText.substring(0, 1000);
    } else {
      content = document.body.innerText.substring(0, 1000);
    }

    return {
      title,
      description: metaDescription,
      content: content.replace(/\s+/g, ' ').trim()
    };
  }

  // Show quick results overlay
  function showQuickResults(analysisData) {
    // Remove existing overlay
    if (quickResultsOverlay) {
      quickResultsOverlay.remove();
    }

    quickResultsOverlay = document.createElement('div');
    quickResultsOverlay.id = 'scam-checker-quick-results';
    quickResultsOverlay.className = 'sc-overlay';

    const riskClass = getRiskClass(analysisData.riskScore);
    const riskLabel = getRiskLabel(analysisData.riskScore);

    quickResultsOverlay.innerHTML = `
      <div class="sc-overlay-content">
        <div class="sc-close-btn" id="sc-close-overlay">×</div>
        
        <div class="sc-result-header">
          <div class="sc-logo">🛡️</div>
          <h3>Page Analysis</h3>
        </div>

        <div class="sc-risk-score ${riskClass}">
          <div class="sc-score-value">${analysisData.riskScore}</div>
          <div class="sc-score-label">${riskLabel}</div>
        </div>

        <div class="sc-quick-indicators">
          ${analysisData.indicators.positive.slice(0, 2).map(item => `
            <div class="sc-indicator positive">
              <span class="sc-ind-icon">✓</span>
              <span class="sc-ind-text">${item}</span>
            </div>
          `).join('')}
          ${analysisData.indicators.warning.slice(0, 2).map(item => `
            <div class="sc-indicator warning">
              <span class="sc-ind-icon">⚠</span>
              <span class="sc-ind-text">${item}</span>
            </div>
          `).join('')}
        </div>

        <button class="sc-view-full-btn" id="sc-view-full">View Full Analysis</button>

        <div class="sc-timer-bar">
          <div class="sc-timer-fill"></div>
        </div>
      </div>
    `;

    document.body.appendChild(quickResultsOverlay);

    // Animate in
    setTimeout(() => quickResultsOverlay.classList.add('sc-visible'), 10);

    // Setup event listeners
    document.getElementById('sc-close-overlay').addEventListener('click', closeQuickResults);
    document.getElementById('sc-view-full').addEventListener('click', openFullAnalysis);

    // Auto-dismiss after 7 seconds
    const timerFill = quickResultsOverlay.querySelector('.sc-timer-fill');
    timerFill.style.animation = 'sc-timer-progress 7s linear forwards';

    setTimeout(() => {
      closeQuickResults();
    }, 7000);
  }

  function closeQuickResults() {
    if (quickResultsOverlay) {
      quickResultsOverlay.classList.remove('sc-visible');
      setTimeout(() => {
        if (quickResultsOverlay) {
          quickResultsOverlay.remove();
          quickResultsOverlay = null;
        }
      }, 300);
    }
  }

  function openFullAnalysis() {
    closeQuickResults();
    // Open extension popup (this will be handled by clicking the extension icon)
    chrome.runtime.sendMessage({ action: 'openPopup' });
  }

  function getRiskClass(score) {
    if (score >= 70) return 'high-risk';
    if (score >= 40) return 'medium-risk';
    return 'low-risk';
  }

  function getRiskLabel(score) {
    if (score >= 70) return 'High Risk';
    if (score >= 40) return 'Medium Risk';
    return 'Low Risk';
  }

  // Setup message listener for popup communication
  function setupMessageListener() {
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      if (request.action === 'getPageContent') {
        const pageData = extractPageData();
        sendResponse({ content: pageData.content });
      }
      return true;
    });
  }

  // Mock analysis data
  function getMockAnalysis() {
    const domain = window.location.hostname;
    return {
      analysisId: `mock-${Date.now()}`,
      url: window.location.href,
      domain: domain,
      riskScore: Math.floor(Math.random() * 40) + 20, // 20-60 range
      sentiment: { scam: 0.21, legit: 0.79 },
      metrics: {
        postsAnalyzed: Math.floor(Math.random() * 200) + 50,
        commentsReviewed: Math.floor(Math.random() * 500) + 100,
        positiveSentiment: 79,
        negativeSentiment: 21
      },
      indicators: {
        positive: [
          'Active community discussions',
          'Multiple verified user testimonials',
          'Consistent positive feedback',
          'Good customer service response'
        ],
        warning: [
          'Some refund complaints reported',
          'Mixed reviews on customer support',
          'Payment processing delays mentioned',
          'Limited company information'
        ]
      },
      riskFactors: [
        { severity: 'MEDIUM', percentage: 45, description: 'Occasional customer complaints' },
        { severity: 'LOW', percentage: 25, description: 'Support response time concerns' },
        { severity: 'LOW', percentage: 20, description: 'Pricing transparency issues' }
      ],
      recommendations: [
        { type: 'do', text: 'Use credit card for payment protection' },
        { type: 'do', text: 'Screenshot all transaction confirmations' },
        { type: 'warning', text: 'Read terms and conditions carefully' },
        { type: 'warning', text: 'Verify seller credentials before purchase' }
      ],
      redditPosts: [
        {
          id: '1',
          title: `Has anyone used ${domain}? Experiences?`,
          subreddit: 'AskReddit',
          score: 145,
          numComments: 32
        },
        {
          id: '2',
          title: `${domain} Review Thread`,
          subreddit: 'Reviews',
          score: 89,
          numComments: 21
        }
      ],
      timestamp: new Date().toISOString()
    };
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
