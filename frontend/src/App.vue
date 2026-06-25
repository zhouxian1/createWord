<template>
  <div class="app-shell">
    <div class="bg-glow glow-a"></div>
    <div class="bg-glow glow-b"></div>
    <router-view />
  </div>
</template>

<script setup>
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
  font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
}

.app-shell {
  position: relative;
  min-height: 100%;
}

.bg-glow {
  position: fixed;
  width: 360px;
  height: 360px;
  border-radius: 50%;
  filter: blur(110px);
  z-index: 0;
  pointer-events: none;
  opacity: 0.12;
}

.glow-a {
  top: -100px;
  left: -80px;
  background: rgba(89, 184, 255, 0.5);
}

.glow-b {
  right: -120px;
  bottom: -100px;
  background: rgba(159, 134, 255, 0.42);
}
</style>
