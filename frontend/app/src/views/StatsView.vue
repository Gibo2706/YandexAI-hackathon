<template>
  <div class="stats">
    <div class="header-section">
      <h1>Community Analysis Report</h1>
      <p class="intro-text">Based on real Reddit discussions and user experiences from across multiple communities</p>
    </div>
    
    <!-- Key Metrics Cards -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-icon">📊</div>
        <div class="metric-value">{{ redditData.length }}</div>
        <div class="metric-label">Posts Analyzed</div>
      </div>
      <div class="metric-card">
        <div class="metric-icon">💬</div>
        <div class="metric-value">{{ totalComments }}</div>
        <div class="metric-label">Comments Reviewed</div>
      </div>
      <div class="metric-card">
        <div class="metric-icon">📈</div>
        <div class="metric-value">{{ (sentimentData.legit * 100).toFixed(0) }}%</div>
        <div class="metric-label">Positive Sentiment</div>
      </div>
      <div class="metric-card">
        <div class="metric-icon">⚠️</div>
        <div class="metric-value">{{ (sentimentData.scam * 100).toFixed(0) }}%</div>
        <div class="metric-label">Negative Sentiment</div>
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
    <div class="top-posts-section">
      <h2>Top Reddit Discussions</h2>
      <p class="section-description">Most discussed posts about Kiwi.com on Reddit</p>
      
      <div class="reddit-posts">
        <div v-for="(item, index) in topPosts" :key="index" class="post-card">
          <div class="post-rank">{{ index + 1 }}</div>
          <div class="post-header">
            <span class="subreddit">r/{{ item.post.subreddit }}</span>
            <div class="post-stats">
              <span class="post-stat">
                <span class="stat-icon">▲</span>
                {{ item.post.score }}
              </span>
              <span class="post-stat">
                <span class="stat-icon">💬</span>
                {{ item.post.num_comments }}
              </span>
            </div>
          </div>
          <h3>{{ item.post.title }}</h3>
          <p class="post-text">{{ item.post.text }}</p>
          
          <div class="comments-section">
            <div class="comments-header">
              <h4>Top Comments</h4>
              <span class="comments-count">{{ item.comments.length }} comments</span>
            </div>
            <div v-for="(comment, cIndex) in item.comments" :key="cIndex" class="comment" :class="{ 'negative': comment.score < 0, 'positive': comment.score > 0 }">
              <div class="comment-score-badge" :class="{ 'score-negative': comment.score < 0, 'score-positive': comment.score > 0 }">
                {{ comment.score > 0 ? '+' : '' }}{{ comment.score }}
              </div>
              <p class="comment-text">{{ comment.text }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <footer class="footer">
      <p>&copy; 2025 The Sthrokaders | AI NATION Hackathon by Yandex & Repute</p>
    </footer>
  </div>
</template>

<script>
import redditData, { 
  getSentimentPercentages, 
  getAnalysisMetrics,
  getKeyIndicators,
  getRiskFactors,
  getDecisionFactors,
  getWordAnalysis,
  getRecommendations
} from '@/data/data.js'

export default {
  name: 'StatsView',
  data() {
    return {
      redditData: redditData,
      sentimentData: getSentimentPercentages(),
      metrics: getAnalysisMetrics(),
      keyIndicators: getKeyIndicators(),
      riskFactors: getRiskFactors(),
      decisionFactors: getDecisionFactors(),
      wordAnalysis: getWordAnalysis(),
      recommendations: getRecommendations()
    }
  },
  computed: {
    topPosts() {
      return [...this.redditData]
        .sort((a, b) => b.post.score - a.post.score)
        .slice(0, 5);
    },
    totalComments() {
      return this.redditData.reduce((sum, item) => sum + item.comments.length, 0);
    }
  },
  methods: {
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
</style>

