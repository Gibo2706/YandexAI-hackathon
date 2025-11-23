// Chrome Storage utility functions

const STORAGE_KEYS = {
  CURRENT_ANALYSIS: 'currentPageAnalysis',
  SEARCH_HISTORY: 'searchHistory',
  USER_SETTINGS: 'userSettings',
  CACHE: 'analysisCache'
};

const DEFAULT_SETTINGS = {
  autoShowButton: true,
  autoAnalyzeEcommerce: false,
  overlayDismissTime: 7000,
  maxHistoryItems: 50,
  enableCache: true,
  cacheDuration: 3600000 // 1 hour in milliseconds
};

class StorageManager {
  /**
   * Save current page analysis
   * @param {Object} analysis - Analysis data
   * @returns {Promise<boolean>}
   */
  static async saveCurrentAnalysis(analysis) {
    try {
      await chrome.storage.local.set({
        [STORAGE_KEYS.CURRENT_ANALYSIS]: {
          ...analysis,
          savedAt: Date.now()
        }
      });
      return true;
    } catch (error) {
      console.error('Failed to save current analysis:', error);
      return false;
    }
  }

  /**
   * Get current page analysis
   * @param {string} url - Page URL to check
   * @returns {Promise<Object|null>}
   */
  static async getCurrentAnalysis(url) {
    try {
      const result = await chrome.storage.local.get([STORAGE_KEYS.CURRENT_ANALYSIS]);
      const analysis = result[STORAGE_KEYS.CURRENT_ANALYSIS];

      if (!analysis) return null;

      // Check if analysis is for the current URL and still valid
      if (analysis.url === url) {
        const settings = await this.getSettings();
        const age = Date.now() - analysis.savedAt;

        if (age < settings.cacheDuration) {
          return analysis;
        }
      }

      return null;
    } catch (error) {
      console.error('Failed to get current analysis:', error);
      return null;
    }
  }

  /**
   * Add analysis to search history
   * @param {Object} analysis - Analysis data
   * @returns {Promise<boolean>}
   */
  static async addToHistory(analysis) {
    try {
      const result = await chrome.storage.local.get([STORAGE_KEYS.SEARCH_HISTORY]);
      let history = result[STORAGE_KEYS.SEARCH_HISTORY] || [];

      // Create history item
      const historyItem = {
        id: Date.now(),
        domain: analysis.domain,
        url: analysis.url,
        riskScore: analysis.riskScore,
        timestamp: analysis.timestamp,
        fullData: analysis
      };

      // Remove duplicates (same domain)
      history = history.filter(item => item.domain !== analysis.domain);

      // Add to beginning
      history.unshift(historyItem);

      // Limit history size
      const settings = await this.getSettings();
      if (history.length > settings.maxHistoryItems) {
        history = history.slice(0, settings.maxHistoryItems);
      }

      await chrome.storage.local.set({ [STORAGE_KEYS.SEARCH_HISTORY]: history });
      return true;
    } catch (error) {
      console.error('Failed to add to history:', error);
      return false;
    }
  }

  /**
   * Get search history
   * @param {number} limit - Number of items to return
   * @returns {Promise<Array>}
   */
  static async getHistory(limit = 10) {
    try {
      const result = await chrome.storage.local.get([STORAGE_KEYS.SEARCH_HISTORY]);
      const history = result[STORAGE_KEYS.SEARCH_HISTORY] || [];
      return history.slice(0, limit);
    } catch (error) {
      console.error('Failed to get history:', error);
      return [];
    }
  }

  /**
   * Clear search history
   * @returns {Promise<boolean>}
   */
  static async clearHistory() {
    try {
      await chrome.storage.local.set({ [STORAGE_KEYS.SEARCH_HISTORY]: [] });
      return true;
    } catch (error) {
      console.error('Failed to clear history:', error);
      return false;
    }
  }

  /**
   * Get user settings
   * @returns {Promise<Object>}
   */
  static async getSettings() {
    try {
      const result = await chrome.storage.local.get([STORAGE_KEYS.USER_SETTINGS]);
      return { ...DEFAULT_SETTINGS, ...result[STORAGE_KEYS.USER_SETTINGS] };
    } catch (error) {
      console.error('Failed to get settings:', error);
      return DEFAULT_SETTINGS;
    }
  }

  /**
   * Update user settings
   * @param {Object} settings - Settings to update
   * @returns {Promise<boolean>}
   */
  static async updateSettings(settings) {
    try {
      const currentSettings = await this.getSettings();
      const newSettings = { ...currentSettings, ...settings };
      await chrome.storage.local.set({ [STORAGE_KEYS.USER_SETTINGS]: newSettings });
      return true;
    } catch (error) {
      console.error('Failed to update settings:', error);
      return false;
    }
  }

  /**
   * Save analysis to cache
   * @param {string} key - Cache key (usually domain)
   * @param {Object} data - Data to cache
   * @returns {Promise<boolean>}
   */
  static async setCache(key, data) {
    try {
      const result = await chrome.storage.local.get([STORAGE_KEYS.CACHE]);
      const cache = result[STORAGE_KEYS.CACHE] || {};

      cache[key] = {
        data,
        cachedAt: Date.now()
      };

      await chrome.storage.local.set({ [STORAGE_KEYS.CACHE]: cache });
      return true;
    } catch (error) {
      console.error('Failed to set cache:', error);
      return false;
    }
  }

  /**
   * Get data from cache
   * @param {string} key - Cache key
   * @returns {Promise<Object|null>}
   */
  static async getCache(key) {
    try {
      const result = await chrome.storage.local.get([STORAGE_KEYS.CACHE]);
      const cache = result[STORAGE_KEYS.CACHE] || {};
      const cached = cache[key];

      if (!cached) return null;

      const settings = await this.getSettings();
      const age = Date.now() - cached.cachedAt;

      if (age < settings.cacheDuration) {
        return cached.data;
      }

      return null;
    } catch (error) {
      console.error('Failed to get cache:', error);
      return null;
    }
  }

  /**
   * Clear all cache
   * @returns {Promise<boolean>}
   */
  static async clearCache() {
    try {
      await chrome.storage.local.set({ [STORAGE_KEYS.CACHE]: {} });
      return true;
    } catch (error) {
      console.error('Failed to clear cache:', error);
      return false;
    }
  }

  /**
   * Get storage usage info
   * @returns {Promise<Object>}
   */
  static async getStorageInfo() {
    try {
      const bytesInUse = await chrome.storage.local.getBytesInUse();
      const quota = chrome.storage.local.QUOTA_BYTES || 5242880; // 5MB default

      return {
        bytesInUse,
        quota,
        percentUsed: ((bytesInUse / quota) * 100).toFixed(2)
      };
    } catch (error) {
      console.error('Failed to get storage info:', error);
      return { bytesInUse: 0, quota: 0, percentUsed: 0 };
    }
  }

  /**
   * Clear old data (cleanup)
   * @param {number} maxAge - Max age in milliseconds
   * @returns {Promise<boolean>}
   */
  static async cleanup(maxAge = 604800000) { // 7 days default
    try {
      const cutoff = Date.now() - maxAge;

      // Clean history
      const historyResult = await chrome.storage.local.get([STORAGE_KEYS.SEARCH_HISTORY]);
      let history = historyResult[STORAGE_KEYS.SEARCH_HISTORY] || [];
      history = history.filter(item => new Date(item.timestamp).getTime() > cutoff);
      await chrome.storage.local.set({ [STORAGE_KEYS.SEARCH_HISTORY]: history });

      // Clean cache
      const cacheResult = await chrome.storage.local.get([STORAGE_KEYS.CACHE]);
      const cache = cacheResult[STORAGE_KEYS.CACHE] || {};
      const cleanedCache = {};

      for (const [key, value] of Object.entries(cache)) {
        if (value.cachedAt > cutoff) {
          cleanedCache[key] = value;
        }
      }

      await chrome.storage.local.set({ [STORAGE_KEYS.CACHE]: cleanedCache });

      return true;
    } catch (error) {
      console.error('Failed to cleanup storage:', error);
      return false;
    }
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = StorageManager;
}

