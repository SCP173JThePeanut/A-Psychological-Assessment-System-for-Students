<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
// 不需要额外逻辑
</script>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  width: 100%;
  min-height: 100vh;
  overflow-x: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans SC', sans-serif;
  background: linear-gradient(135deg, #f8fafc 0%, #e8f4f3 100%);
  color: #2c3e50;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* 响应式容器 */
.container {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 工具类 */
.text-center { text-align: center; }
.text-left { text-align: left; }
.text-right { text-align: right; }

.m-0 { margin: 0; }
.p-0 { padding: 0; }

.w-100 { width: 100%; }
.h-100 { height: 100%; }
.min-h-100vh { min-height: 100vh; }

.d-flex { display: flex; }
.flex-column { flex-direction: column; }
.flex-wrap { flex-wrap: wrap; }
.justify-center { justify-content: center; }
.justify-between { justify-content: space-between; }
.align-center { align-items: center; }
.align-stretch { align-items: stretch; }

/* 响应式断点 */
@media (max-width: 1200px) {
  .container {
    max-width: 100%;
    padding: 0 16px;
  }
}

@media (max-width: 768px) {
  .container {
    padding: 0 12px;
  }
}
</style>