<template>
  <Transition name="fade">
    <div v-if="show" class="loading-overlay">
      <div class="loading-container">
        <!-- 水墨动画 -->
        <div class="ink-animation">
          <div class="ink-drop"></div>
          <div class="ink-ripple ripple-1"></div>
          <div class="ink-ripple ripple-2"></div>
          <div class="ink-ripple ripple-3"></div>
        </div>
        
        <!-- 加载文本 -->
        <div class="loading-content">
          <h3 class="loading-title">{{ title }}</h3>
          <p class="loading-subtitle">{{ subtitle }}</p>
          
          <!-- 进度条 -->
          <div class="progress-container">
            <div class="progress-track">
              <div class="progress-bar" :style="{ width: progress + '%' }"></div>
            </div>
            <div class="progress-text">
              <span>{{ progress }}%</span>
              <span class="progress-dots">
                <span class="dot" :class="{ active: dotActive }">.</span>
                <span class="dot" :class="{ active: dotActive && progress >= 33 }">.</span>
                <span class="dot" :class="{ active: dotActive && progress >= 66 }">.</span>
              </span>
            </div>
          </div>
        </div>
        
        <!-- 提示信息 -->
        <div v-if="tips.length > 0" class="loading-tips">
          <p class="tip-text">{{ currentTip }}</p>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: '正在生成报告'
  },
  subtitle: {
    type: String,
    default: 'AI正在分析您的心理状态，请稍候...'
  },
  duration: {
    type: Number,
    default: 3000 // 加载总时长（毫秒）
  }
})

const progress = ref(0)
const dotActive = ref(false)
const tips = ref([
  '正在分析面部表情特征...',
  '正在处理语音情感数据...',
  '正在计算心率变异性指标...',
  '正在整合多模态数据...',
  '正在生成专业评估报告...'
])
const currentTipIndex = ref(0)

const currentTip = computed(() => tips.value[currentTipIndex.value])

let interval = null
let tipInterval = null

const startProgress = () => {
  progress.value = 0
  dotActive.value = true
  currentTipIndex.value = 0
  
  // 进度条动画
  interval = setInterval(() => {
    if (progress.value < 100) {
      const increment = Math.random() * 10
      progress.value = Math.min(100, progress.value + increment)
    } else {
      clearInterval(interval)
    }
  }, props.duration / 20) // 分20步完成

  // 提示文本切换
  tipInterval = setInterval(() => {
    currentTipIndex.value = (currentTipIndex.value + 1) % tips.value.length
  }, 800)
}

const stopProgress = () => {
  progress.value = 100
  dotActive.value = false
  if (interval) clearInterval(interval)
  if (tipInterval) clearInterval(tipInterval)
}

watch(() => props.show, (newVal) => {
  if (newVal) {
    startProgress()
  } else {
    setTimeout(stopProgress, 500)
  }
})

onMounted(() => {
  if (props.show) {
    startProgress()
  }
})

onUnmounted(() => {
  stopProgress()
})
</script>

<style scoped>
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, 
    rgba(248, 250, 252, 0.98) 0%,
    rgba(232, 244, 243, 0.98) 100%
  );
  backdrop-filter: blur(10px);
  z-index: var(--z-index-modal);
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xl);
  padding: var(--spacing-2xl);
  background: rgba(255, 255, 255, 0.95);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  border: 1px solid var(--color-border);
  max-width: 480px;
  width: 90%;
  position: relative;
  overflow: hidden;
}

/* 水墨动画 */
.ink-animation {
  position: relative;
  width: 120px;
  height: 120px;
}

.ink-drop {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 40px;
  height: 40px;
  background: var(--color-primary);
  border-radius: 50%;
  animation: inkDrop 2s ease-in-out infinite;
  filter: blur(2px);
  opacity: 0.8;
  z-index: 1;
}

.ink-ripple {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 40px;
  height: 40px;
  border: 2px solid var(--color-primary);
  opacity: 0;
  border-radius: 50%;
  animation: inkRipple 2s ease-out infinite;
  z-index: 0;
}

.ripple-1 { animation-delay: 0s; }
.ripple-2 { animation-delay: 0.5s; }
.ripple-3 { animation-delay: 1s; }

@keyframes inkDrop {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.8;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.1);
    opacity: 1;
  }
}

@keyframes inkRipple {
  0% {
    width: 40px;
    height: 40px;
    opacity: 0.8;
  }
  100% {
    width: 120px;
    height: 120px;
    opacity: 0;
  }
}

/* 加载内容 */
.loading-content {
  text-align: center;
  width: 100%;
}

.loading-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-primary-dark);
  margin-bottom: var(--spacing-sm);
  font-family: var(--font-family-title);
  letter-spacing: 1px;
}

.loading-subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xl);
  line-height: 1.6;
}

/* 进度条 */
.progress-container {
  width: 100%;
  max-width: 300px;
  margin: 0 auto;
}

.progress-track {
  width: 100%;
  height: 6px;
  background: var(--color-border);
  border-radius: var(--radius-full);
  overflow: hidden;
  margin-bottom: var(--spacing-sm);
}

.progress-bar {
  height: 100%;
  background: linear-gradient(
    90deg,
    var(--color-primary-light),
    var(--color-primary),
    var(--color-primary-dark)
  );
  border-radius: var(--radius-full);
  transition: width var(--transition-normal);
  box-shadow: 0 0 8px rgba(78, 205, 196, 0.3);
}

.progress-text {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--font-size-sm);
  color: var(--color-text-light);
}

.progress-dots {
  display: flex;
  gap: 2px;
}

.dot {
  color: var(--color-primary);
  font-size: var(--font-size-lg);
  line-height: 1;
  transition: all var(--transition-fast);
  opacity: 0.3;
}

.dot.active {
  opacity: 1;
  transform: scale(1.2);
}

/* 提示信息 */
.loading-tips {
  margin-top: var(--spacing-lg);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-border);
  text-align: center;
  width: 100%;
}

.tip-text {
  font-size: var(--font-size-sm);
  color: var(--color-primary-dark);
  font-style: italic;
  animation: tipFade 0.8s ease-in-out;
}

@keyframes tipFade {
  0% { opacity: 0; transform: translateY(5px); }
  100% { opacity: 1; transform: translateY(0); }
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-normal) ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>