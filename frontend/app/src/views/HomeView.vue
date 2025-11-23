<template>
  <div class="home">
    <!-- Enhanced Progress Bar Loader -->
    <div v-if="isLoading" class="global-loader-overlay">
      <div class="progress-container">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="progress-text">{{ loadingMessage }}</div>
        <div class="progress-percentage">{{ loadingProgress }}%</div>
      </div>
    </div>

    <div class="content-wrapper">
      <div class="logo-container">
        <img alt="Reddit logo" src="../assets/logoP.png" class="logo">
      </div>
      
      <h1 class="main-title">CheckMate</h1>
      <p class="subtitle">CheckMate to Scammers. Real Reviews. Real Protection.</p>
      <p class="description">Check any website name, seller, service, or product through authentic Reddit discussions, along with technical and content checks. Our AI analyzes thousands of real human experiences to guide your decisions.</p>
      
      <!-- Recent Searches -->
      <div v-if="recentSearches.length > 0" class="recent-searches">
        <h3 class="recent-title"><i class="fas fa-history"></i> Recent Searches</h3>
        <div class="recent-items">
          <button 
            v-for="(search, index) in recentSearches" 
            :key="index"
            @click="selectRecentSearch(search)"
            class="recent-item"
          >
            <i class="fas fa-search"></i>
            {{ search }}
          </button>
        </div>
      </div>
      
      <div class="search-section">
        <div class="input-wrapper">
          <input 
            type="text" 
            v-model="prompt" 
            placeholder="Enter website name, seller, service, or product" 
            class="search-bar"
          />
        </div>
        <button @click="onAnalyzeClick" class="check-button" :disabled="isLoading">
          <span v-if="!isLoading">Analyze</span>
          <span v-else>Analyzing...</span>
        </button>
        
        <!-- Extension Download Button (Desktop Only) -->
        <div class="extension-section">
          <p class="extension-text">
            <i class="fas fa-puzzle-piece"></i> 
            Install our browser extension for instant Reddit analysis while browsing
          </p>
          <a href="#" class="extension-button" target="_blank" rel="noopener noreferrer">
            <i class="fab fa-chrome"></i>
            Download Extension
          </a>
        </div>
      </div>
    </div>

    <footer class="footer">
      <p>&copy; 2025 The Sthrokaders | AI NATION Hackathon by Yandex & Reputeo</p>
    </footer>
  </div>
</template>

<script>
const CACHE_KEY = 'checkmate_cache'
const RECENT_KEY = 'checkmate_recent'
const MAX_RECENT = 3

export default {
  name: 'HomeView',
  data() {
    return {
      prompt: '',
      isLoading: false,
      loadingProgress: 0,
      loadingMessage: 'Initializing...',
      recentSearches: []
    }
  },
  mounted() {
    this.loadRecentSearches()
  },
  methods: {
    getApiBaseUrl() {
      // Vue CLI exposes env vars prefixed with VUE_APP_
      const base = process.env.VUE_APP_API_BASE_URL || '/api'
      // Ensure no trailing slash to make joining paths predictable
      return base.replace(/\/$/, '')
    },
    
    loadRecentSearches() {
      try {
        const recent = localStorage.getItem(RECENT_KEY)
        this.recentSearches = recent ? JSON.parse(recent) : []
      } catch (e) {
        console.error('Failed to load recent searches', e)
        this.recentSearches = []
      }
    },
    
    saveRecentSearch(query) {
      try {
        let recent = this.recentSearches.filter(s => s !== query)
        recent.unshift(query)
        recent = recent.slice(0, MAX_RECENT)
        localStorage.setItem(RECENT_KEY, JSON.stringify(recent))
        this.recentSearches = recent
      } catch (e) {
        console.error('Failed to save recent search', e)
      }
    },
    
    selectRecentSearch(search) {
      this.prompt = search
      this.onAnalyzeClick()
    },
    
    getCachedResult(query) {
      try {
        const cache = localStorage.getItem(CACHE_KEY)
        if (!cache) return null
        
        const cacheData = JSON.parse(cache)
        const cached = cacheData[query]
        
        if (cached && cached.timestamp) {
          // Cache valid for 24 hours
          const age = Date.now() - cached.timestamp
          if (age < 24 * 60 * 60 * 1000) {
            console.log('✅ Using cached result for:', query)
            return cached.data
          }
        }
        return null
      } catch (e) {
        console.error('Cache read error', e)
        return null
      }
    },
    
    setCachedResult(query, data) {
      try {
        const cache = localStorage.getItem(CACHE_KEY)
        const cacheData = cache ? JSON.parse(cache) : {}
        
        cacheData[query] = {
          data,
          timestamp: Date.now()
        }
        
        // Keep only last 10 searches to avoid localStorage limits
        const keys = Object.keys(cacheData)
        if (keys.length > 10) {
          const sorted = keys.sort((a, b) => 
            cacheData[a].timestamp - cacheData[b].timestamp
          )
          delete cacheData[sorted[0]]
        }
        
        localStorage.setItem(CACHE_KEY, JSON.stringify(cacheData))
        console.log('💾 Cached result for:', query)
      } catch (e) {
        console.error('Cache write error', e)
      }
    },
    
    simulateProgress() {
      const stages = [
        { progress: 15, message: 'Connecting to Reddit...' },
        { progress: 30, message: 'Fetching discussions...' },
        { progress: 50, message: 'Analyzing comments...' },
        { progress: 70, message: 'Processing sentiment...' },
        { progress: 85, message: 'Generating report...' },
        { progress: 95, message: 'Finalizing results...' }
      ]
      
      let stageIndex = 0
      this.loadingProgress = 0
      this.loadingMessage = 'Initializing...'
      
      const interval = setInterval(() => {
        if (stageIndex < stages.length && this.isLoading) {
          const stage = stages[stageIndex]
          this.loadingProgress = stage.progress
          this.loadingMessage = stage.message
          stageIndex++
        } else {
          clearInterval(interval)
        }
      }, 800)
      
      return interval
    },
    
    async onAnalyzeClick() {
      const query = this.prompt && this.prompt.trim().length > 0 ? this.prompt.trim() : 'Kiwi.com'

      // Check cache first
      const cachedData = this.getCachedResult(query)
      if (cachedData) {
        this.saveRecentSearch(query)
        this.$router.push({
          name: 'stats',
          query: { prompt: query },
          state: { analyzeResponse: cachedData }
        })
        return
      }

      this.isLoading = true
      const progressInterval = this.simulateProgress()
      
      try {
        const baseUrl = this.getApiBaseUrl()
        const response = await fetch(`${baseUrl}/analyze`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            k: 20,
            query
          }),
        })

        if (!response.ok) {
          console.error('Analyze request failed', await response.text())
        }

        const data = await response.json().catch(() => null)

        if (data) {
          this.setCachedResult(query, data)
          this.saveRecentSearch(query)
        }
        
        // Complete progress
        this.loadingProgress = 100
        this.loadingMessage = 'Complete!'
        
        setTimeout(() => {
          this.$router.push({
            name: 'stats',
            query: { prompt: query },
            state: data ? { analyzeResponse: data } : undefined
          })
        }, 300)
      } catch (err) {
        console.error('Analyze request error', err)
        clearInterval(progressInterval)
        this.$router.push({
          name: 'stats',
          query: { prompt: query }
        })
      } finally {
        setTimeout(() => {
          this.isLoading = false
          clearInterval(progressInterval)
        }, 500)
      }
    }
  }
}
</script>

<style scoped>
.home {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 2rem;
  padding-bottom: 5rem; /* Space for footer on mobile */
  background-image: url('../assets/backgroundHQ.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed;
}

.global-loader-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.progress-container {
  width: 90%;
  max-width: 500px;
  text-align: center;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 1rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #FF4500, #ff6a33);
  border-radius: 10px;
  transition: width 0.5s ease;
  box-shadow: 0 0 20px rgba(255, 69, 0, 0.6);
}

.progress-text {
  color: #ffffff;
  font-size: 1.1rem;
  font-weight: 500;
  letter-spacing: 0.5px;
  margin-bottom: 0.5rem;
}

.progress-percentage {
  color: #FF4500;
  font-size: 2rem;
  font-weight: 700;
  letter-spacing: 1px;
}

/* Recent Searches */
.recent-searches {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  backdrop-filter: blur(10px);
}

.recent-title {
  color: #ffffff;
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.recent-title i {
  color: #FF4500;
  font-size: 0.9rem;
}

.recent-items {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.recent-item {
  padding: 0.6rem 1.2rem;
  background: rgba(255, 69, 0, 0.1);
  border: 1px solid rgba(255, 69, 0, 0.3);
  border-radius: 20px;
  color: #ffffff;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.recent-item i {
  color: #FF4500;
  font-size: 0.8rem;
}

.recent-item:hover {
  background: rgba(255, 69, 0, 0.2);
  border-color: #FF4500;
  transform: translateY(-2px);
}

.content-wrapper {
  max-width: 800px;
  margin-left: 8%;
}

.logo-container {
  margin-bottom: 0.5rem;
}

.logo {
  max-width: 150px;
  height: auto;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.3));
}

.main-title {
  font-size: 4rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
  margin-bottom: 0.5rem;
  letter-spacing: -1px;
  line-height: 1.2;
}

.subtitle {
  font-size: 1.3rem;
  color: #FF4500;
  margin: 0;
  margin-bottom: 1rem;
  font-weight: 600;
  letter-spacing: 0.3px;
}

.description {
  font-size: 1rem;
  color: #b0b0b0;
  margin: 0;
  margin-bottom: 3rem;
  font-weight: 400;
  line-height: 1.6;
  max-width: 600px;
}

.search-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-top: 3rem;
}

.input-wrapper {
  position: relative;
}

.search-bar {
  width: 100%;
  padding: 1.2rem 1.5rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 30px;
  font-size: 1rem;
  color: #ffffff;
  outline: none;
  transition: all 0.3s ease;
  font-weight: 400;
}

.search-bar::placeholder {
  color: #707070;
  font-weight: 300;
}

.search-bar:focus {
  border-color: #FF4500;
  background: rgba(255, 255, 255, 0.15);
}

.check-button {
  padding: 1.2rem 3rem;
  background: #FF4500;
  color: white;
  border: none;
  border-radius: 30px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  letter-spacing: 0.5px;
  position: relative;
  overflow: hidden;
  align-self: flex-start;
}

.check-button:hover {
  background: #ff6a33;
  transform: translateY(-2px);
}

.check-button:active {
  transform: translateY(0);
}

.check-button span {
  position: relative;
  z-index: 1;
}

/* Extension Section */
.extension-section {
  margin-top: 2rem;
  padding: 1.5rem;
  background: rgba(255, 69, 0, 0.1);
  border: 1px solid rgba(255, 69, 0, 0.3);
  border-radius: 16px;
  backdrop-filter: blur(10px);
  text-align: center;
}

.extension-text {
  color: #b0b0b0;
  font-size: 0.95rem;
  margin: 0 0 1rem 0;
  line-height: 1.5;
}

.extension-text i {
  color: #FF4500;
  margin-right: 0.5rem;
}

.extension-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.9rem 2rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 30px;
  color: #ffffff;
  text-decoration: none;
  font-size: 0.95rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.extension-button:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: #FF4500;
  transform: translateY(-2px);
}

.extension-button i {
  font-size: 1.1rem;
}

/* Hide extension section on mobile */
@media (max-width: 1024px) {
  .extension-section {
    display: none;
  }
}

/* Responsive */
@media (max-width: 768px) {
  .home {
    padding: 1rem;
    padding-bottom: 6rem; /* More space for footer on mobile */
  }

  .content-wrapper {
    margin-left: 0;
    max-width: 100%;
  }
  
  .logo {
    max-width: 100px;
  }

  .main-title {
    font-size: 2.5rem;
  }
  
  .subtitle {
    font-size: 1rem;
  }

  .description {
    font-size: 0.9rem;
    margin-bottom: 2rem;
  }

  .search-section {
    margin-top: 2rem;
  }

  .search-bar {
    padding: 1rem 1.2rem;
    font-size: 0.9rem;
  }
  
  .check-button {
    width: 100%;
    padding: 1rem 2rem;
  }

  .footer {
    font-size: 0.7rem;
    padding: 1rem;
  }
}

@media (max-width: 480px) {
  .home {
    padding: 0.75rem;
  }

  .main-title {
    font-size: 2rem;
  }

  .subtitle {
    font-size: 0.9rem;
  }

  .description {
    font-size: 0.85rem;
  }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.footer {
  position: relative;
  margin-top: auto;
  padding: 1.5rem 0;
  text-align: center;
  z-index: 2;
}

.footer p {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.85rem;
  font-weight: 300;
  margin: 0;
  letter-spacing: 0.5px;
}

/* iOS Safe Area */
@supports (padding-bottom: env(safe-area-inset-bottom)) {
  .home {
    padding-bottom: calc(5rem + env(safe-area-inset-bottom));
  }
  
  .footer {
    padding-bottom: env(safe-area-inset-bottom);
  }
}
</style>
