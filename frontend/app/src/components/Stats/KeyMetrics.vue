<template>
  <div class="metrics-grid">
    <div class="metric-card">
      <div class="metric-icon">📊</div>
      <div class="metric-value">{{ metrics.totalPosts }}</div>
      <div class="metric-label">Posts Analyzed</div>
    </div>
    <div class="metric-card">
      <div class="metric-icon">💬</div>
      <div class="metric-value">{{ metrics.totalComments }}</div>
      <div class="metric-label">Comments Reviewed</div>
    </div>
    <div class="metric-card">
      <div class="metric-icon">📈</div>
      <div class="metric-value">{{ (sentiment.legit * 100).toFixed(0) }}%</div>
      <div class="metric-label">Positive Sentiment</div>
    </div>
    <div class="metric-card">
      <div class="metric-icon">⚠️</div>
      <div class="metric-value">{{ (sentiment.scam * 100).toFixed(0) }}%</div>
      <div class="metric-label">Negative Sentiment</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'KeyMetrics',
  props: {
    metrics: {
      type: Object,
      required: true
    },
    sentiment: {
      type: Object,
      required: true
    }
  }
}
</script>

<style scoped>
/* Uses the same class names as StatsView.vue; no extra styles needed here. */
</style>
