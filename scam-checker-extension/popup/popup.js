const { createApp } = Vue;

createApp({
  data() {
    return {
      searchQuery: '',
      loading: false,
      currentAnalysis: null,
      history: [],
      currentPageUrl: '',
      currentPageDomain: ''
    };
  },
  mounted() {
    this.loadHistory();
    this.getCurrentPageInfo();
    this.checkForExistingAnalysis();
  },
  methods: {
    async getCurrentPageInfo() {
      try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        if (tab && tab.url) {
          this.currentPageUrl = tab.url;
          this.currentPageDomain = new URL(tab.url).hostname;
        }
      } catch (error) {
        console.error('Error getting current page:', error);
      }
    },

    async checkForExistingAnalysis() {
      if (!this.currentPageUrl) return;

      try {
        const result = await chrome.storage.local.get(['currentPageAnalysis']);
        if (result.currentPageAnalysis && result.currentPageAnalysis.url === this.currentPageUrl) {
          // Check if analysis is recent (within last hour)
          const analysisTime = new Date(result.currentPageAnalysis.timestamp);
          const now = new Date();
          const hoursDiff = (now - analysisTime) / (1000 * 60 * 60);

          if (hoursDiff < 1) {
            this.currentAnalysis = result.currentPageAnalysis;
          }
        }
      } catch (error) {
        console.error('Error checking existing analysis:', error);
      }
    },

    async loadHistory() {
      try {
        const result = await chrome.storage.local.get(['searchHistory']);
        this.history = result.searchHistory || [];
      } catch (error) {
        console.error('Error loading history:', error);
      }
    },

    async analyzeCurrentPage() {
      if (!this.currentPageUrl) {
        alert('Cannot analyze this page');
        return;
      }

      this.loading = true;

      try {
        // Send message to content script to get page content
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        chrome.tabs.sendMessage(tab.id, { action: 'getPageContent' }, async (response) => {
          if (chrome.runtime.lastError) {
            console.error('Error:', chrome.runtime.lastError);
            await this.performAnalysis(this.currentPageUrl, this.currentPageDomain, '');
            return;
          }

          const pageContent = response?.content || '';
          await this.performAnalysis(this.currentPageUrl, this.currentPageDomain, pageContent);
        });
      } catch (error) {
        console.error('Error analyzing current page:', error);
        this.loading = false;
        alert('Error analyzing page. Please try again.');
      }
    },

    async analyzeManual() {
      if (!this.searchQuery.trim()) return;

      this.loading = true;
      try {
        await this.performAnalysis(this.searchQuery, this.searchQuery, '');
      } catch (error) {
        console.error('Error analyzing:', error);
        this.loading = false;
        alert('Error analyzing. Please try again.');
      }
    },

    async performAnalysis(url, domain, content) {
      try {
        // Send to background script for API call
        const response = await chrome.runtime.sendMessage({
          action: 'analyzeUrl',
          data: {
            url: url,
            domain: domain,
            content: content,
            timestamp: new Date().toISOString()
          }
        });

        if (response.success) {
          this.currentAnalysis = {
            ...response.data,
            url: url,
            domain: domain,
            timestamp: new Date().toISOString()
          };

          // Save to storage
          await this.saveAnalysis(this.currentAnalysis);
        } else {
          throw new Error(response.error || 'Analysis failed');
        }
      } catch (error) {
        console.error('Analysis error:', error);
        // Use mock data for demonstration
        this.currentAnalysis = this.getMockAnalysis(url, domain);
        await this.saveAnalysis(this.currentAnalysis);
      } finally {
        this.loading = false;
      }
    },

    async saveAnalysis(analysis) {
      try {
        // Save current page analysis
        await chrome.storage.local.set({ currentPageAnalysis: analysis });

        // Add to history
        const historyItem = {
          id: Date.now(),
          domain: analysis.domain,
          riskScore: analysis.riskScore,
          timestamp: analysis.timestamp,
          fullData: analysis
        };

        this.history.unshift(historyItem);
        if (this.history.length > 10) {
          this.history = this.history.slice(0, 10);
        }

        await chrome.storage.local.set({ searchHistory: this.history });
      } catch (error) {
        console.error('Error saving analysis:', error);
      }
    },

    loadAnalysis(historyItem) {
      this.currentAnalysis = historyItem.fullData;
    },

    backToSearch() {
      this.currentAnalysis = null;
      this.searchQuery = '';
    },

    getScoreClass(score) {
      if (score >= 70) return 'high-risk';
      if (score >= 40) return 'medium-risk';
      return 'low-risk';
    },

    formatTime(timestamp) {
      const date = new Date(timestamp);
      const now = new Date();
      const diffMs = now - date;
      const diffMins = Math.floor(diffMs / 60000);

      if (diffMins < 60) return `${diffMins}m ago`;
      const diffHours = Math.floor(diffMins / 60);
      if (diffHours < 24) return `${diffHours}h ago`;
      return `${Math.floor(diffHours / 24)}d ago`;
    },

    getMockAnalysis(url, domain) {
      // Mock data matching the original Vue app structure
      return {
        analysisId: `mock-${Date.now()}`,
        url: url,
        domain: domain,
        riskScore: 35,
        sentiment: { scam: 0.21, legit: 0.79 },
        metrics: {
          postsAnalyzed: 156,
          commentsReviewed: 420,
          positiveSentiment: 79,
          negativeSentiment: 21
        },
        indicators: {
          positive: [
            'Multiple verified user testimonials',
            'Consistent positive feedback across subreddits',
            'Good customer service response rate'
          ],
          warning: [
            'Some refund complaints reported',
            'Mixed reviews on customer support',
            'Payment processing delays mentioned'
          ]
        },
        riskFactors: [
          { severity: 'MEDIUM', percentage: 45, description: 'Occasional refund issues' },
          { severity: 'LOW', percentage: 25, description: 'Customer support delays' },
          { severity: 'LOW', percentage: 20, description: 'Pricing complaints' }
        ],
        recommendations: [
          { type: 'do', text: 'Use credit card for payment protection' },
          { type: 'do', text: 'Screenshot all booking confirmations' },
          { type: 'warning', text: 'Be prepared for potential support delays' },
          { type: 'warning', text: 'Read refund policy carefully before purchase' }
        ],
        redditPosts: [
          {
            id: '1',
            title: 'Anyone have experience with this site?',
            subreddit: 'AskReddit',
            score: 145,
            numComments: 32
          },
          {
            id: '2',
            title: 'Review - My experience so far',
            subreddit: 'Reviews',
            score: 89,
            numComments: 21
          }
        ],
        timestamp: new Date().toISOString()
      };
    }
  }
}).mount('#app');

