// API Client utility for backend communication

const API_CONFIG = {
  baseUrl: 'http://localhost:8000/api', // Change this to your backend URL
  timeout: 10000, // 10 seconds
  endpoints: {
    analyze: '/analyze',
    history: '/history',
    feedback: '/feedback'
  }
};

class ApiClient {
  constructor(config = API_CONFIG) {
    this.config = config;
  }

  /**
   * Make a POST request to analyze a URL
   * @param {Object} data - Analysis request data
   * @returns {Promise<Object>} Analysis result
   */
  async analyzeUrl(data) {
    const endpoint = `${this.config.baseUrl}${this.config.endpoints.analyze}`;

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

      const response = await fetch(endpoint, {
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

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      return this.validateAnalysisResponse(result);
    } catch (error) {
      if (error.name === 'AbortError') {
        throw new Error('Request timeout - API took too long to respond');
      }
      console.error('API request failed:', error);
      throw error;
    }
  }

  /**
   * Validate the analysis response structure
   * @param {Object} response - API response
   * @returns {Object} Validated response
   */
  validateAnalysisResponse(response) {
    const required = ['analysisId', 'riskScore', 'sentiment', 'metrics', 'indicators'];

    for (const field of required) {
      if (!(field in response)) {
        throw new Error(`Invalid API response: missing ${field}`);
      }
    }

    // Ensure riskScore is in valid range
    if (response.riskScore < 0 || response.riskScore > 100) {
      response.riskScore = Math.max(0, Math.min(100, response.riskScore));
    }

    // Ensure sentiment values are valid
    if (!response.sentiment.scam || !response.sentiment.legit) {
      response.sentiment = { scam: 0.5, legit: 0.5 };
    }

    return response;
  }

  /**
   * Submit user feedback on an analysis
   * @param {string} analysisId - Analysis ID
   * @param {Object} feedback - User feedback data
   * @returns {Promise<Object>} Submission result
   */
  async submitFeedback(analysisId, feedback) {
    const endpoint = `${this.config.baseUrl}${this.config.endpoints.feedback}`;

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          analysisId,
          feedback,
          timestamp: new Date().toISOString()
        })
      });

      if (!response.ok) {
        throw new Error(`Feedback submission failed: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Feedback submission error:', error);
      throw error;
    }
  }

  /**
   * Get analysis history from backend
   * @param {number} limit - Number of items to retrieve
   * @returns {Promise<Array>} Analysis history
   */
  async getHistory(limit = 10) {
    const endpoint = `${this.config.baseUrl}${this.config.endpoints.history}?limit=${limit}`;

    try {
      const response = await fetch(endpoint, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`History fetch failed: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('History fetch error:', error);
      throw error;
    }
  }

  /**
   * Check if API is available
   * @returns {Promise<boolean>} API availability status
   */
  async checkApiHealth() {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);

      const response = await fetch(`${this.config.baseUrl}/health`, {
        method: 'GET',
        signal: controller.signal
      });

      clearTimeout(timeoutId);
      return response.ok;
    } catch (error) {
      return false;
    }
  }
}

// Export for use in service worker
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ApiClient;
}

