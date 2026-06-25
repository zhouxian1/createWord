<template>
  <div class="app-shell">
    <div class="bg-orb orb-a"></div>
    <div class="bg-orb orb-b"></div>
    <div class="bg-grid"></div>
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

.bg-orb {
  position: fixed;
  width: 420px;
  height: 420px;
  border-radius: 50%;
  filter: blur(90px);
  z-index: 0;
  pointer-events: none;
  opacity: 0.35;
}

.orb-a {
  top: -120px;
  left: -120px;
  background: rgba(63, 166, 255, 0.45);
}

.orb-b {
  right: -140px;
  bottom: -140px;
  background: rgba(154, 124, 255, 0.3);
}

.bg-grid {
  position: fixed;
  inset: 0;
  background-image:
    linear-gradient(rgba(89, 184, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(89, 184, 255, 0.03) 1px, transparent 1px);
  background-size: 44px 44px;
  mask-image: linear-gradient(180deg, rgba(255, 255, 255, 0.32), transparent 78%);
  pointer-events: none;
  z-index: 0;
}
</style>
