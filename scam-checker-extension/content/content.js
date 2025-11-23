// Content script - injected into all web pages
(function() {
  'use strict';

  let floatingButton = null;
  let quickResultsOverlay = null;
  let isAnalyzing = false;
  let isOverlayFolded = false;

  // Initialize on page load
  function init() {
    // Always create the button - show on ALL pages
    createFloatingButton();
    setupMessageListener();
  }

  // Create the floating "Check This Page" button
  function createFloatingButton() {
    if (floatingButton) return;

    floatingButton = document.createElement('div');
    floatingButton.id = 'scam-checker-floating-btn';
    floatingButton.innerHTML = `
      <div class="sc-btn-close-extension" id="sc-btn-close-ext" title="Hide extension temporarily">×</div>
      <div class="sc-btn-content">
        <img src="${chrome.runtime.getURL('assets/logoP.png')}" class="sc-icon-img" alt="CheckMate Logo">
        <span class="sc-text">Check Page</span>
      </div>
    `;

    floatingButton.querySelector('.sc-btn-content').addEventListener('click', handleCheckPage);
    floatingButton.querySelector('#sc-btn-close-ext').addEventListener('click', (e) => {
      e.stopPropagation();
      hideExtensionCompletely();
    });
    document.body.appendChild(floatingButton);

    // Show immediately on ALL pages
    setTimeout(() => {
      if (floatingButton) {
        floatingButton.classList.add('sc-visible');
      }
    }, 1000); // Show after 1 second on ANY page
  }

  // Check if current site is e-commerce related
  function isEcommerceSite() {
    const domain = window.location.hostname.toLowerCase();
    const ecommerceKeywords = [
      'shop', 'store', 'buy', 'cart', 'checkout', 'product',
      'amazon', 'ebay', 'etsy', 'marketplace', 'temu', 'shein', 'aliexpress', 'wish',
      'kupujem', 'prodajem', 'kupujemprodajem', 'olx', 'njuskalo',
      'polovni', 'oglasi', 'halo', 'limundo'
    ];

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
    // No longer needed - button shows everywhere
    // Keeping function for backwards compatibility
  }

  // Strip images and heavy content from HTML to reduce size
  function cleanHtmlContent(htmlString) {
    // Create temporary DOM parser
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlString, 'text/html');

    // Remove all images
    const images = doc.querySelectorAll('img');
    images.forEach(img => img.remove());

    // Remove all SVGs (can be large)
    const svgs = doc.querySelectorAll('svg');
    svgs.forEach(svg => svg.remove());

    // Remove inline styles with background images
    const elementsWithStyle = doc.querySelectorAll('[style*="background"]');
    elementsWithStyle.forEach(el => {
      const style = el.getAttribute('style');
      if (style && style.includes('background')) {
        el.removeAttribute('style');
      }
    });

    // Remove picture elements
    const pictures = doc.querySelectorAll('picture');
    pictures.forEach(pic => pic.remove());

    // Remove video and audio elements
    const media = doc.querySelectorAll('video, audio, source');
    media.forEach(m => m.remove());

    // Remove canvas elements
    const canvases = doc.querySelectorAll('canvas');
    canvases.forEach(c => c.remove());

    // Remove iframes (can contain heavy content)
    const iframes = doc.querySelectorAll('iframe');
    iframes.forEach(iframe => iframe.remove());

    // Get cleaned HTML
    return doc.documentElement.outerHTML;
  }

  // Handle button click
  async function handleCheckPage() {
    if (isAnalyzing) return;

    console.log('[Scam Checker] ========================================');
    console.log('[Scam Checker] Button clicked, starting analysis...');
    console.log('[Scam Checker] URL:', window.location.href);
    console.log('[Scam Checker] Domain:', window.location.hostname);

    isAnalyzing = true;
    floatingButton.classList.add('sc-analyzing');

    try {
      // Extract and clean HTML - remove images and heavy content
      const fullHtml = document.documentElement.outerHTML;
      console.log('[Scam Checker] Original HTML size:', fullHtml.length, 'chars');

      // Clean HTML - remove images, SVGs, videos, etc.
      const cleanedHtml = cleanHtmlContent(fullHtml);
      console.log('[Scam Checker] After cleaning (no images):', cleanedHtml.length, 'chars');

      // LIMIT to 200KB after cleaning
      const maxHtmlSize = 200000; // 200KB
      const htmlContent = cleanedHtml.length > maxHtmlSize
        ? cleanedHtml.substring(0, maxHtmlSize) + '\n<!-- Content truncated -->'
        : cleanedHtml;

      console.log('[Scam Checker] Final HTML size to send:', htmlContent.length, 'chars');

      // CALL REAL API
      console.log('[Scam Checker] Calling API: https://check-mate.systems/api/analyze-html');

      const apiUrl = 'https://check-mate.systems/api/analyze-html';
      const requestBody = {
        html_content: htmlContent,
        k: 20
      };

      console.log('[Scam Checker] Request payload:', {
        html_content_length: htmlContent.length,
        k: 20
      });

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      console.log('[Scam Checker] API Response status:', response.status);
      console.log('[Scam Checker] API Response headers:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        const errorText = await response.text();
        console.error('[Scam Checker] API Error response:', errorText);
        throw new Error(`API returned ${response.status}: ${errorText}`);
      }

      const apiData = await response.json();
      console.log('[Scam Checker] ✅ API Response received!');
      console.log('[Scam Checker] API Response data:', apiData);

      // Transform API response to extension format
      const analysisData = transformApiResponse(apiData);
      console.log('[Scam Checker] ✅ Data transformed!');
      console.log('[Scam Checker] Analysis data:', analysisData);
      console.log('[Scam Checker] Risk Score:', analysisData.riskScore);

      isAnalyzing = false;
      floatingButton.classList.remove('sc-analyzing');

      // Show results
      console.log('[Scam Checker] ✅ Showing results...');
      showQuickResults(analysisData);

      // Try to save to storage
      try {
        chrome.storage.local.set({ currentPageAnalysis: analysisData });
      } catch (e) {
        console.log('[Scam Checker] Storage error (ignored):', e);
      }

    } catch (error) {
      console.error('[Scam Checker] ========================================');
      console.error('[Scam Checker] ERROR:', error);
      console.error('[Scam Checker] Error type:', error.name);
      console.error('[Scam Checker] Error message:', error.message);
      console.error('[Scam Checker] Error stack:', error.stack);
      console.error('[Scam Checker] ========================================');

      isAnalyzing = false;
      floatingButton.classList.remove('sc-analyzing');
      showErrorMessage('Error: ' + error.message);
    }
  }

  // Transform API response to extension format
  function transformApiResponse(apiResponse) {
    console.log('[Scam Checker] Transforming API response...');
    console.log('[Scam Checker] API response:', apiResponse);

    // Check for combined_verdict (from /analyze-html) or analysis (from /analyze)
    const combinedVerdict = apiResponse.combined_verdict || {};
    const analysisObj = apiResponse.analysis || combinedVerdict;
    const stats = apiResponse.aggregate_stats || {};

    // Extract confidence (0-1 scale from combined_verdict, or 0-100 from analysis)
    let confidence = combinedVerdict.confidence || analysisObj.confidence || 0;
    // Convert to percentage if needed
    if (confidence <= 1) {
      confidence = Math.round(confidence * 100);
    }

    // Use overall_scam_score from combined_verdict if available, otherwise scam_score from analysis
    const scamScore = combinedVerdict.overall_scam_score || analysisObj.scam_score || 50;
    const riskScore = Math.min(100, Math.max(0, Math.round(scamScore)));

    console.log('[Scam Checker] Scam score from API:', scamScore);
    console.log('[Scam Checker] Risk score calculated:', riskScore);
    console.log('[Scam Checker] Confidence:', confidence);

    // Extract indicators from red_flags and green_flags
    const indicators = extractIndicatorsFromAnalysisObject(analysisObj);

    console.log('[Scam Checker] Indicators extracted:', indicators);

    // Extract top posts from enriched results
    const topPosts = (apiResponse.enriched_results || []).slice(0, 5).map(result => ({
      id: result.submission_id || result.id,
      title: result.title,
      subreddit: result.subreddit,
      score: result.score || 0,
      numComments: result.num_comments || 0,
      similarity: result.similarity_score || 0
    }));

    // Calculate sentiment from scam_score (lower scam_score = more legit)
    const scamRatio = scamScore / 100;
    const legitRatio = 1 - scamRatio;

    return {
      analysisId: `api-${Date.now()}`,
      url: window.location.href,
      domain: window.location.hostname,
      riskScore: riskScore,
      confidence: confidence,
      sentiment: {
        scam: scamRatio,
        legit: legitRatio
      },
      metrics: {
        postsAnalyzed: apiResponse.num_discussions_analyzed || 0,
        commentsReviewed: stats.total_discussions || 0,
        positiveSentiment: Math.round(legitRatio * 100),
        negativeSentiment: Math.round(scamRatio * 100)
      },
      indicators: indicators,
      riskFactors: generateRiskFactorsFromScore(scamScore, stats),
      recommendations: generateRecommendations(riskScore),
      redditPosts: topPosts,
      llmAnalysis: analysisObj.summary || analysisObj.reasoning || 'No analysis available',
      aggregateStats: stats,
      analysisObject: analysisObj,
      timestamp: new Date().toISOString()
    };
  }

  // Extract indicators from analysis object (new API format)
  function extractIndicatorsFromAnalysisObject(analysisObj) {
    const positive = [];
    const warning = [];

    // Extract green flags (positive indicators)
    if (analysisObj.green_flags && Array.isArray(analysisObj.green_flags)) {
      analysisObj.green_flags.forEach(flag => {
        if (typeof flag === 'string') {
          positive.push(flag);
        } else if (flag.description) {
          positive.push(flag.description);
        }
      });
    }

    // Extract red flags (warning indicators)
    if (analysisObj.red_flags && Array.isArray(analysisObj.red_flags)) {
      analysisObj.red_flags.forEach(flag => {
        if (typeof flag === 'string') {
          warning.push(flag);
        } else if (flag.description) {
          warning.push(flag.description);
        }
      });
    }

    // Defaults if no flags found
    if (positive.length === 0) {
      positive.push('Community discussions found', 'Multiple user perspectives available');
    }
    if (warning.length === 0) {
      warning.push('Limited feedback available', 'Proceed with standard caution');
    }

    return {
      positive: positive.slice(0, 4),
      warning: warning.slice(0, 4)
    };
  }

  // Generate risk factors from scam score
  function generateRiskFactorsFromScore(scamScore, stats) {
    const factors = [];

    if (scamScore > 60) {
      factors.push({
        severity: 'HIGH',
        percentage: scamScore,
        description: 'High scam probability detected'
      });
    } else if (scamScore > 30) {
      factors.push({
        severity: 'MEDIUM',
        percentage: scamScore,
        description: 'Mixed signals - exercise caution'
      });
    } else {
      factors.push({
        severity: 'LOW',
        percentage: scamScore,
        description: 'Low risk detected'
      });
    }

    // Add scam indicators if present
    const scamIndicators = stats.scam_indicators || {};
    if (scamIndicators.total_scam_mentions > 0) {
      factors.push({
        severity: 'MEDIUM',
        percentage: Math.min(100, scamIndicators.total_scam_mentions * 5),
        description: `${scamIndicators.total_scam_mentions} scam mentions in discussions`
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

  // Show error message overlay
  function showErrorMessage(errorText) {
    const errorOverlay = document.createElement('div');
    errorOverlay.id = 'scam-checker-error';
    errorOverlay.className = 'sc-overlay';

    errorOverlay.innerHTML = `
      <div class="sc-overlay-content" style="background: rgba(231, 76, 60, 0.95);">
        <div class="sc-close-btn" id="sc-error-close">×</div>
        
        <div class="sc-result-header">
          <div class="sc-logo">⚠️</div>
          <h3>Analysis Failed</h3>
        </div>

        <div style="padding: 20px; text-align: center;">
          <p style="color: white; font-size: 14px; line-height: 1.6;">
            ${errorText}
          </p>
          <p style="color: rgba(255,255,255,0.8); font-size: 12px; margin-top: 15px;">
            Check the console (F12) for details
          </p>
        </div>

        <button class="sc-view-full-btn" id="sc-error-retry" style="background: white; color: #e74c3c;">
          Retry
        </button>
      </div>
    `;

    document.body.appendChild(errorOverlay);
    setTimeout(() => errorOverlay.classList.add('sc-visible'), 10);

    document.getElementById('sc-error-close').addEventListener('click', () => {
      errorOverlay.classList.remove('sc-visible');
      setTimeout(() => errorOverlay.remove(), 300);
    });

    document.getElementById('sc-error-retry').addEventListener('click', () => {
      errorOverlay.remove();
      handleCheckPage();
    });

    setTimeout(() => {
      if (errorOverlay.parentNode) {
        errorOverlay.classList.remove('sc-visible');
        setTimeout(() => errorOverlay.remove(), 300);
      }
    }, 10000);
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

  // Helper function to get risk class
  function getRiskClass(riskScore) {
    if (riskScore >= 60) return 'high-risk';
    if (riskScore >= 30) return 'medium-risk';
    return 'low-risk';
  }

  // Helper function to get risk label
  function getRiskLabel(riskScore) {
    if (riskScore >= 60) return 'HIGH RISK';
    if (riskScore >= 30) return 'MEDIUM RISK';
    return 'LOW RISK';
  }

  // Open full analysis in popup
  function openFullAnalysis() {
    chrome.runtime.sendMessage({ action: 'openPopup' });
  }

  // Toggle fold/unfold overlay
  function toggleOverlayFold() {
    if (!quickResultsOverlay) return;

    isOverlayFolded = !isOverlayFolded;
    const content = quickResultsOverlay.querySelector('.sc-overlay-collapsible');
    const foldBtn = quickResultsOverlay.querySelector('#sc-fold-overlay');

    if (isOverlayFolded) {
      content.style.display = 'none';
      foldBtn.innerHTML = '▼';
      foldBtn.title = 'Unfold';
      quickResultsOverlay.style.width = '360px';
    } else {
      content.style.display = 'block';
      foldBtn.innerHTML = '▲';
      foldBtn.title = 'Fold';
      quickResultsOverlay.style.width = '360px';
    }
  }

  // Show quick results overlay
  function showQuickResults(analysisData) {
    // Don't remove existing overlay - just update it if it exists
    if (quickResultsOverlay) {
      // Update existing overlay content
      updateQuickResults(analysisData);
      return;
    }

    quickResultsOverlay = document.createElement('div');
    quickResultsOverlay.id = 'scam-checker-quick-results';
    quickResultsOverlay.className = 'sc-overlay';

    const riskClass = getRiskClass(analysisData.riskScore);
    const riskLabel = getRiskLabel(analysisData.riskScore);
    const confidence = analysisData.confidence || 0;

    quickResultsOverlay.innerHTML = `
      <div class="sc-overlay-content">
        <div class="sc-header-controls">
          <div class="sc-fold-btn" id="sc-fold-overlay" title="Fold">▲</div>
          <div class="sc-close-btn" id="sc-close-overlay" title="Close">×</div>
        </div>
        
        <div class="sc-overlay-collapsible">
          <div class="sc-logo-container">
            <img src="${chrome.runtime.getURL('assets/logoP.png')}" class="sc-overlay-logo" alt="CheckMate Logo">
          </div>
          
          <div class="sc-risk-score ${riskClass}">
            <div class="sc-score-value">${analysisData.riskScore}</div>
            <div class="sc-score-label">${riskLabel}</div>
          </div>
          
          <div class="sc-confidence-container">
            <div class="sc-confidence-label">Confidence</div>
            <div class="sc-confidence-value">${confidence}%</div>
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(quickResultsOverlay);

    // Animate in
    setTimeout(() => quickResultsOverlay.classList.add('sc-visible'), 10);

    // Setup event listeners
    document.getElementById('sc-close-overlay').addEventListener('click', closeQuickResults);
    document.getElementById('sc-fold-overlay').addEventListener('click', toggleOverlayFold);
  }

  // Update existing overlay with new data
  function updateQuickResults(analysisData) {
    if (!quickResultsOverlay) return;

    const riskClass = getRiskClass(analysisData.riskScore);
    const riskLabel = getRiskLabel(analysisData.riskScore);
    const confidence = analysisData.confidence || 0;

    const collapsibleContent = quickResultsOverlay.querySelector('.sc-overlay-collapsible');
    if (collapsibleContent) {
      collapsibleContent.innerHTML = `
        <div class="sc-logo-container">
          <img src="${chrome.runtime.getURL('assets/logoP.png')}" class="sc-overlay-logo" alt="CheckMate Logo">
        </div>
        
        <div class="sc-risk-score ${riskClass}">
          <div class="sc-score-value">${analysisData.riskScore}</div>
          <div class="sc-score-label">${riskLabel}</div>
        </div>
        
        <div class="sc-confidence-container">
          <div class="sc-confidence-label">Confidence</div>
          <div class="sc-confidence-value">${confidence}%</div>
        </div>
      `;
    }

    // Show overlay if it was hidden
    if (!quickResultsOverlay.classList.contains('sc-visible')) {
      setTimeout(() => quickResultsOverlay.classList.add('sc-visible'), 10);
    }
  }

  // Close quick results overlay
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

  function hideExtensionOnPage() {
    // Close overlay first
    closeQuickResults();

    // Hide floating button
    if (floatingButton) {
      floatingButton.classList.remove('sc-visible');
      floatingButton.style.display = 'none';
    }

    // Save preference to not show on this domain
    try {
      const domain = window.location.hostname;
      chrome.storage.local.get(['hiddenDomains'], (result) => {
        const hiddenDomains = result.hiddenDomains || [];
        if (!hiddenDomains.includes(domain)) {
          hiddenDomains.push(domain);
          chrome.storage.local.set({ hiddenDomains: hiddenDomains });
          console.log('[Scam Checker] Extension hidden on domain:', domain);
        }
      });
    } catch (e) {
      console.error('[Scam Checker] Error saving hidden domain:', e);
    }
  }

  // Completely hide extension on current page (temporarily - will return on page reload)
  function hideExtensionCompletely() {
    console.log('[Scam Checker] Hiding extension temporarily (will return on page reload)');

    // Close overlay if open
    if (quickResultsOverlay) {
      quickResultsOverlay.classList.remove('sc-visible');
      setTimeout(() => {
        if (quickResultsOverlay) {
          quickResultsOverlay.remove();
          quickResultsOverlay = null;
        }
      }, 300);
    }

    // Hide and remove floating button
    if (floatingButton) {
      floatingButton.classList.remove('sc-visible');
      setTimeout(() => {
        if (floatingButton) {
          floatingButton.remove();
          floatingButton = null;
        }
      }, 300);
    }

    // DO NOT save to storage - user can reload page to get it back
    console.log('[Scam Checker] Extension hidden temporarily. Reload page to show again.');
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

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
