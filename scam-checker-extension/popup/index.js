console.log('🚀 Popup script loaded');

// DOM elements
const loading = document.getElementById('loading');
const noAnalysis = document.getElementById('no-analysis');
const results = document.getElementById('results');

// Show/hide views
function showLoading() {
  loading.style.display = 'block';
  noAnalysis.style.display = 'none';
  results.style.display = 'none';
}

function showNoAnalysis() {
  loading.style.display = 'none';
  noAnalysis.style.display = 'block';
  results.style.display = 'none';
}

function showResults() {
  loading.style.display = 'none';
  noAnalysis.style.display = 'none';
  results.style.display = 'block';
}

// Populate results
function displayResults(data) {
  console.log('📊 Displaying results:', data);
  
  // Extract data
  const analysis = data.analysisObject || data.analysis || {};
  const stats = data.aggregateStats || data.aggregate_stats || {};
  
  const scamScore = analysis.scam_score !== undefined ? analysis.scam_score : data.riskScore || 0;
  const confidence = analysis.confidence !== undefined ? analysis.confidence : data.confidence || 0;
  const summary = analysis.summary || data.llmAnalysis || 'No summary available';
  const recommendation = analysis.recommendation || 'CAUTION';
  const redFlags = analysis.red_flags || [];
  const greenFlags = analysis.green_flags || [];
  
  const totalDiscussions = stats.total_discussions || 0;
  const scamMentions = stats.scam_indicators?.total_scam_mentions || 0;
  const positiveVouches = stats.scam_indicators?.total_positive_vouches || 0;
  const avgCredibility = stats.avg_discussion_credibility || 0;
  
  // Update DOM
  document.getElementById('domain-name').textContent = data.domain || 'Analysis Results';
  document.getElementById('scam-score').textContent = scamScore;
  document.getElementById('confidence').textContent = confidence + '%';
  document.getElementById('summary').textContent = summary;
  document.getElementById('recommendation-text').textContent = recommendation;
  
  // Stats
  document.getElementById('discussions').textContent = totalDiscussions;
  document.getElementById('scam-mentions').textContent = scamMentions;
  document.getElementById('positive-vouches').textContent = positiveVouches;
  document.getElementById('avg-credibility').textContent = avgCredibility.toFixed(1);
  
  // Red flags
  const redFlagsList = document.getElementById('red-flags');
  if (redFlags.length > 0) {
    redFlagsList.innerHTML = redFlags.map(flag => 
      `<li>${typeof flag === 'string' ? flag : flag.description || flag}</li>`
    ).join('');
  } else {
    redFlagsList.innerHTML = '<li>No red flags detected</li>';
  }
  
  // Green flags
  const greenFlagsList = document.getElementById('green-flags');
  if (greenFlags.length > 0) {
    greenFlagsList.innerHTML = greenFlags.map(flag => 
      `<li>${typeof flag === 'string' ? flag : flag.description || flag}</li>`
    ).join('');
  } else {
    greenFlagsList.innerHTML = '<li>No green flags detected</li>';
  }
  
  // Update score card color based on risk
  const scoreCard = document.querySelector('.score-card');
  if (scamScore >= 70) {
    scoreCard.style.background = 'rgba(239, 68, 68, 0.3)'; // Red
  } else if (scamScore >= 40) {
    scoreCard.style.background = 'rgba(251, 191, 36, 0.3)'; // Yellow
  } else {
    scoreCard.style.background = 'rgba(34, 197, 94, 0.3)'; // Green
  }
  
  showResults();
}

// Load analysis from storage
async function loadAnalysis() {
  console.log('📂 Loading analysis from storage...');
  
  try {
    // Get current tab URL first
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const currentUrl = tab?.url || '';
    const currentDomain = currentUrl ? new URL(currentUrl).hostname : '';
    
    console.log('📍 Current page:', currentDomain);
    
    const result = await chrome.storage.local.get(['currentPageAnalysis']);
    console.log('💾 Storage result:', result);
    
    if (result.currentPageAnalysis) {
      const storedUrl = result.currentPageAnalysis.pageUrl || result.currentPageAnalysis.url || '';
      const storedDomain = result.currentPageAnalysis.pageDomain || result.currentPageAnalysis.domain || '';
      
      console.log('💾 Stored analysis for:', storedDomain);
      console.log('🔍 Comparing:', { current: currentDomain, stored: storedDomain });
      
      // Check if analysis is for current page
      if (storedDomain === currentDomain || storedUrl === currentUrl) {
        // Check if not too old (max 1 hour)
        const savedAt = result.currentPageAnalysis.savedAt || result.currentPageAnalysis.timestamp;
        const age = savedAt ? (Date.now() - new Date(savedAt).getTime()) / 1000 / 60 : 999;
        
        console.log(`⏰ Analysis age: ${age.toFixed(0)} minutes`);
        
        if (age < 60) {
          console.log('✅ Using stored analysis (fresh & same page)');
          displayResults(result.currentPageAnalysis);
        } else {
          console.log('⚠️ Analysis too old (>1 hour)');
          showNoAnalysis();
        }
      } else {
        console.log('⚠️ Analysis is for different page');
        showNoAnalysis();
      }
    } else {
      console.log('❌ No analysis found in storage');
      showNoAnalysis();
    }
  } catch (error) {
    console.error('❌ Error loading analysis:', error);
    showNoAnalysis();
  }
}

// Analyze current page
async function analyzeCurrentPage() {
  console.log('🔍 Starting analysis...');
  
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (tab && tab.id) {
      // Trigger content script to analyze
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => {
          const btn = document.querySelector('#scam-checker-floating-btn .sc-btn-content');
          if (btn) {
            btn.click();
          } else {
            console.error('Check Page button not found');
          }
        }
      });
      
      // Close popup after triggering
      window.close();
    }
  } catch (error) {
    console.error('❌ Error analyzing page:', error);
    alert('Error: ' + error.message);
  }
}

// Event listeners
document.getElementById('btn-analyze')?.addEventListener('click', analyzeCurrentPage);
document.getElementById('btn-reanalyze')?.addEventListener('click', analyzeCurrentPage);
document.getElementById('btn-back')?.addEventListener('click', showNoAnalysis);
document.getElementById('btn-clear-storage')?.addEventListener('click', async () => {
  await chrome.storage.local.clear();
  console.log('🗑️ Storage cleared');
  alert('Storage cleared! Refresh this popup.');
  window.close();
});

// Initialize
console.log('🎬 Initializing popup...');
showLoading();
loadAnalysis();
