<template>
  <router-view/>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background: #0a0a0a;
  min-height: 100vh;
}

#app {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  min-height: 100vh;
}

nav {
  padding: 30px;
  background: rgba(18, 18, 18, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 30px rgba(255, 69, 0, 0.2);
  border-bottom: 2px solid #FF4500;
}

nav a {
  font-weight: 500;
  color: #b0b0b0;
  text-decoration: none;
  margin: 0 15px;
  transition: all 0.3s ease;
  position: relative;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  font-size: 0.85rem;
}

nav a::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 0;
  width: 0;
  height: 2px;
  background: linear-gradient(90deg, #FF4500, #ff6a33);
  transition: width 0.3s ease;
  box-shadow: 0 0 10px rgba(255, 69, 0, 0.5);
}

nav a:hover::after,
nav a.router-link-exact-active::after {
  width: 100%;
}

nav a:hover {
  color: #FF4500;
  text-shadow: 0 0 8px rgba(255, 69, 0, 0.3);
}

nav a.router-link-exact-active {
  color: #FF4500;
}
</style>
