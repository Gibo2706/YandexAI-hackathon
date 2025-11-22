<template>
  <div class="home">
    <div v-if="isLoading" class="global-loader-overlay">
      <div class="loader-spinner"></div>
      <div class="loader-text">Analyzing Reddit... Please wait</div>
    </div>

    <div class="content-wrapper">
      <div class="logo-container">
        <img alt="Reddit logo" src="../assets/logoP.png" class="logo">
      </div>
      
      <h1 class="main-title">CheckMate</h1>
      <p class="subtitle">CheckMate to Scammers. Real Reviews. Real Protection.</p>
      <p class="description">Check any website name, seller, service, or product through authentic Reddit discussions, along with technical and content checks. Our AI analyzes thousands of real human experiences to guide your decisions.</p>
      
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
      </div>
    </div>

    <footer class="footer">
      <p>&copy; 2025 The Sthrokaders | AI NATION Hackathon by Yandex & Reputeo</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'HomeView',
  data() {
    return {
      prompt: '',
      isLoading: false
    }
  },
  methods: {
    getApiBaseUrl() {
      // Vue CLI exposes env vars prefixed with VUE_APP_
      const base = process.env.VUE_APP_API_BASE_URL || '/api'
      // Ensure no trailing slash to make joining paths predictable
      return base.replace(/\/$/, '')
    },
    async onAnalyzeClick() {
      const query = this.prompt && this.prompt.trim().length > 0 ? this.prompt.trim() : 'Kiwi.com'

      this.isLoading = true
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
          credentials: 'include', // include cookies for session management if any
        })

        if (!response.ok) {
          console.error('Analyze request failed', await response.text())
          // Fallback: still navigate so StatsView can handle absence of data / show mock
        }

        const data = await response.json().catch(() => null)

        this.$router.push({
          name: 'stats',
          query: { prompt: query },
          state: data ? { analyzeResponse: data } : undefined
        })
      } catch (err) {
        console.error('Analyze request error', err)
        this.$router.push({
          name: 'stats',
          query: { prompt: query }
        })
      } finally {
        this.isLoading = false
      }
    }
  }
}
</script>

<style scoped>
.home {
  min-height: 100vh;
  display: flex;
  align-items: center;
  padding: 2rem;
  background-image: url('../assets/backgroundHQ.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed;
}

.global-loader-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loader-spinner {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  border: 4px solid rgba(255, 255, 255, 0.15);
  border-top-color: #FF4500;
  animation: spin 0.9s linear infinite;
  margin-bottom: 1rem;
}

.loader-text {
  color: #ffffff;
  font-size: 1rem;
  font-weight: 500;
  letter-spacing: 0.5px;
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

/* Responsive */
@media (max-width: 768px) {
  .home {
    padding: 1rem;
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
    bottom: 1rem;
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
  position: absolute;
  bottom: 1.5rem;
  left: 0;
  right: 0;
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
</style>
