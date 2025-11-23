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

    <!-- Flags Section -->
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
    }
  }
}
</script>

<style scoped>
/* Base Styles */
.stats {
  min-height: 100vh;
  background: #0a0a0a;
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

/* Hero Section */
.hero-section {
  text-align: center;
  padding: 3rem 0;
  border-bottom: 2px solid #FF4500;
  margin-bottom: 3rem;
}

.query-title {
  font-size: 3rem;
  font-weight: 700;
  color: #FFFFFF;
  margin: 0 0 1rem 0;
  letter-spacing: -1px;
  word-break: break-word;
}

.analysis-meta {
  font-size: 1.1rem;
  color: #808080;
  margin: 0;
}

.analysis-meta strong {
  color: #FF4500;
  font-weight: 700;
}

/* Verdict Card */
.verdict-card {
  background: #1a1a1a;
  border: 3px solid #2a2a2a;
  padding: 2.5rem;
  margin-bottom: 3rem;
  transition: all 0.3s ease;
}

.verdict-card.verdict-avoid {
  border-color: #DC2626;
  background: linear-gradient(135deg, #1a0a0a 0%, #1a1a1a 100%);
}

.verdict-card.verdict-high-caution {
  border-color: #EA580C;
  background: linear-gradient(135deg, #1a0f0a 0%, #1a1a1a 100%);
}

.verdict-card.verdict-investigate {
  border-color: #EAB308;
  background: linear-gradient(135deg, #1a1a0a 0%, #1a1a1a 100%);
}

.verdict-card.verdict-low-risk {
  border-color: #22C55E;
  background: linear-gradient(135deg, #0a1a0a 0%, #1a1a1a 100%);
}

.verdict-card.verdict-safe {
  border-color: #16A34A;
  background: linear-gradient(135deg, #0a1a0f 0%, #1a1a1a 100%);
}

.verdict-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1.5rem;
}

.verdict-badge {
  background: #FF4500;
  color: white;
  padding: 0.75rem 2rem;
  font-size: 1.2rem;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.verdict-avoid .verdict-badge {
  background: #DC2626;
}

.verdict-high-caution .verdict-badge {
  background: #EA580C;
}

.verdict-investigate .verdict-badge {
  background: #EAB308;
  color: #0a0a0a;
}

.verdict-low-risk .verdict-badge {
  background: #22C55E;
  color: #0a0a0a;
}

.verdict-safe .verdict-badge {
  background: #16A34A;
}

.verdict-score-display {
  text-align: right;
}

.score-number {
  font-size: 4rem;
  font-weight: 700;
  color: #FF4500;
  line-height: 1;
  letter-spacing: -2px;
}

.score-label {
  font-size: 0.9rem;
  color: #808080;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-top: 0.5rem;
}

.confidence-bar-wrapper {
  margin-bottom: 2rem;
}

.confidence-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.75rem;
  font-weight: 600;
  color: #c0c0c0;
}

.confidence-value {
  color: #FF4500;
  font-size: 1.2rem;
}

.confidence-bar {
  height: 12px;
  background: #0a0a0a;
  border: 2px solid #2a2a2a;
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  background: linear-gradient(90deg, #FF4500 0%, #ff8844 100%);
  transition: width 1s ease;
}

.verdict-summary {
  font-size: 1.1rem;
  line-height: 1.7;
  color: #b0b0b0;
  margin: 0;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
  margin-bottom: 3rem;
}

@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}

.stat-card {
  background: #1a1a1a;
  border: 2px solid #2a2a2a;
  padding: 2rem 1.5rem;
  text-align: center;
  transition: all 0.3s ease;
}

.stat-card:hover {
  border-color: #FF4500;
  transform: translateY(-5px);
}

.stat-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: #FF4500;
  margin-bottom: 0.5rem;
  letter-spacing: -1px;
}

.stat-label {
  font-size: 0.9rem;
  color: #808080;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 600;
}

/* Two Column Layout */
.two-column-layout {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2rem;
  margin-bottom: 3rem;
}

@media (max-width: 768px) {
  .two-column-layout {
    grid-template-columns: 1fr;
  }
}

/* Findings Sections */
.findings-section {
  background: #1a1a1a;
  border: 2px solid #2a2a2a;
  padding: 2rem;
}

.red-flags-section {
  border-top: 3px solid #FF4500;
}

.green-flags-section {
  border-top: 3px solid #16A34A;
}

.section-title {
  color: #e0e0e0;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 0 1.5rem 0;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.title-icon {
  font-size: 1.8rem;
}

.findings-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.finding-item {
  padding: 1rem 0;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  border-bottom: 1px solid #2a2a2a;
}

.finding-item:last-child {
  border-bottom: none;
}

.finding-bullet {
  width: 8px;
  height: 8px;
  flex-shrink: 0;
  margin-top: 0.5rem;
}

.finding-item.red .finding-bullet {
  background: #FF4500;
}

.finding-item.green .finding-bullet {
  background: #16A34A;
}

.finding-text {
  color: #c0c0c0;
  line-height: 1.6;
  flex: 1;
}

.no-data-message {
  color: #606060;
  font-style: italic;
  text-align: center;
  padding: 2rem 0;
}

/* Consensus Section */
.consensus-section {
  margin-bottom: 3rem;
}

.consensus-card {
  background: #1a1a1a;
  border: 2px solid #2a2a2a;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.consensus-badge {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  font-size: 1.1rem;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  align-self: flex-start;
}

.consensus-badge.consensus-agreement {
  background: #16A34A;
  color: white;
}

.consensus-badge.consensus-controversial {
  background: #DC2626;
  color: white;
}

.consensus-badge.consensus-mixed {
  background: #EAB308;
  color: #0a0a0a;
}

.consensus-stats {
  display: flex;
  gap: 2rem;
}

.consensus-stat {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.consensus-stat .stat-label {
  color: #808080;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.consensus-stat .stat-value {
  color: #FF4500;
  font-size: 2rem;
  font-weight: 700;
}

/* Scam Mentions Section */
.scam-mentions-section {
  margin-bottom: 3rem;
}

.mentions-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

@media (max-width: 768px) {
  .mentions-grid {
    grid-template-columns: 1fr;
  }
}

.mention-card {
  background: #1a1a1a;
  border: 2px solid #2a2a2a;
  padding: 2rem;
  text-align: center;
  transition: all 0.3s ease;
}

.mention-card:hover {
  transform: translateY(-3px);
}

.mention-card.danger {
  border-top: 3px solid #DC2626;
}

.mention-card.warning {
  border-top: 3px solid #EAB308;
}

.mention-card.positive {
  border-top: 3px solid #16A34A;
}

.mention-value {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.mention-card.danger .mention-value {
  color: #DC2626;
}

.mention-card.warning .mention-value {
  color: #EAB308;
}

.mention-card.positive .mention-value {
  color: #16A34A;
}

.mention-label {
  color: #808080;
  font-size: 0.95rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

/* Key Points Section */
.key-points-section {
  margin-bottom: 3rem;
}

.key-points-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.key-point-card {
  background: #1a1a1a;
  border: 2px solid #2a2a2a;
  border-left: 3px solid #FF4500;
  padding: 1.5rem;
  display: flex;
  align-items: flex-start;
  gap: 1.5rem;
  transition: all 0.3s ease;
}

.key-point-card:hover {
  background: #252525;
  border-left-color: #ff8844;
}

.point-number {
  width: 36px;
  height: 36px;
  background: #FF4500;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.point-text {
  color: #c0c0c0;
  line-height: 1.6;
  flex: 1;
  font-size: 1.05rem;
}

/* Discussions Section */
.discussions-section {
  margin-bottom: 3rem;
}

.discussions-list {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.discussion-card {
  background: #1a1a1a;
  border: 2px solid #2a2a2a;
  padding: 2rem;
  transition: all 0.3s ease;
}

.discussion-card:hover {
  border-color: #FF4500;
}

.discussion-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.discussion-rank {
  background: #FF4500;
  color: white;
  padding: 0.5rem 1rem;
  font-weight: 700;
  font-size: 1rem;
}

.subreddit-badge {
  background: #2a2a2a;
  color: #FF4500;
  padding: 0.5rem 1rem;
  font-weight: 600;
  font-size: 0.9rem;
}

.discussion-score {
  color: #808080;
  font-size: 0.9rem;
  margin-left: auto;
}

.discussion-title {
  color: #e0e0e0;
  font-size: 1.3rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
  line-height: 1.4;
}

.discussion-stats {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #808080;
  font-size: 0.9rem;
}

.stat-item .stat-icon {
  font-size: 1rem;
}

.discussion-scam-analysis {
  display: flex;
  gap: 1.5rem;
  padding: 1rem 0;
  border-top: 1px solid #2a2a2a;
  margin-top: 1rem;
}

.scam-mini-stat {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.mini-label {
  color: #808080;
  font-size: 0.9rem;
}

.mini-value {
  font-weight: 700;
  font-size: 1.1rem;
}

.mini-value.danger {
  color: #DC2626;
}

.mini-value.positive {
  color: #16A34A;
}

.thread-consensus {
  padding: 0.75rem 0;
  border-top: 1px solid #2a2a2a;
  margin-top: 1rem;
}

.consensus-label {
  color: #808080;
  font-size: 0.9rem;
  margin-right: 0.5rem;
}

.consensus-value {
  font-weight: 600;
  font-size: 0.95rem;
}

.consensus-value.consensus-strong {
  color: #16A34A;
}

.consensus-value.consensus-controversial {
  color: #DC2626;
}

.consensus-value.consensus-mixed {
  color: #EAB308;
}

/* Reasoning Section */
.reasoning-section {
  margin-bottom: 3rem;
}

.reasoning-card {
  background: #1a1a1a;
  border: 2px solid #2a2a2a;
  border-left: 4px solid #FF4500;
  padding: 2rem;
}

.reasoning-text {
  color: #c0c0c0;
  line-height: 1.8;
  font-size: 1.05rem;
  margin: 0;
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
  margin: 0;
  letter-spacing: 0.5px;
}

/* Responsive */
@media (max-width: 768px) {
  .stats {
    padding: 1rem;
  }

  .hero-section {
    padding: 2rem 0;
  }

  .query-title {
    font-size: 2rem;
  }

  .verdict-card {
    padding: 1.5rem;
  }

  .verdict-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .verdict-score-display {
    text-align: left;
  }

  .score-number {
    font-size: 3rem;
  }

  .findings-section,
  .consensus-card,
  .reasoning-card,
  .discussion-card {
    padding: 1.5rem;
  }

  .section-title {
    font-size: 1.2rem;
  }

  .discussion-header {
    font-size: 0.9rem;
  }

  .discussion-title {
    font-size: 1.1rem;
  }
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

.verdict-card,
.stat-card,
.findings-section,
.consensus-card,
.mention-card,
.key-point-card,
.discussion-card,
.reasoning-card {
  animation: fadeInUp 0.6s ease-out;
}
</style>
