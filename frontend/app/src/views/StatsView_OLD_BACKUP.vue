<template>
  <div class="stats" v-if="hasData">
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="query-title">{{ data.query }}</h1>
        <p class="analysis-meta">
          Analyzed <strong>{{ data.num_discussions_analyzed }}</strong> Reddit discussions
        </p>
      </div>
    </div>

    <!-- Main Verdict Card -->
    <div class="verdict-card" :class="verdictClass">
      <div class="verdict-header">
        <div class="verdict-badge">{{ verdictLabel }}</div>
        <div class="verdict-score-display">
          <div class="score-number">{{ scamScore }}</div>
          <div class="score-label">Scam Score</div>
        </div>
      </div>
      <div class="confidence-bar-wrapper">
        <div class="confidence-label">
          <span>Confidence</span>
          <span class="confidence-value">{{ confidence }}%</span>
        </div>
        <div class="confidence-bar">
          <div class="confidence-fill" :style="{ width: confidence + '%' }"></div>
        </div>
      </div>
      <p class="verdict-summary">{{ data.analysis.summary }}</p>
    </div>

    <!-- Stats Grid -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">💬</div>
        <div class="stat-value">{{ data.aggregate_stats.total_discussions }}</div>
        <div class="stat-label">Discussions</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">⭐</div>
        <div class="stat-value">{{ avgCredibility }}%</div>
        <div class="stat-label">Avg Credibility</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-value">{{ avgQuality }}%</div>
        <div class="stat-label">Avg Quality</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">⚖️</div>
        <div class="stat-value">{{ scamRatio }}</div>
        <div class="stat-label">Scam/Positive Ratio</div>
      </div>
    </div>

    <!-- Scam Indicators Section -->
    <div class="two-column-layout">
      <div class="findings-section red-flags-section">
        <h2 class="section-title">
          <span class="title-icon">🚨</span>
          Red Flags
        </h2>
        <ul class="findings-list" v-if="data.analysis.red_flags && data.analysis.red_flags.length">
          <li v-for="(flag, idx) in data.analysis.red_flags" :key="'red-' + idx" class="finding-item red">
            <span class="finding-bullet"></span>
            <span class="finding-text">{{ flag }}</span>
          </li>
        </ul>
        <p v-else class="no-data-message">No red flags detected</p>
      </div>

      <div class="findings-section green-flags-section">
        <h2 class="section-title">
          <span class="title-icon">✅</span>
          Green Flags
        </h2>
        <ul class="findings-list" v-if="data.analysis.green_flags && data.analysis.green_flags.length">
          <li v-for="(flag, idx) in data.analysis.green_flags" :key="'green-' + idx" class="finding-item green">
            <span class="finding-bullet"></span>
            <span class="finding-text">{{ flag }}</span>
          </li>
        </ul>
        <p v-else class="no-data-message">No positive signals found</p>
      </div>
    </div>

    <!-- Community Consensus -->
    <div class="consensus-section" v-if="data.aggregate_stats.consensus">
      <h2 class="section-title">Community Consensus</h2>
      <div class="consensus-card">
        <div class="consensus-badge" :class="consensusClass">
          {{ consensusLabel }}
        </div>
        <div class="consensus-stats">
          <div class="consensus-stat">
            <span class="stat-label">Strong Agreement</span>
            <span class="stat-value">{{ data.aggregate_stats.consensus.strong_agreement }}</span>
          </div>
          <div class="consensus-stat">
            <span class="stat-label">Controversial</span>
            <span class="stat-value">{{ data.aggregate_stats.consensus.controversial }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Scam Mentions Analysis -->
    <div class="scam-mentions-section" v-if="data.aggregate_stats.scam_indicators">
      <h2 class="section-title">Scam Analysis</h2>
      <div class="mentions-grid">
        <div class="mention-card danger">
          <div class="mention-value">{{ data.aggregate_stats.scam_indicators.total_scam_mentions }}</div>
          <div class="mention-label">Scam Mentions</div>
        </div>
        <div class="mention-card warning">
          <div class="mention-value">{{ data.aggregate_stats.scam_indicators.total_warnings }}</div>
          <div class="mention-label">Warnings</div>
        </div>
        <div class="mention-card positive">
          <div class="mention-value">{{ data.aggregate_stats.scam_indicators.total_positive_vouches }}</div>
          <div class="mention-label">Positive Vouches</div>
        </div>
      </div>
    </div>

    <!-- Key Points -->
    <div class="key-points-section" v-if="data.analysis.key_points && data.analysis.key_points.length">
      <h2 class="section-title">Key Findings</h2>
      <div class="key-points-list">
        <div v-for="(point, idx) in data.analysis.key_points" :key="idx" class="key-point-card">
          <span class="point-number">{{ idx + 1 }}</span>
          <span class="point-text">{{ point }}</span>
        </div>
      </div>
    </div>

    <!-- Top Discussions -->
    <div class="discussions-section" v-if="topDiscussions.length">
      <h2 class="section-title">Top Discussions</h2>
      <div class="discussions-list">
        <div v-for="(discussion, idx) in topDiscussions" :key="idx" class="discussion-card">
          <div class="discussion-header">
            <span class="discussion-rank">#{{ idx + 1 }}</span>
            <span class="subreddit-badge">r/{{ discussion.subreddit }}</span>
            <span class="discussion-score">{{ discussion.score }} upvotes</span>
          </div>
          <h3 class="discussion-title">{{ discussion.title }}</h3>
          <div class="discussion-stats">
            <span class="stat-item">
              <span class="stat-icon">💬</span>
              {{ discussion.num_comments }} comments
            </span>
            <span class="stat-item">
              <span class="stat-icon">⭐</span>
              {{ discussion.enrichment.discussion_credibility.toFixed(1) }}% credibility
            </span>
            <span class="stat-item">
              <span class="stat-icon">📊</span>
              {{ discussion.enrichment.post_quality.quality_score }}% quality
            </span>
          </div>
          
          <!-- Scam Analysis for this discussion -->
          <div class="discussion-scam-analysis" v-if="discussion.enrichment.scam_analysis">
            <div class="scam-mini-stat" v-if="discussion.enrichment.scam_analysis.scam_mention_count > 0">
              <span class="mini-label">Scam mentions:</span>
              <span class="mini-value danger">{{ discussion.enrichment.scam_analysis.scam_mention_count }}</span>
            </div>
            <div class="scam-mini-stat" v-if="discussion.enrichment.scam_analysis.positive_count > 0">
              <span class="mini-label">Positive vouches:</span>
              <span class="mini-value positive">{{ discussion.enrichment.scam_analysis.positive_count }}</span>
            </div>
          </div>

          <!-- Thread consensus -->
          <div class="thread-consensus" v-if="discussion.enrichment.thread_analysis">
            <span class="consensus-label">Thread Consensus:</span>
            <span class="consensus-value" :class="getConsensusClass(discussion.enrichment.thread_analysis.consensus_level)">
              {{ formatConsensus(discussion.enrichment.thread_analysis.consensus_level) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Reasoning -->
    <div class="reasoning-section">
      <h2 class="section-title">Detailed Analysis</h2>
      <div class="reasoning-card">
        <p class="reasoning-text">{{ data.analysis.reasoning }}</p>
      </div>
    </div>

    <div class="external-api-section" style="display: none;">
      <h2>Technical & Security Analysis</h2>
      <p class="section-description">Results from third-party security and validation APIs</p>
      
      <div class="api-results-grid">
        <!-- Google Safe Browsing -->
        <div class="api-card safe">
          <div class="api-header">
            <div class="api-icon">🛡️</div>
            <div class="api-title">Google Safe Browsing</div>
          </div>
          <div class="api-status-badge safe">{{ externalApi.googleSafeBrowsing.status.toUpperCase() }}</div>
          <p class="api-description">{{ externalApi.googleSafeBrowsing.description }}</p>
          <div class="api-detail">Last checked: {{ externalApi.googleSafeBrowsing.lastChecked }}</div>
        </div>

        <!-- SSL Certificate -->
        <div class="api-card" :class="externalApi.sslCertificate.valid ? 'safe' : 'warning'">
          <div class="api-header">
            <div class="api-icon">🔒</div>
            <div class="api-title">SSL Certificate</div>
          </div>
          <div class="api-status-badge" :class="externalApi.sslCertificate.grade === 'A+' ? 'safe' : 'warning'">
            Grade {{ externalApi.sslCertificate.grade }}
          </div>
          <p class="api-description">{{ externalApi.sslCertificate.encryption }} encryption</p>
          <div class="api-detail">Issuer: {{ externalApi.sslCertificate.issuer }}</div>
          <div class="api-detail">Expires: {{ externalApi.sslCertificate.expiryDate }} ({{ externalApi.sslCertificate.daysUntilExpiry }} days)</div>
        </div>

        <!-- VirusTotal -->
        <div class="api-card" :class="externalApi.virusTotal.malicious === 0 ? 'safe' : 'danger'">
          <div class="api-header">
            <div class="api-icon">🔍</div>
            <div class="api-title">VirusTotal Scan</div>
          </div>
          <div class="api-status-badge" :class="externalApi.virusTotal.malicious === 0 ? 'safe' : 'danger'">
            {{ externalApi.virusTotal.clean }}/{{ externalApi.virusTotal.totalEngines }} Clean
          </div>
          <p class="api-description">Multi-engine malware scan results</p>
          <div class="api-detail">Malicious: {{ externalApi.virusTotal.malicious }}</div>
          <div class="api-detail">Suspicious: {{ externalApi.virusTotal.suspicious }}</div>
          <div class="api-detail">Community Score: +{{ externalApi.virusTotal.communityScore }}</div>
        </div>

        <!-- WHOIS Data -->
        <div class="api-card safe">
          <div class="api-header">
            <div class="api-icon">📋</div>
            <div class="api-title">Domain Information</div>
          </div>
          <div class="api-status-badge safe">{{ externalApi.whoisData.domainAge }}</div>
          <p class="api-description">Registered with {{ externalApi.whoisData.registrar }}</p>
          <div class="api-detail">Registration: {{ externalApi.whoisData.registrationDate }}</div>
          <div class="api-detail">Country: {{ externalApi.whoisData.registrantCountry }}</div>
          <div class="api-detail">Expires: {{ externalApi.whoisData.expiryDate }}</div>
        </div>

        <!-- ScamAdvisor -->
        <div class="api-card" :class="externalApi.scamAdvisor.trustScore > 70 ? 'safe' : 'warning'">
          <div class="api-header">
            <div class="api-icon">⭐</div>
            <div class="api-title">ScamAdvisor</div>
          </div>
          <div class="api-status-badge" :class="externalApi.scamAdvisor.trustScore > 70 ? 'safe' : 'warning'">
            {{ externalApi.scamAdvisor.trustScore }}/100
          </div>
          <p class="api-description">Trust score: {{ externalApi.scamAdvisor.risk }}</p>
          <div class="api-highlights">
            <div v-for="(highlight, idx) in externalApi.scamAdvisor.highlights" :key="idx" class="highlight-item">
              • {{ highlight }}
            </div>
          </div>
        </div>

        <!-- Website Analytics -->
        <div class="api-card safe">
          <div class="api-header">
            <div class="api-icon">📊</div>
            <div class="api-title">Traffic Analytics</div>
          </div>
          <div class="api-status-badge safe">{{ externalApi.websiteAnalytics.monthlyVisitors }} visits/mo</div>
          <p class="api-description">Global ranking and traffic data</p>
          <div class="api-detail">Alexa Rank: #{{ externalApi.websiteAnalytics.alexaRank.toLocaleString() }}</div>
          <div class="api-detail">Avg. Session: {{ externalApi.websiteAnalytics.avgSessionDuration }}</div>
          <div class="api-detail">Bounce Rate: {{ externalApi.websiteAnalytics.bounceRate }}</div>
        </div>
      </div>

      <!-- Technical Checks Summary -->
      <div v-if="technicalChecks && technicalChecks.length" class="technical-checks-section">
        <h3>Security Checklist</h3>
        <div class="checks-grid">
          <div v-for="(check, idx) in technicalChecks" :key="idx" class="check-item" :class="check.status">
            <div class="check-header">
              <span class="check-icon" :class="check.status">
                {{ check.status === 'pass' ? '✓' : '⚠' }}
              </span>
              <span class="check-name">{{ check.name }}</span>
              <span class="check-score">{{ check.score }}%</span>
            </div>
            <p class="check-details">{{ check.details }}</p>
          </div>
        </div>
      </div>
    </div>

    <div class="layout-container">
      <div class="main-column">
        <!-- Sentiment Visualization -->
        <div class="sentiment-visual-section">
          <h2>Sentiment Distribution</h2>
          <div class="sentiment-bars">
            <div class="sentiment-bar-item">
              <div class="sentiment-bar-header">
                <span class="sentiment-label">Positive Reviews</span>
                <span class="sentiment-value">{{ (sentimentData.legit * 100).toFixed(0) }}%</span>
              </div>
              <div class="sentiment-bar-bg">
                <div class="sentiment-bar-fill positive" :style="{ width: (sentimentData.legit * 100) + '%' }"></div>
              </div>
            </div>
            <div class="sentiment-bar-item">
              <div class="sentiment-bar-header">
                <span class="sentiment-label">Negative Reviews</span>
                <span class="sentiment-value">{{ (sentimentData.scam * 100).toFixed(0) }}%</span>
              </div>
              <div class="sentiment-bar-bg">
                <div class="sentiment-bar-fill negative" :style="{ width: (sentimentData.scam * 100) + '%' }"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Key Indicators Section -->
        <div class="indicators-section">
          <div class="indicators-grid">
            <div class="indicator-card positive">
              <div class="indicator-header">
                <span class="indicator-icon-large">✓</span>
                <h3>Positive Signals</h3>
              </div>
              <ul>
                <li v-for="(item, index) in keyIndicators.positive" :key="index">
                  <span class="indicator-bullet"></span>
                  {{ item.text }}
                </li>
              </ul>
            </div>
            <div class="indicator-card warning">
              <div class="indicator-header">
                <span class="indicator-icon-large">⚠</span>
                <h3>Warning Signals</h3>
              </div>
              <ul>
                <li v-for="(item, index) in keyIndicators.warnings" :key="index">
                  <span class="indicator-bullet"></span>
                  {{ item.text }}
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Risk Factors Section -->
        <div class="risk-section">
          <h2>Risk Analysis</h2>
          <div class="risk-factors">
            <div v-for="(risk, index) in riskFactors" :key="index" class="risk-item">
              <div class="risk-header">
                <span class="risk-level" :class="risk.level">{{ risk.level.toUpperCase() }}</span>
                <span class="risk-text">{{ risk.text }}</span>
                <span class="risk-percentage">{{ risk.percentage }}%</span>
              </div>
              <div class="risk-bar">
                <div class="risk-fill" :style="{ width: risk.percentage + '%', backgroundColor: risk.color }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <!-- End main-column -->

      <!-- Sidebar Column -->
      <aside class="sidebar-column">
        <!-- Pie Chart Section -->
        <div class="chart-section">
          <h2>Community Sentiment</h2>
          <div class="pie-chart-container">
            <svg viewBox="0 0 200 200" class="pie-chart">
              <circle cx="100" cy="100" r="80" fill="#2a2a2a" />
              <path 
                :d="getLegitPath()" 
                fill="#606060"
                class="pie-segment"
              />
              <path 
                :d="getScamPath()" 
                fill="#FF4500"
                class="pie-segment"
              />
              <circle cx="100" cy="100" r="50" fill="#0a0a0a" />
            </svg>
            <div class="chart-stats">
              <div class="chart-stat-item positive-stat">
                <div class="stat-value">{{ (sentimentData.legit * 100).toFixed(0) }}%</div>
                <div class="stat-label">Positive</div>
              </div>
              <div class="chart-stat-item negative-stat">
                <div class="stat-value">{{ (sentimentData.scam * 100).toFixed(0) }}%</div>
                <div class="stat-label">Negative</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Recommendations -->
        <div class="recommendations-compact">
          <h3>Key Recommendations</h3>
          <div class="rec-list">
            <div v-for="(rec, index) in recommendations" :key="index" 
                 class="recommendation-item" 
                 :class="rec.type">
              <span class="rec-number">{{ index + 1 }}</span>
              <span class="rec-text">{{ rec.text }}</span>
            </div>
          </div>
        </div>

        <!-- Risk Score Card -->
        <div class="risk-score-card">
          <div class="risk-score-header">Overall Risk Score</div>
          <div class="risk-score-value">{{ (sentimentData.scam * 100).toFixed(0) }}</div>
          <div class="risk-score-label">out of 100</div>
          <div class="risk-score-bar">
            <div class="risk-score-fill" :style="{ width: (sentimentData.scam * 100) + '%' }"></div>
          </div>
        </div>
      </aside>
    </div>

    <!-- Top Posts Section - Full Width -->
    <TopPosts :posts="topPosts" :prompt="prompt" />

    <footer class="footer">
      <p>&copy; 2025 The Sthrokaders | AI NATION Hackathon by Yandex & Reputeo</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'StatsView',
  data() {
    return {
      data: null,
      hasData: false
    }
  },
  created() {
    // GUARD: Only allow access via router navigation with data
    const navState = window.history.state && window.history.state.analyzeResponse
    
    if (!navState) {
      // No data from navigation - redirect to home
      console.warn('[StatsView] No analysis data found, redirecting to home')
      this.$router.replace('/')
      return
    }

    console.log('[StatsView] Loading analysis data:', navState)
    this.data = navState
    this.hasData = true
  },
  computed: {
    scamScore() {
      return this.data?.analysis?.scam_score || 0
    },
    confidence() {
      return this.data?.analysis?.confidence || 0
    },
    verdictLabel() {
      const recommendation = this.data?.analysis?.recommendation || 'UNKNOWN'
      const labels = {
        'AVOID': 'AVOID',
        'HIGH_CAUTION': 'HIGH CAUTION',
        'INVESTIGATE': 'INVESTIGATE FURTHER',
        'LOW_RISK': 'LOW RISK',
        'LIKELY_SAFE': 'LIKELY SAFE'
      }
      return labels[recommendation] || recommendation
    },
    verdictClass() {
      const recommendation = this.data?.analysis?.recommendation || ''
      const classMap = {
        'AVOID': 'verdict-avoid',
        'HIGH_CAUTION': 'verdict-high-caution',
        'INVESTIGATE': 'verdict-investigate',
        'LOW_RISK': 'verdict-low-risk',
        'LIKELY_SAFE': 'verdict-safe'
      }
      return classMap[recommendation] || 'verdict-unknown'
    },
    avgCredibility() {
      return Math.round(this.data?.aggregate_stats?.avg_discussion_credibility || 0)
    },
    avgQuality() {
      return Math.round(this.data?.aggregate_stats?.avg_post_quality || 0)
    },
    scamRatio() {
      const ratio = this.data?.aggregate_stats?.scam_indicators?.scam_to_positive_ratio || 0
      return ratio.toFixed(2)
    },
    consensusLabel() {
      const overall = this.data?.aggregate_stats?.consensus?.overall || ''
      const labels = {
        'strong_community_agreement': 'Strong Community Agreement',
        'highly_controversial': 'Highly Controversial',
        'mixed_opinions': 'Mixed Opinions'
      }
      return labels[overall] || overall.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    },
    consensusClass() {
      const overall = this.data?.aggregate_stats?.consensus?.overall || ''
      if (overall.includes('agreement')) return 'consensus-agreement'
      if (overall.includes('controversial')) return 'consensus-controversial'
      return 'consensus-mixed'
    },
    topDiscussions() {
      if (!this.data?.enriched_results) return []
      // Sort by credibility and quality, take top 5
      return [...this.data.enriched_results]
        .filter(d => d.enrichment && d.metadata)
        .map(d => ({
          title: d.metadata.title || 'Untitled',
          subreddit: d.metadata.subreddit || 'unknown',
          score: d.metadata.score || 0,
          num_comments: d.metadata.num_comments || 0,
          enrichment: d.enrichment
        }))
        .sort((a, b) => {
          const scoreA = (a.enrichment.discussion_credibility || 0) + (a.enrichment.post_quality?.quality_score || 0)
          const scoreB = (b.enrichment.discussion_credibility || 0) + (b.enrichment.post_quality?.quality_score || 0)
          return scoreB - scoreA
        })
        .slice(0, 5)
    }
  },
  methods: {
    getConsensusClass(consensus) {
      if (!consensus) return ''
      if (consensus === 'strong_agreement') return 'consensus-strong'
      if (consensus === 'controversial' || consensus === 'active_debate') return 'consensus-controversial'
      return 'consensus-mixed'
    },
    formatConsensus(consensus) {
      if (!consensus) return 'N/A'
      return consensus.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    },
    mapBackendToUi_OBSOLETE(response) {
      // Response follows AnalyzeResponse from API_STRUCTURES_FINAL.md
      try {
        console.log('[StatsView] Mapping backend response to UI...', response)
        const enriched = Array.isArray(response.enriched_results) ? response.enriched_results : []
        const stats = response.aggregate_stats || {}
        const analysis = response.analysis || {}

        // Map to simple sentiment percentages from scam_score or scam mentions
        const scamScore = typeof analysis.scam_score === 'number' ? analysis.scam_score : 0
        const scam = Math.min(Math.max(scamScore / 100, 0), 1)
        const legit = 1 - scam
        this.sentimentData = { scam, legit }
  console.log('[StatsView] sentimentData set to:', this.sentimentData)

        // Map metrics
        const totalPosts = enriched.length
        const totalComments = enriched.reduce((sum, item) => {
          const ta = item.enrichment && item.enrichment.thread_analysis
          return sum + (ta && typeof ta.total_comments === 'number' ? ta.total_comments : 0)
        }, 0)

        this.metrics = {
          totalPosts,
          totalComments,
          dateRange: 'Reddit history',
          confidence: typeof analysis.confidence === 'number' ? analysis.confidence : 0
        }
        console.log('[StatsView] metrics derived from backend:', this.metrics)

        // Key indicators from flags
        const redFlags = Array.isArray(analysis.red_flags) ? analysis.red_flags : []
        const greenFlags = Array.isArray(analysis.green_flags) ? analysis.green_flags : []
        this.keyIndicators = {
          positive: greenFlags.map(text => ({ text, icon: '✓' })),
          warnings: redFlags.map(text => ({ text, icon: '⚠' }))
        }
        console.log('[StatsView] keyIndicators:', this.keyIndicators)

        // Risk factors from scam score and scam indicators
        const scamIndicators = (stats && stats.scam_indicators) || {}
        const totalScam = scamIndicators.total_scam_mentions || 0
        const totalWarnings = scamIndicators.total_warnings || 0

        this.riskFactors = [
          {
            level: scamScore >= 75 ? 'high' : scamScore >= 35 ? 'medium' : 'medium',
            text: 'Scam risk based on community reports',
            percentage: Math.round(scamScore || 0),
            color: '#e74c3c'
          },
          {
            level: 'medium',
            text: `Warning phrases detected in discussions (${totalWarnings})`,
            percentage: Math.min(totalWarnings * 10, 100),
            color: '#f39c12'
          },
          {
            level: 'medium',
            text: `Total scam mentions across threads (${totalScam})`,
            percentage: Math.min(totalScam * 8, 100),
            color: '#f39c12'
          }
        ]
        console.log('[StatsView] riskFactors:', this.riskFactors)

        // Recommendations from analysis.recommendation + key_points
        const recs = []
        if (analysis.recommendation) {
          recs.push({
            type: ['AVOID', 'HIGH_CAUTION'].includes(analysis.recommendation) ? 'priority' : 'caution',
            text: `Overall recommendation: ${analysis.recommendation}`,
            icon: ['AVOID', 'HIGH_CAUTION'].includes(analysis.recommendation) ? '⚠' : '✓'
          })
        }
        const keyPoints = Array.isArray(analysis.key_points) ? analysis.key_points : []
        keyPoints.slice(0, 4).forEach(text => {
          recs.push({ type: 'caution', text, icon: '⚠' })
        })
        this.recommendations = recs.length ? recs : getRecommendations()
        console.log('[StatsView] recommendations:', this.recommendations)

        // redditData mapping for Top Reddit Discussions
        if (enriched.length) {
          this.redditData = enriched.map(item => {
            const meta = item.metadata || {}
            const enrichment = item.enrichment || {}
            const post = {
              id: meta.submission_id || meta.id || '',
              title: meta.title || '',
              text: item.text || '',
              subreddit: meta.subreddit || 'unknown',
              score: typeof meta.score === 'number' ? meta.score : 0,
              num_comments: typeof meta.num_comments === 'number' ? meta.num_comments : (enrichment.thread_analysis && enrichment.thread_analysis.total_comments) || 0
            }

            const scamAnalysis = enrichment.scam_analysis || {}
            const comments = []
            const positiveVouches = Array.isArray(scamAnalysis.positive_vouches) ? scamAnalysis.positive_vouches : []
            const fraudIndicators = Array.isArray(scamAnalysis.fraud_indicators) ? scamAnalysis.fraud_indicators : []

            positiveVouches.forEach(text => {
              comments.push({ id: `pos-${text}`, text, score: 1, subreddit: post.subreddit })
            })
            fraudIndicators.forEach(text => {
              comments.push({ id: `neg-${text}`, text, score: -1, subreddit: post.subreddit })
            })

            return { post, comments }
          })
          console.log('[StatsView] redditData mapped from enriched_results (sample):', this.redditData[0])
        }

        // externalApi & technicalChecks are still mock (no external APIs yet)
        this.externalApi = getExternalApiResults()
        this.technicalChecks = getTechnicalChecks()

        this.loadError = null
        console.log('[StatsView] Mapping complete. UI state ready.')
      } catch (e) {
        console.error('Error mapping backend response to UI', e)
        this.loadError = 'There was a problem displaying the analysis. Showing demo data instead.'
      }
    },
    polarToCartesian(centerX, centerY, radius, angleInDegrees) {
      const angleInRadians = (angleInDegrees - 90) * Math.PI / 180.0;
      return {
        x: centerX + (radius * Math.cos(angleInRadians)),
        y: centerY + (radius * Math.sin(angleInRadians))
      };
    },
    getLegitPath() {
      const percentage = this.sentimentData.legit;
      const angle = percentage * 360;
      const start = this.polarToCartesian(100, 100, 80, 0);
      const end = this.polarToCartesian(100, 100, 80, angle);
      const largeArcFlag = angle > 180 ? 1 : 0;
      
      return [
        `M 100 100`,
        `L ${start.x} ${start.y}`,
        `A 80 80 0 ${largeArcFlag} 1 ${end.x} ${end.y}`,
        `Z`
      ].join(' ');
    },
    getScamPath() {
      const legitPercentage = this.sentimentData.legit;
      const scamPercentage = this.sentimentData.scam;
      const startAngle = legitPercentage * 360;
      const endAngle = startAngle + (scamPercentage * 360);
      
      const start = this.polarToCartesian(100, 100, 80, startAngle);
      const end = this.polarToCartesian(100, 100, 80, endAngle);
      const largeArcFlag = scamPercentage * 360 > 180 ? 1 : 0;
      
      return [
        `M 100 100`,
        `L ${start.x} ${start.y}`,
        `A 80 80 0 ${largeArcFlag} 1 ${end.x} ${end.y}`,
        `Z`
      ].join(' ');
    }
  }
}
</script>

<style scoped>
.stats {
  padding: 2rem;
  max-width: 1600px;
  margin: 0 auto;
  min-height: 100vh;
}

/* Header Section */
.header-section {
  text-align: center;
  margin-bottom: 3rem;
  padding-bottom: 2rem;
  border-bottom: 2px solid #FF4500;
}

.stats h1 {
  color: #FFFFFF;
  margin-bottom: 0.75rem;
  font-size: 2.5rem;
  font-weight: 700;
  letter-spacing: -1px;
}

.search-query {
  color: #FF4500;
  font-weight: 800;
  text-decoration: underline;
  text-decoration-color: #FF4500;
  text-decoration-thickness: 3px;
  text-underline-offset: 5px;
}

.intro-text {
  color: #808080;
  font-size: 1rem;
  font-weight: 400;
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
  margin-bottom: 3rem;
}

@media (max-width: 1200px) {
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }
}

.metric-card {
  background: #1a1a1a;
  border: 2px solid #2a2a2a;
  padding: 2rem 1.5rem;
  text-align: center;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.metric-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: #FF4500;
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.metric-card:hover {
  border-color: #FF4500;
  transform: translateY(-5px);
}

.metric-card:hover::before {
  transform: scaleX(1);
}

.metric-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  filter: grayscale(0.3);
}

.metric-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: #FF4500;
  margin-bottom: 0.5rem;
  letter-spacing: -1px;
}

.metric-label {
  font-size: 0.9rem;
  color: #808080;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* Layout Container */
.layout-container {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 2rem;
  margin-bottom: 3rem;
}

/* External API Section */
.external-api-section {
  margin-bottom: 3rem;
  padding: 2rem;
  background: #0a0a0a;
  border: 2px solid #2a2a2a;
}

.external-api-section h2 {
  color: #FFFFFF;
  text-align: center;
  margin-bottom: 0.5rem;
  font-size: 2rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.api-results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.api-card {
  background: #1a1a1a;
  border: 2px solid #2a2a2a;
  padding: 1.5rem;
  transition: all 0.3s ease;
  position: relative;
}

.api-card.safe {
  border-top: 3px solid #606060;
}

.api-card.warning {
  border-top: 3px solid #ff8844;
}

.api-card.danger {
  border-top: 3px solid #FF4500;
}

.api-card:hover {
  border-color: #FF4500;
  transform: translateY(-3px);
}

.api-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.api-icon {
  font-size: 2rem;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0a0a0a;
  border: 2px solid #2a2a2a;
}

.api-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #e0e0e0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.api-status-badge {
  display: inline-block;
  padding: 0.5rem 1rem;
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 1px;
  margin-bottom: 1rem;
  color: white;
}

.api-status-badge.safe {
  background: #606060;
}

.api-status-badge.warning {
  background: #ff8844;
  color: #0a0a0a;
}

.api-status-badge.danger {
  background: #FF4500;
}

.api-description {
  color: #b0b0b0;
  font-size: 0.95rem;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.api-detail {
  color: #808080;
  font-size: 0.85rem;
  padding: 0.4rem 0;
  border-bottom: 1px solid #2a2a2a;
}

.api-detail:last-child {
  border-bottom: none;
}

.api-highlights {
  margin-top: 1rem;
}

.highlight-item {
  color: #a0a0a0;
  font-size: 0.85rem;
  padding: 0.3rem 0;
  line-height: 1.5;
}

/* Technical Checks Section */
.technical-checks-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 2px solid #2a2a2a;
}

.technical-checks-section h3 {
  color: #e0e0e0;
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  text-align: center;
}

.checks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.check-item {
  background: #1a1a1a;
  border: 2px solid #2a2a2a;
  padding: 1.25rem;
  transition: all 0.3s ease;
}

.check-item:hover {
  border-color: #3a3a3a;
  background: #252525;
}

.check-item.pass {
  border-left: 3px solid #606060;
}

.check-item.warning {
  border-left: 3px solid #ff8844;
}

.check-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.check-icon {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  font-weight: 700;
  background: #0a0a0a;
  border: 2px solid #2a2a2a;
}

.check-icon.pass {
  color: #606060;
  border-color: #606060;
}

.check-icon.warning {
  color: #ff8844;
  border-color: #ff8844;
}

.check-name {
  flex: 1;
  color: #e0e0e0;
  font-weight: 600;
  font-size: 0.95rem;
}

.check-score {
  color: #FF4500;
  font-weight: 700;
  font-size: 1rem;
}

.check-details {
  color: #a0a0a0;
  font-size: 0.85rem;
  margin: 0;
  line-height: 1.5;
}

/* Layout Container */
.layout-container {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 2rem;
  margin-bottom: 3rem;
}

@media (max-width: 1200px) {
  .layout-container {
    grid-template-columns: 1fr;
  }
}

/* Sentiment Visual Section */
.sentiment-visual-section {
  background: #1a1a1a;
  border: 2px solid #2a2a2a;
  padding: 2rem;
  margin-bottom: 2rem;
}

.sentiment-visual-section h2 {
  color: #e0e0e0;
  margin-bottom: 2rem;
  font-size: 1.5rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.sentiment-bars {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.sentiment-bar-item {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.sentiment-bar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sentiment-label {
  color: #c0c0c0;
  font-weight: 600;
  font-size: 1rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.sentiment-value {
  color: #FF4500;
  font-weight: 700;
  font-size: 1.5rem;
}

.sentiment-bar-bg {
  height: 40px;
  background: #0a0a0a;
  border: 2px solid #2a2a2a;
  position: relative;
  overflow: hidden;
}

.sentiment-bar-fill {
  height: 100%;
  transition: width 1s ease;
  position: relative;
}

.sentiment-bar-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.sentiment-bar-fill.positive {
  background: linear-gradient(90deg, #4a4a4a 0%, #606060 100%);
  border-right: 3px solid #808080;
}

.sentiment-bar-fill.negative {
  background: linear-gradient(90deg, #FF4500 0%, #ff6a33 100%);
  border-right: 3px solid #ff8844;
}

/* Indicators Section */
.indicators-section {
  margin-bottom: 2rem;
}

.indicators-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

@media (max-width: 768px) {
  .indicators-grid {
    grid-template-columns: 1fr;
  }
}

.indicator-card {
  background: #1a1a1a;
  border: 2px solid #2a2a2a;
  padding: 2rem;
  transition: all 0.3s ease;
}

.indicator-card:hover {
  border-color: #FF4500;
}

.indicator-card.positive {
  border-top: 3px solid #606060;
}

.indicator-card.warning {
  border-top: 3px solid #FF4500;
}

.indicator-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #2a2a2a;
}

.indicator-icon-large {
  font-size: 2rem;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-center: center;
  background: #0a0a0a;
  border: 2px solid #2a2a2a;
}

.indicator-card.positive .indicator-icon-large {
  color: #606060;
  border-color: #606060;
}

.indicator-card.warning .indicator-icon-large {
  color: #FF4500;
  border-color: #FF4500;
}

.indicator-card h3 {
  margin: 0;
  font-size: 1.2rem;
  color: #e0e0e0;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.indicator-card ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.indicator-card li {
  padding: 1rem 0;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  color: #c0c0c0;
  font-weight: 400;
  border-bottom: 1px solid #2a2a2a;
  font-size: 0.95rem;
  line-height: 1.6;
}

.indicator-card li:last-child {
  border-bottom: none;
}

.indicator-bullet {
  width: 8px;
  height: 8px;
  background: #FF4500;
  flex-shrink: 0;
  margin-top: 0.5rem;
}

/* Risk Section */
.risk-section {
  background: #1a1a1a;
  border: 2px solid #2a2a2a;
  padding: 2rem;
}

.risk-section h2 {
  color: #e0e0e0;
  margin-bottom: 2rem;
  font-size: 1.5rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  border-bottom: 2px solid #FF4500;
  padding-bottom: 1rem;
}

.risk-factors {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.risk-item {
  padding: 1.5rem;
  background: #0a0a0a;
  border: 2px solid #2a2a2a;
  transition: all 0.3s ease;
}

.risk-item:hover {
  border-color: #FF4500;
  background: #1a1a1a;
}

.risk-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.risk-level {
  padding: 0.5rem 1rem;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 1px;
  background: #FF4500;
  color: white;
  flex-shrink: 0;
}

.risk-level.high {
  background: #FF4500;
}

.risk-level.medium {
  background: #ff8844;
  color: #0a0a0a;
}

.risk-text {
  font-weight: 500;
  color: #c0c0c0;
  flex: 1;
}

.risk-percentage {
  font-weight: 700;
  color: #FF4500;
  font-size: 1.2rem;
  margin-left: auto;
}

.risk-bar {
  height: 8px;
  background: #0a0a0a;
  border: 1px solid #2a2a2a;
  overflow: hidden;
  position: relative;
}

.risk-fill {
  height: 100%;
  transition: width 0.8s cubic-bezier(0.34, 1.61, 0.7, 1);
}

/* Sidebar */
.sidebar-column {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Chart Section */
.chart-section {
  background: #1a1a1a;
  border: 2px solid #2a2a2a;
  padding: 2rem;
}

.chart-section h2 {
  color: #e0e0e0;
  margin-bottom: 2rem;
  font-size: 1.3rem;
  font-weight: 600;
  text-align: center;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.pie-chart-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
}

.pie-chart {
  width: 200px;
  height: 200px;
}

.pie-segment {
  transition: opacity 0.3s ease;
}

.chart-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  width: 100%;
}

.chart-stat-item {
  background: #0a0a0a;
  border: 2px solid #2a2a2a;
  padding: 1.5rem;
  text-align: center;
}

.chart-stat-item.positive-stat {
  border-top: 3px solid #606060;
}

.chart-stat-item.negative-stat {
  border-top: 3px solid #FF4500;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #FF4500;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.85rem;
  color: #808080;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 600;
}

/* Recommendations */
.recommendations-compact {
  background: #1a1a1a;
  border: 2px solid #2a2a2a;
  padding: 2rem;
}

.recommendations-compact h3 {
  font-size: 1.1rem;
  color: #e0e0e0;
  margin-bottom: 1.5rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.rec-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.recommendation-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  background: #0a0a0a;
  border: 2px solid #2a2a2a;
  border-left: 3px solid #606060;
  font-size: 0.9rem;
  line-height: 1.5;
  transition: all 0.3s ease;
}

.recommendation-item:hover {
  border-left-color: #FF4500;
  background: #1a1a1a;
}

.recommendation-item.priority {
  border-left-color: #FF4500;
}

.recommendation-item.caution {
  border-left-color: #ff8844;
}

.rec-number {
  width: 24px;
  height: 24px;
  background: #FF4500;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.85rem;
  flex-shrink: 0;
}

.rec-text {
  color: #b0b0b0;
  flex: 1;
}

/* Risk Score Card */
.risk-score-card {
  background: #1a1a1a;
  border: 2px solid #FF4500;
  padding: 2rem;
  text-align: center;
}

.risk-score-header {
  color: #808080;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 1rem;
  font-weight: 600;
}

.risk-score-value {
  font-size: 4rem;
  font-weight: 700;
  color: #FF4500;
  line-height: 1;
  margin-bottom: 0.5rem;
  letter-spacing: -2px;
}

.risk-score-label {
  color: #606060;
  font-size: 0.85rem;
  margin-bottom: 1.5rem;
}

.risk-score-bar {
  height: 12px;
  background: #0a0a0a;
  border: 2px solid #2a2a2a;
  overflow: hidden;
}

.risk-score-fill {
  height: 100%;
  background: linear-gradient(90deg, #FF4500 0%, #ff6a33 100%);
  transition: width 1s ease;
}

/* Top Posts Section */
.top-posts-section {
  margin-bottom: 3rem;
}

.top-posts-section h2 {
  color: #FFFFFF;
  text-align: center;
  margin-bottom: 0.5rem;
  font-size: 2rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.section-description {
  text-align: center;
  color: #808080;
  margin-bottom: 2.5rem;
  font-size: 0.95rem;
}

.reddit-posts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 2rem;
}

@media (max-width: 600px) {
  .reddit-posts {
    grid-template-columns: 1fr;
  }
}

.post-card {
  background: #1a1a1a;
  border: 2px solid #2a2a2a;
  padding: 2rem;
  position: relative;
  transition: all 0.3s ease;
}

.post-card:hover {
  border-color: #FF4500;
}

.post-rank {
  position: absolute;
  top: 1.5rem;
  right: 1.5rem;
  width: 50px;
  height: 50px;
  background: #FF4500;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 700;
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #2a2a2a;
}

.subreddit {
  background: #FF4500;
  color: white;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.post-stats {
  display: flex;
  gap: 1.5rem;
}

.post-stat {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #808080;
  font-weight: 600;
  font-size: 0.9rem;
}

.stat-icon {
  color: #FF4500;
}

.post-card h3 {
  color: #e0e0e0;
  margin-bottom: 1rem;
  font-size: 1.3rem;
  line-height: 1.4;
  font-weight: 600;
  padding-right: 60px;
}

.post-text {
  color: #a0a0a0;
  line-height: 1.6;
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
}

/* Comments Section */
.comments-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 2px solid #2a2a2a;
}

.comments-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.comments-section h4 {
  color: #e0e0e0;
  font-size: 1.1rem;
  margin: 0;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.comments-count {
  color: #606060;
  font-size: 0.85rem;
  font-weight: 600;
}

.comment {
  background: #0a0a0a;
  padding: 1.25rem;
  margin-bottom: 1rem;
  border: 2px solid #2a2a2a;
  border-left: 3px solid #2a2a2a;
  transition: all 0.3s ease;
  position: relative;
  padding-left: 4rem;
}

.comment:hover {
  background: #1a1a1a;
  border-color: #3a3a3a;
}

.comment.positive {
  border-left-color: #606060;
}

.comment.negative {
  border-left-color: #FF4500;
}

.comment-score-badge {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  width: 40px;
  height: 40px;
  background: #1a1a1a;
  border: 2px solid #2a2a2a;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.9rem;
}

.comment-score-badge.score-positive {
  color: #808080;
  border-color: #606060;
}

.comment-score-badge.score-negative {
  color: #FF4500;
  border-color: #FF4500;
}

.comment-text {
  color: #c0c0c0;
  margin: 0;
  line-height: 1.6;
  font-size: 0.95rem;
}

/* Footer */
.footer {
  text-align: center;
  padding: 2rem 0;
  margin-top: 4rem;
  border-top: 2px solid #2a2a2a;
}

.footer p {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.85rem;
  font-weight: 400;
  margin: 0;
  letter-spacing: 0.5px;
}

/* Animations */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.metric-card,
.sentiment-visual-section,
.indicator-card,
.risk-section,
.chart-section,
.recommendations-compact,
.risk-score-card,
.post-card {
  animation: fadeInUp 0.6s ease-out;
}

/* Additional Mobile Responsive Styles */
@media (max-width: 768px) {
  .stats {
    padding: 1rem;
  }

  .header-section {
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
  }

  .stats h1 {
    font-size: 1.8rem;
    word-break: break-word;
  }

  .search-query {
    display: block;
    margin-top: 0.5rem;
  }

  .intro-text {
    font-size: 0.9rem;
  }

  .metrics-grid {
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .metric-card {
    padding: 1.5rem 1rem;
  }

  .metric-icon {
    font-size: 2rem;
  }

  .metric-value {
    font-size: 2rem;
  }

  .metric-label {
    font-size: 0.8rem;
  }

  .external-api-section {
    padding: 1.5rem 1rem;
    margin-bottom: 2rem;
  }

  .external-api-section h2 {
    font-size: 1.5rem;
  }

  .api-results-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .api-card {
    padding: 1.2rem;
  }

  .technical-checks-section {
    margin-top: 1.5rem;
    padding-top: 1.5rem;
  }

  .technical-checks-section h3 {
    font-size: 1.2rem;
  }

  .checks-grid {
    grid-template-columns: 1fr;
    gap: 0.8rem;
  }

  .check-item {
    padding: 1rem;
  }

  .layout-container {
    grid-template-columns: 1fr;
    gap: 1.5rem;
    margin-bottom: 2rem;
  }

  .sentiment-visual-section,
  .indicators-section,
  .risk-section,
  .chart-section,
  .recommendations-compact,
  .risk-score-card {
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }

  .sentiment-visual-section h2,
  .risk-section h2,
  .chart-section h2 {
    font-size: 1.3rem;
    margin-bottom: 1.5rem;
  }

  .indicator-card {
    padding: 1.5rem;
  }

  .indicator-card h3 {
    font-size: 1rem;
  }

  .risk-score-value {
    font-size: 3rem;
  }

  .top-posts-section h2 {
    font-size: 1.5rem;
  }

  .reddit-posts {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .post-card {
    padding: 1.5rem;
  }

  .post-card h3 {
    font-size: 1.1rem;
    padding-right: 50px;
  }

  .post-rank {
    width: 40px;
    height: 40px;
    font-size: 1.2rem;
    top: 1rem;
    right: 1rem;
  }

  .comment {
    padding-left: 3.5rem;
    padding: 1rem;
    padding-left: 3.5rem;
  }

  .comment-score-badge {
    width: 35px;
    height: 35px;
    font-size: 0.8rem;
  }

  .footer {
    margin-top: 3rem;
    padding: 1.5rem 0;
  }

  .footer p {
    font-size: 0.75rem;
  }
}

@media (max-width: 480px) {
  .stats {
    padding: 0.75rem;
  }

  .stats h1 {
    font-size: 1.5rem;
  }

  .metric-card {
    padding: 1.2rem 0.8rem;
  }

  .metric-value {
    font-size: 1.8rem;
  }

  .api-card,
  .check-item,
  .post-card {
    padding: 1rem;
  }

  .post-card h3 {
    font-size: 1rem;
  }

  .sentiment-visual-section,
  .risk-section,
  .chart-section {
    padding: 1.2rem;
  }
}
</style>

