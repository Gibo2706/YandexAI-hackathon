<template>
  <div class="top-posts-section" v-if="posts && posts.length">
    <h2>Top Reddit Discussions</h2>
    <p class="section-description">Most discussed posts about {{ prompt }} on Reddit</p>
    
    <div class="reddit-posts">
      <div v-for="(item, index) in posts" :key="index" class="post-card">
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
        
        <div class="comments-section" v-if="item.comments && item.comments.length">
          <div class="comments-header">
            <h4>Top Comments / Signals</h4>
            <span class="comments-count">{{ item.comments.length }} items</span>
          </div>
          <div
            v-for="(comment, cIndex) in item.comments"
            :key="cIndex"
            class="comment"
            :class="{ 'negative': comment.score < 0, 'positive': comment.score > 0 }"
          >
            <div
              class="comment-score-badge"
              :class="{ 'score-negative': comment.score < 0, 'score-positive': comment.score > 0 }"
            >
              {{ comment.score > 0 ? '+' : '' }}{{ comment.score }}
            </div>
            <p class="comment-text">{{ comment.text }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TopPosts',
  props: {
    posts: {
      type: Array,
      required: true
    },
    prompt: {
      type: String,
      required: true
    }
  }
}
</script>

<style scoped>
/* Uses the same class names as StatsView.vue; no extra styles needed here. */
</style>
