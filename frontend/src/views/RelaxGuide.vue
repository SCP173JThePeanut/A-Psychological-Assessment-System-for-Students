<template>
  <div class="relax-guide-watercolor">
    <!-- 水墨风背景 -->
    <div class="watercolor-bg">
      <div class="watercolor-layer layer-1" style="background: radial-gradient(circle at 20% 30%, rgba(78, 205, 196, 0.08) 0%, transparent 50%);"></div>
      <div class="watercolor-layer layer-2" style="background: radial-gradient(circle at 80% 70%, rgba(42, 111, 121, 0.06) 0%, transparent 50%);"></div>
      <div class="watercolor-layer layer-3" style="background: radial-gradient(circle at 40% 80%, rgba(127, 211, 33, 0.04) 0%, transparent 50%);"></div>
      <div class="ink-drip ink-1"></div>
      <div class="ink-drip ink-2"></div>
      <div class="ink-drip ink-3"></div>
    </div>

    <!-- 主容器 -->
    <div class="main-container">
      <!-- 左侧导航面板 -->
      <div class="nav-panel">
        <div class="brand-section">
          <div class="logo-container">
            <div class="logo-icon">💮</div>
            <div class="logo-text">
              <h1>心镜·守望</h1>
              <p class="subtitle">心理健康多模态评估系统</p>
            </div>
          </div>
          
          <div class="progress-timeline">
            <div class="timeline-step" :class="{ active: currentStep >= 1, completed: currentStep > 1 }">
              <div class="step-marker">
                <span v-if="currentStep > 1">✓</span>
                <span v-else>1</span>
              </div>
              <div class="step-info">
                <h3>环境准备</h3>
                <p>创建理想评估环境</p>
              </div>
              <div class="timeline-connector"></div>
            </div>
            
            <div class="timeline-step" :class="{ active: currentStep >= 2, completed: currentStep > 2 }">
              <div class="step-marker">
                <span v-if="currentStep > 2">✓</span>
                <span v-else>2</span>
              </div>
              <div class="step-info">
                <h3>呼吸调整</h3>
                <p>4-7-8呼吸法引导</p>
              </div>
              <div class="timeline-connector"></div>
            </div>
            
            <div class="timeline-step" :class="{ active: currentStep >= 3, completed: currentStep > 3 }">
              <div class="step-marker">
                <span v-if="currentStep > 3">✓</span>
                <span v-else>3</span>
              </div>
              <div class="step-info">
                <h3>身心放松</h3>
                <p>渐进式肌肉放松</p>
              </div>
              <div class="timeline-connector"></div>
            </div>
            
            <div class="timeline-step" :class="{ active: currentStep >= 4 }">
              <div class="step-marker">4</div>
              <div class="step-info">
                <h3>准备就绪</h3>
                <p>开始正式评估</p>
              </div>
            </div>
          </div>
          
          <div class="time-estimate-card">
            <div class="time-icon">⏳</div>
            <div class="time-info">
              <p class="time-label">预计完成时间</p>
              <p class="time-value">5-7分钟</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 主内容区域 -->
      <div class="content-panel">
        <!-- 步骤内容 -->
        <div class="step-content-area">
          <!-- 步骤1: 环境准备 -->
          <div v-if="currentStep === 1" class="step-panel">
            <div class="step-header">
              <div class="step-icon">🍀</div>
              <div class="step-title">
                <h2>创建理想的评估环境</h2>
                <p class="step-description">请确保您处于以下理想状态，以获得最准确的评估结果</p>
              </div>
            </div>
            
            <div class="env-check-grid">
              <div class="env-card" 
                   :class="{ checked: envChecks.quiet }"
                   @click="envChecks.quiet = !envChecks.quiet">
                <div class="env-icon-wrapper">
                  <span class="env-icon">🔇</span>
                </div>
                <h3 class="env-title">安静环境</h3>
                <p class="env-desc">无噪音干扰，可专注进行评估</p>
                <div class="check-status" :class="{ checked: envChecks.quiet }">
                  {{ envChecks.quiet ? '✓ 已准备' : '点击准备' }}
                </div>
              </div>
              
              <div class="env-card" 
                   :class="{ checked: envChecks.comfortable }"
                   @click="envChecks.comfortable = !envChecks.comfortable">
                <div class="env-icon-wrapper">
                  <span class="env-icon">🪑</span>
                </div>
                <h3 class="env-title">舒适姿势</h3>
                <p class="env-desc">座椅舒适，身体放松不紧绷</p>
                <div class="check-status" :class="{ checked: envChecks.comfortable }">
                  {{ envChecks.comfortable ? '✓ 已准备' : '点击准备' }}
                </div>
              </div>
              
              <div class="env-card" 
                   :class="{ checked: envChecks.light }"
                   @click="envChecks.light = !envChecks.light">
                <div class="env-icon-wrapper">
                  <span class="env-icon">💡</span>
                </div>
                <h3 class="env-title">适宜光线</h3>
                <p class="env-desc">光线充足柔和，不刺眼</p>
                <div class="check-status" :class="{ checked: envChecks.light }">
                  {{ envChecks.light ? '✓ 已准备' : '点击准备' }}
                </div>
              </div>
              
              <div class="env-card" 
                   :class="{ checked: envChecks.undisturbed }"
                   @click="envChecks.undisturbed = !envChecks.undisturbed">
                <div class="env-icon-wrapper">
                  <span class="env-icon">🔒</span>
                </div>
                <h3 class="env-title">无干扰时段</h3>
                <p class="env-desc">未来5-10分钟无人打扰</p>
                <div class="check-status" :class="{ checked: envChecks.undisturbed }">
                  {{ envChecks.undisturbed ? '✓ 已准备' : '点击准备' }}
                </div>
              </div>
            </div>
            
            <div class="tech-notice-card">
              <div class="notice-header">
                <span class="notice-icon">📷</span>
                <h3>设备准备提示</h3>
              </div>
              <div class="notice-content">
                <p>评估过程中，系统将通过<strong>摄像头</strong>和<strong>麦克风</strong>采集面部表情、语音语调等生理数据。</p>
                <p class="notice-tip">请确保摄像头和麦克风正常工作，所有数据将被严格保密。</p>
              </div>
            </div>
          </div>

          <!-- 步骤2: 呼吸调整 - 修改为两行布局 -->
          <div v-else-if="currentStep === 2" class="step-panel">
            <!-- 第一行：深呼吸描述和呼吸技巧在同一行 -->
            <div class="breath-top-row">
              <!-- 左侧：深呼吸描述 -->
              <div class="breath-description-card">
                <div class="step-header-content">
                  <div class="step-icon">🌬️</div>
                  <div class="step-title">
                    <h2>深呼吸，平静心绪</h2>
                    <p class="step-description">跟随引导进行4-7-8呼吸法，帮助身心进入最佳状态</p>
                  </div>
                </div>
              </div>
              
              <!-- 右侧：呼吸技巧 -->
              <div class="breath-tips-card">
                <div class="tips-header">
                  <span class="tips-icon">✨</span>
                  <h3>呼吸技巧</h3>
                </div>
                <ul class="tips-list">
                  <li>保持呼吸平缓，不要过度用力</li>
                  <li>可以把手放在腹部感受呼吸</li>
                  <li>闭上眼睛效果更佳</li>
                  <li>完成4次完整循环即可继续</li>
                </ul>
              </div>
            </div>
            
            <!-- 第二行：呼吸动画 -->
            <div class="breath-guide-section">
              <div class="breath-visualizer">
                <div class="breath-animation-container">
                  <div class="breath-circle" :style="{
                    transform: `scale(${breathScale})`,
                    opacity: breathOpacity
                  }"></div>
                  <div class="breath-info-overlay">
                    <div class="breath-phase">{{ breathText }}</div>
                    <div class="breath-timer">{{ breathTimer }}s</div>
                    <div class="breath-cycle">第 {{ Math.min(breathCycle + 1, 4) }}/4 次</div>
                  </div>
                </div>
                
                <div class="breath-instructions">
                  <div class="instruction-card" :class="{ active: breathPhase === 'inhale' }">
                    <div class="instruction-number">1</div>
                    <div class="instruction-content">
                      <h4>吸气 4秒</h4>
                      <p>用鼻子缓慢吸气，感受气息充满肺部</p>
                    </div>
                  </div>
                  <div class="instruction-card" :class="{ active: breathPhase === 'hold' }">
                    <div class="instruction-number">2</div>
                    <div class="instruction-content">
                      <h4>屏息 7秒</h4>
                      <p>保持气息，让氧气充分吸收</p>
                    </div>
                  </div>
                  <div class="instruction-card" :class="{ active: breathPhase === 'exhale' }">
                    <div class="instruction-number">3</div>
                    <div class="instruction-content">
                      <h4>呼气 8秒</h4>
                      <p>用嘴巴缓慢呼气，释放所有压力</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 步骤3: 身心放松 -->
          <div v-else-if="currentStep === 3" class="step-panel">
            <div class="step-header">
              <div class="step-icon">🧘</div>
              <div class="step-title">
                <h2>渐进式肌肉放松</h2>
                <p class="step-description">从脚底到头顶，逐步释放身体各部位的紧张感</p>
              </div>
            </div>
            
            <div class="relaxation-section">
              <!-- 顶部：音乐组件和当前放松部位 -->
              <div class="relaxation-top">
                <div class="audio-options">
                  <div class="audio-header">
                    <span class="audio-icon">🎵</span>
                    <h3>辅助放松音效（可选）</h3>
                  </div>
                  <p class="audio-desc">选择一种自然音效，帮助您更快进入放松状态</p>
                  
                  <!-- 新增：音效选择卡片 -->
                  <div class="audio-selection">
                    <div v-for="audio in audioOptions" 
                         :key="audio.id" 
                         class="audio-card" 
                         :class="{ selected: selectedAudio.id === audio.id }"
                         @click="changeAudio(audio)">
                      <div class="audio-icon">{{ audio.icon }}</div>
                      <div class="audio-info">
                        <h4>{{ audio.name }}</h4>
                        <p>{{ audio.description }}</p>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 修改：音频控制区域 -->
                  <div class="audio-controls">
                    <button class="audio-btn" @click="toggleAudio">
                      {{ isAudioPlaying ? '⏸️ 暂停播放' : '▶️ 播放 ' + selectedAudio.name }}
                    </button>
                  </div>
                  
                  <!-- 新增：音频进度条 -->
                  <div class="audio-progress-container">
                    <input 
                      type="range" 
                      min="0" 
                      :max="audioDuration || 0" 
                      :value="audioCurrentTime" 
                      @input="audioCurrentTime = $event.target.value; audioElement.currentTime = audioCurrentTime"
                      class="audio-progress-bar">
                    <div class="audio-time-display">
                      <span class="current-time">{{ formatTime(audioCurrentTime) }}</span>
                      <span class="duration">{{ formatTime(audioDuration) }}</span>
                    </div>
                  </div>
                </div>
                  
              <div class="current-focus">
                <div class="focus-info">
                  <p class="focus-label">当前放松部位</p>
                  <h3 class="focus-part">{{ activeBodyPart }}</h3>
                  <p class="focus-instruction">{{ getBodyPartInstruction(activeBodyPart) }}</p>
                </div>
              </div>
            </div>
                                                    
              
              <!-- 中间：身体示意图和放松步骤 -->
              <div class="relaxation-main">
                <div class="body-visual-area">
                  <!-- 身体示意图 -->
                  <div class="body-silhouette">
                    <div class="body-part" 
                         v-for="part in bodyParts" 
                         :key="part"
                         :class="{ 
                           active: activeBodyPart === part,
                           completed: bodyParts.indexOf(activeBodyPart) > bodyParts.indexOf(part)
                         }"
                         :style="getBodyPartStyle(part)">
                      <span class="part-label">{{ getBodyPartLabel(part) }}</span>
                    </div>
                  </div>
                </div>
                
                <div class="relaxation-steps">
                  <div class="steps-header">
                    <!-- <span class="steps-icon">📋</span> -->
                    <h3>放松步骤</h3>
                  </div>
                  <div class="steps-list">
                    <div class="step-item" 
                         v-for="(part, index) in bodyParts" 
                         :key="part"
                         :class="{ 
                           completed: bodyParts.indexOf(activeBodyPart) > index,
                           current: activeBodyPart === part
                         }">
                      <span class="step-index">{{ index + 1 }}</span>
                      <span class="step-name">{{ part }}</span>
                      <span class="step-duration">放松5秒</span>
                      <span v-if="bodyParts.indexOf(activeBodyPart) > index" class="step-check">✓</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 步骤4: 准备就绪 -->
          <div v-else-if="currentStep === 4" class="step-panel">
            <div class="step-header">
              <div class="step-icon">✨</div>
              <div class="step-title">
                <h2>准备就绪，开始评估</h2>
                <p class="step-description">您已完成所有准备工作，可以开始正式的心理健康评估</p>
              </div>
            </div>
            
            <div class="readiness-overview">
              <div class="readiness-card">
                <div class="readiness-icon">✅</div>
                <div class="readiness-content">
                  <h3>环境就绪</h3>
                  <p>已创建理想的评估环境</p>
                </div>
              </div>
              
              <div class="readiness-card">
                <!-- <div class="readiness-icon">🌬️</div> -->
                <div class="readiness-content">
                  <h3>呼吸平稳</h3>
                  <p>已完成4轮呼吸调整</p>
                </div>
              </div>
              
              <div class="readiness-card">
                <!-- <div class="readiness-icon">🧘</div> -->
                <div class="readiness-content">
                  <h3>身心放松</h3>
                  <p>已完成全身肌肉放松</p>
                </div>
              </div>
            </div>
            
            <div class="assessment-instructions">
              <div class="instructions-grid">
                <div class="instruction-item">
                    <div>
                    <h4>评估时长</h4>
                    <p>约5-8分钟，请确保全程专注</p>
                  </div>
                </div>
                <div class="instruction-item">
                 
                  <div>
                    <h4>评估方式</h4>
                    <p>结合心理量表与多模态数据分析</p>
                  </div>
                </div>
                <div class="instruction-item">
                  <div>
                    <h4>问题类型</h4>
                    <p>情境判断与自我状态评估</p>
                  </div>
                </div>
                <div class="instruction-item">
                  <!-- <div class="item-icon">🔐</div> -->
                  <div>
                    <h4>数据安全</h4>
                    <p>所有数据加密存储，仅用于本次评估</p>
                  </div>
                </div>
              </div>
              
              <div class="consent-section">
                <div class="consent-header">
                  <!-- <span class="consent-icon">📋</span> -->
                  <h3>评估须知</h3>
                </div>
                <div class="consent-content">
                  <p>评估过程中，系统将通过<b>摄像头和麦克风</b>采集面部表情、语音语调等数据。所有数据将被<b>严格保密</b>，仅用于本次心理健康评估。</p>
                  <label class="consent-agreement">
                    <input type="checkbox" v-model="consentGiven">
                    <span>我已阅读并同意《评估知情同意书》，并授权使用摄像头和麦克风进行数据采集</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 导航控制区 -->
        <div class="navigation-bar">
          <div class="nav-left">
            <button v-if="currentStep > 1" class="nav-btn back-btn" @click="prevStep">
              <span class="btn-icon">←</span> 返回上一步
            </button>
            <div v-else class="nav-spacer"></div>
          </div>
          
          <div class="nav-center">
            <div class="step-progress">
              <span class="current-step">步骤 {{ currentStep }}</span>
              <span class="step-separator">/</span>
              <span class="total-steps">4</span>
            </div>
          </div>
          
          <div class="nav-right">
            <button v-if="currentStep < 4" 
                    class="nav-btn next-btn" 
                    @click="nextStep" 
                    :disabled="currentStep === 1 && !allEnvChecksPassed"
                    :class="{ disabled: currentStep === 1 && !allEnvChecksPassed }">
              继续下一步
              <span class="btn-icon">→</span>
            </button>
            <button v-else 
                    class="nav-btn start-btn" 
                    @click="startAssessment"
                    :disabled="!consentGiven"
                    :class="{ disabled: !consentGiven }">
               开始正式评估
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 音频元素 -->
  <audio ref="audioElement" loop crossorigin="anonymous"></audio>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 当前步骤
const currentStep = ref(1)

// 环境检查状态
const envChecks = ref({
  quiet: false,
  comfortable: false,
  light: false,
  undisturbed: false
})

// 呼吸动画相关
const breathPhase = ref('inhale') // inhale, hold, exhale
const breathTimer = ref(4)
const breathScale = ref(1)
const breathOpacity = ref(0.7)
const breathText = ref('吸气...')
const breathCycle = ref(0)

// 音频控制
const activeBodyPart = ref('脚部')
const consentGiven = ref(false)

// 身体部位顺序（从下到上）
const bodyParts = ref(['脚部', '小腿', '大腿', '臀部', '腹部', '背部', '胸部', '手臂', '肩膀', '颈部', '面部', '头部'])

// 计算属性
const allEnvChecksPassed = computed(() => {
  return Object.values(envChecks.value).every(check => check)
})

// 获取身体部位样式
const getBodyPartStyle = (part) => {
  const index = bodyParts.value.indexOf(part)
  const total = bodyParts.value.length
  const top = 10 + (index / total) * 80 + '%'
  
  return {
    top: top
  }
}

// 获取身体部位标签
const getBodyPartLabel = (part) => {
  const labels = {
    '脚部': '脚',
    '小腿': '小腿',
    '大腿': '大腿',
    '臀部': '臀',
    '腹部': '腹',
    '背部': '背',
    '胸部': '胸',
    '手臂': '臂',
    '肩膀': '肩',
    '颈部': '颈',
    '面部': '面',
    '头部': '头'
  }
  return labels[part] || part
}

// 获取身体部位的专业放松指导

const getBodyPartInstruction = (part) => {
  const instructions = {
    '脚部': '用力勾紧脚趾5秒 → 彻底放松',
    '小腿': '脚尖勾起绷紧5秒 → 完全松开',
    '大腿': '收缩前侧肌肉5秒 → 缓缓放下',
    '臀部': '用力夹紧5秒 → 彻底释放',
    '腹部': '收紧核心5秒 → 长叹放松',
    '背部': '肩后收，夹背5秒 → 恢复自然',
    '胸部': '挺胸扩张5秒 → 含胸释放',
    '手臂': '握拳屈肘5秒 → 突然松开',
    '肩膀': '耸肩向上5秒 → 沉肩下拉',
    '颈部': '侧头拉伸5秒 → 缓慢回正',
    '面部': '皱紧面部5秒 → 彻底舒展',
    '头部': '向上牵引 → 释放紧张'
  }
  return instructions[part] || '请专注于这个部位，深呼吸，并有意识地释放所有紧张'
}
// 新增：音频选项
const audioOptions = ref([
  { id: 'wind', name: '风声', icon: '🌬️', file: '../../public/audio/forest-wind.mp3', description: '舒缓的森林风声' },
  { id: 'wave', name: '海浪声', icon: '🌊', file: '../../public/audio/ocean-wave.mp3', description: '平静的海浪拍岸' },
  { id: 'rain', name: '雨声', icon: '🌧️', file: '../../public/audio/rain-light.mp3', description: '轻柔的绵绵细雨' }
])

// 修改：音频控制相关状态
const selectedAudio = ref(audioOptions.value[0]) // 默认选中第一个选项（风声）
const isAudioPlaying = ref(false)
const audioVolume = ref(50)
const audioElement = ref(null) // 用于引用HTML Audio元素
const audioCurrentTime = ref(0) // 音频当前播放时间
const audioDuration = ref(0) // 音频总时长

// 修改：切换音频
const toggleAudio = () => {
  if (!audioElement.value) return
  
  if (isAudioPlaying.value) {
    audioElement.value.pause()
  } else {
    // 如果切换了音效，需要重新加载音频源
    if (audioElement.value.src !== selectedAudio.value.file) {
      audioElement.value.src = selectedAudio.value.file
      audioElement.value.load()
    }
    audioElement.value.play().catch(e => console.log("音频播放失败:", e))
  }
  isAudioPlaying.value = !isAudioPlaying.value
}

// 格式化时间
const formatTime = (seconds) => {
  if (!seconds || isNaN(seconds)) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs < 10 ? '0' : ''}${secs}`
}

// 新增：切换选择的音效
const changeAudio = (audio) => {
  if (selectedAudio.value.id === audio.id) return // 如果选择的是当前正在播放的，则不操作
  
  const wasPlaying = isAudioPlaying.value
  if (wasPlaying) {
    // 如果之前正在播放，先暂停当前音频
    audioElement.value.pause()
    isAudioPlaying.value = false
  }
  
  // 切换到新的音频
  selectedAudio.value = audio
  audioElement.value.src = audio.file
  audioElement.value.load()
  audioElement.value.volume = audioVolume.value / 100
  
  // 重置时间
  audioCurrentTime.value = 0
  audioDuration.value = 0
  
  if (wasPlaying) {
    // 如果之前是播放状态，则播放新选择的音频
    audioElement.value.play().catch(e => console.log("音频播放失败:", e))
    isAudioPlaying.value = true
  }
}

// 新增：音频事件监听设置
const setupAudioListeners = () => {
  if (!audioElement.value) return
  
  // 监听时间更新
  audioElement.value.addEventListener('timeupdate', () => {
    audioCurrentTime.value = audioElement.value.currentTime
  })
  
  // 监听音频元数据加载
  audioElement.value.addEventListener('loadedmetadata', () => {
    audioDuration.value = audioElement.value.duration
  })
  
  // 监听播放结束
  audioElement.value.addEventListener('ended', () => {
    isAudioPlaying.value = false
  })
  
  // 监听播放/暂停
  audioElement.value.addEventListener('play', () => {
    isAudioPlaying.value = true
  })
  
  audioElement.value.addEventListener('pause', () => {
    isAudioPlaying.value = false
  })
}

// 呼吸动画逻辑
let breathInterval = null
const initBreathAnimation = () => {
  if (breathInterval) clearInterval(breathInterval)
  
  breathInterval = setInterval(() => {
    breathTimer.value--
    
    if (breathTimer.value === 0) {
      switch (breathPhase.value) {
        case 'inhale':
          breathPhase.value = 'hold'
          breathTimer.value = 7
          breathText.value = '屏息...'
          break
        case 'hold':
          breathPhase.value = 'exhale'
          breathTimer.value = 8
          breathText.value = '呼气...'
          break
        case 'exhale':
          breathPhase.value = 'inhale'
          breathTimer.value = 4
          breathText.value = '吸气...'
          breathCycle.value++
          if (breathCycle.value >= 4) {
            clearInterval(breathInterval)
            breathText.value = '呼吸调整完成'
          }
          break
      }
    }
    
    // 更新动画效果
    if (breathPhase.value === 'inhale') {
      breathScale.value = 1 + (1 - breathTimer.value / 4) * 0.5
      breathOpacity.value = 0.7 + (1 - breathTimer.value / 4) * 0.3
    } else if (breathPhase.value === 'exhale') {
      breathScale.value = 1.5 - (1 - breathTimer.value / 8) * 0.5
      breathOpacity.value = 1 - (1 - breathTimer.value / 8) * 0.3
    } else {
      breathOpacity.value = 0.9
    }
  }, 1000)
}

// 身体放松引导
let bodyRelaxInterval = null
const initBodyRelaxation = () => {
  let partIndex = 0
  if (bodyRelaxInterval) clearInterval(bodyRelaxInterval)
  
  bodyRelaxInterval = setInterval(() => {
    activeBodyPart.value = bodyParts.value[partIndex]
    partIndex = (partIndex + 1) % bodyParts.value.length
  }, 3000) // 每个部位3秒
}

// 下一步
const nextStep = () => {
  if (currentStep.value < 4) {
    // 清理当前步骤的动画
    if (currentStep.value === 2 && breathInterval) {
      clearInterval(breathInterval)
    } else if (currentStep.value === 3 && bodyRelaxInterval) {
      clearInterval(bodyRelaxInterval)
    }
    
    currentStep.value++
    
    // 启动新步骤的动画
    if (currentStep.value === 2) {
      breathCycle.value = 0
      initBreathAnimation()
    } else if (currentStep.value === 3) {
      initBodyRelaxation()
    }
  }
}

// 上一步
const prevStep = () => {
  if (currentStep.value > 1) {
    // 清理当前步骤的动画
    if (currentStep.value === 2 && breathInterval) {
      clearInterval(breathInterval)
    } else if (currentStep.value === 3 && bodyRelaxInterval) {
      clearInterval(bodyRelaxInterval)
    }
    
    currentStep.value--
    
    // 如果回到步骤2，重新启动呼吸动画
    if (currentStep.value === 2) {
      initBreathAnimation()
    } else if (currentStep.value === 3) {
      initBodyRelaxation()
    }
  }
}

// 开始评估
const startAssessment = () => {
  if (!consentGiven.value) return
  
  // 清理所有计时器
  if (breathInterval) clearInterval(breathInterval)
  if (bodyRelaxInterval) clearInterval(bodyRelaxInterval)
  
  // 停止音频播放
  if (audioElement.value) {
    audioElement.value.pause()
  }
  
  // 跳转到测试页面
  router.push('/test')
}

// 组件挂载
onMounted(() => {
  // 设置音频事件监听
  setupAudioListeners()
  
  // 初始化音频源
  if (audioElement.value) {
    audioElement.value.src = selectedAudio.value.file
    audioElement.value.volume = audioVolume.value / 100
  }
})

// 组件卸载
onUnmounted(() => {
  if (breathInterval) clearInterval(breathInterval)
  if (bodyRelaxInterval) clearInterval(bodyRelaxInterval)
  
  if (audioElement.value) {
    audioElement.value.pause()
    audioElement.value = null
  }
})

// 监听音量变化
watch(audioVolume, (newVolume) => {
  if (audioElement.value) {
    audioElement.value.volume = newVolume / 100
  }
})
</script>

<style scoped>
.relax-guide-watercolor {
  position: fixed;
  inset: 0;
  display: flex;
  background: linear-gradient(135deg, #F9FCFB 0%, #E8F4F3 100%);
  color: #2C3E50;
  overflow: hidden;
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* 水墨风背景 */
.watercolor-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  overflow: hidden;
}

.watercolor-layer {
  position: absolute;
  inset: 0;
  opacity: 0.8;
  animation: watercolorFloat 40s ease-in-out infinite;
}

.layer-1 {
  animation-delay: 0s;
}

.layer-2 {
  animation-delay: -20s;
}

.layer-3 {
  animation-delay: -10s;
}

.ink-drip {
  position: absolute;
  background: radial-gradient(circle, rgba(78, 205, 196, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  opacity: 0.6;
  filter: blur(20px);
}

.ink-1 {
  width: 400px;
  height: 400px;
  top: -100px;
  left: -100px;
  animation: inkFlow 25s linear infinite;
}

.ink-2 {
  width: 300px;
  height: 300px;
  bottom: -50px;
  right: 10%;
  animation: inkFlow 30s linear infinite reverse;
  background: radial-gradient(circle, rgba(42, 111, 121, 0.08) 0%, transparent 70%);
}

.ink-3 {
  width: 200px;
  height: 200px;
  top: 30%;
  right: 20%;
  animation: inkFlow 20s linear infinite;
  background: radial-gradient(circle, rgba(127, 211, 33, 0.05) 0%, transparent 70%);
}

@keyframes watercolorFloat {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(2%, 1%) scale(1.05);
  }
  66% {
    transform: translate(-1%, 2%) scale(0.95);
  }
}

@keyframes inkFlow {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  50% {
    transform: translate(20px, 30px) scale(1.2);
  }
}

/* 主容器 */
.main-container {
  display: flex;
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
  padding: 2rem;
  gap: 2rem;
  z-index: 10;
  position: relative;
}

/* 左侧导航面板 */
.nav-panel {
  flex: 0 0 320px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 2rem;
  border: 1px solid rgba(78, 205, 196, 0.2);
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 40px rgba(78, 205, 196, 0.1);
}

.brand-section {
  margin-bottom: 2rem;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid rgba(78, 205, 196, 0.2);
}

.logo-icon {
  font-size: 3rem;
  width: 70px;
  height: 70px;
  background: linear-gradient(135deg, #4ECDC4, #2A6F79);
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 8px 25px rgba(78, 205, 196, 0.3);
}

.logo-text h1 {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #2A6F79, #4ECDC4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  color: #546E7A;
  font-size: 0.9rem;
  font-weight: 400;
}

/* 时间线进度条 */
.progress-timeline {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin: 1rem 0;
}

.timeline-step {
  display: flex;
  align-items: center;
  gap: 1rem;
  position: relative;
  padding: 1rem 0;
  opacity: 0.5;
  transition: all 0.3s ease;
}

.timeline-step.active {
  opacity: 1;
}

.timeline-step.completed {
  opacity: 0.8;
}

.step-marker {
  width: 36px;
  height: 36px;
  min-width: 36px;
  background: #E8F4F3;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1rem;
  color: #2A6F79;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  box-shadow: 0 4px 12px rgba(42, 111, 121, 0.1);
}

.timeline-step.active .step-marker {
  background: #4ECDC4;
  color: white;
  border-color: white;
  box-shadow: 0 4px 12px rgba(78, 205, 196, 0.3);
}

.timeline-step.completed .step-marker {
  background: #4ECDC4;
  color: white;
}

.step-info h3 {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
  color: #2C3E50;
}

.step-info p {
  font-size: 0.85rem;
  color: #546E7A;
  line-height: 1.4;
}

.timeline-connector {
  position: absolute;
  left: 18px;
  top: 54px;
  bottom: -1.5rem;
  width: 2px;
  background: linear-gradient(to bottom, #E8F4F3, transparent);
  z-index: -1;
}

.timeline-step:last-child .timeline-connector {
  display: none;
}

.timeline-step.completed .timeline-connector {
  background: linear-gradient(to bottom, #4ECDC4, #E8F4F3);
}

/* 时间估计卡片 */
.time-estimate-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  background: linear-gradient(135deg, rgba(248, 252, 251, 0.8), rgba(232, 244, 243, 0.8));
  border-radius: 16px;
  border: 1px solid rgba(78, 205, 196, 0.2);
  margin-top: auto;
}

.time-icon {
  font-size: 2rem;
  color: #2A6F79;
}

.time-label {
  font-size: 0.9rem;
  color: #546E7A;
  margin-bottom: 0.25rem;
}

.time-value {
  font-size: 1.3rem;
  font-weight: 700;
  color: #2A6F79;
}

/* 右侧内容面板 */
.content-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  border: 1px solid rgba(78, 205, 196, 0.2);
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(78, 205, 196, 0.1);
}

/* 步骤内容区域 */
.step-content-area {
  flex: 1;
  padding: 2.5rem 3rem;
  overflow-y: auto;
  max-height: calc(100vh - 180px);
}

/* 步骤头部（步骤1、3、4使用） */
.step-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.step-icon {
  font-size: 3.5rem;
  filter: drop-shadow(0 4px 12px rgba(78, 205, 196, 0.3));
  animation: gentleFloat 3s ease-in-out infinite;
}

@keyframes gentleFloat {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}

.step-title h2 {
  font-size: 2.2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: #2A6F79;
}

.step-description {
  font-size: 1.1rem;
  color: #546E7A;
  line-height: 1.6;
}

/* 步骤1: 环境准备 */
.env-check-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin-bottom: 2.5rem;
  max-width: 900px;
}

.env-card {
  background: linear-gradient(135deg, rgba(248, 252, 251, 0.9), rgba(232, 244, 243, 0.9));
  border: 2px solid rgba(78, 205, 196, 0.1);
  border-radius: 18px;
  padding: 2rem;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.env-card:hover {
  transform: translateY(-4px);
  border-color: rgba(78, 205, 196, 0.3);
  box-shadow: 0 12px 30px rgba(78, 205, 196, 0.15);
}

.env-card.checked {
  background: linear-gradient(135deg, rgba(232, 248, 245, 0.95), rgba(210, 240, 237, 0.95));
  border-color: #4ECDC4;
  box-shadow: 0 12px 30px rgba(78, 205, 196, 0.2);
}

.env-icon-wrapper {
  width: 70px;
  height: 70px;
  background: linear-gradient(135deg, #E8F4F3, #D0F0ED);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.5rem;
}

.env-icon {
  font-size: 2.5rem;
}

.env-title {
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #2A6F79;
}

.env-desc {
  font-size: 0.95rem;
  color: #546E7A;
  line-height: 1.5;
  flex: 1;
}

.check-status {
  font-size: 0.9rem;
  font-weight: 600;
  padding: 0.6rem 1.5rem;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.8);
  color: #546E7A;
  border: 2px solid #E8F4F3;
  transition: all 0.3s ease;
}

.env-card.checked .check-status {
  background: #4ECDC4;
  color: white;
  border-color: #4ECDC4;
}

.tech-notice-card {
  background: linear-gradient(135deg, rgba(248, 252, 251, 0.95), rgba(232, 244, 243, 0.95));
  border-radius: 18px;
  border: 1px solid rgba(78, 205, 196, 0.3);
  padding: 1.5rem 2rem;
  max-width: 900px;
  margin: 0 auto;
}

.notice-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.notice-icon {
  font-size: 2rem;
  color: #2A6F79;
}

.tech-notice-card h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2A6F79;
}

.tech-notice-card p {
  color: #546E7A;
  line-height: 1.6;
  margin-bottom: 0.5rem;
}

.tech-notice-card p strong {
  color: #2A6F79;
}

.notice-tip {
  font-size: 0.9rem;
  color: #78909C;
  font-style: italic;
  margin-top: 0.5rem;
}

/* 步骤2: 呼吸调整 - 新的两行布局 */

/* 第一行：深呼吸描述和呼吸技巧在同一行 */
.breath-top-row {
  display: flex;
  justify-content: space-between;
  align-items: stretch; /* 确保两个组件高度一致 */
  gap: 2rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

/* 左侧：深呼吸描述卡片 */
.breath-description-card {
  flex: 1;
  min-width: 300px;
  padding: 1.5rem 2rem;
  background: linear-gradient(135deg, rgba(248, 252, 251, 0.9), rgba(232, 244, 243, 0.9));
  border-radius: 18px;
  border: 1px solid rgba(78, 205, 196, 0.2);
  display: flex;
  align-items: center;
  box-shadow: 0 4px 20px rgba(78, 205, 196, 0.1);
  transition: all 0.3s ease;
  min-height: 140px; /* 设置最小高度确保与右侧对齐 */
}

.breath-description-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(78, 205, 196, 0.15);
}

.step-header-content {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  width: 100%;
}

/* 右侧：呼吸技巧卡片 */
.breath-tips-card {
  flex: 0 0 320px;
  padding: 1.5rem 2rem;
  background: linear-gradient(135deg, rgba(248, 252, 251, 0.95), rgba(232, 244, 243, 0.95));
  border-radius: 18px;
  border: 1px solid rgba(78, 205, 196, 0.3);
  box-shadow: 0 4px 20px rgba(78, 205, 196, 0.1);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 140px; /* 设置最小高度确保与左侧对齐 */
}

.breath-tips-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(78, 205, 196, 0.15);
}

.tips-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.tips-icon {
  font-size: 1.5rem;
  color: #2A6F79;
}

.breath-tips-card h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: #2A6F79;
  margin: 0;
}

.tips-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.tips-list li {
  color: #546E7A;
  padding-left: 1.5rem;
  position: relative;
  line-height: 1.5;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.tips-list li:hover {
  color: #2A6F79;
  transform: translateX(4px);
}

.tips-list li:before {
  content: "•";
  color: #4ECDC4;
  position: absolute;
  left: 0;
  font-size: 1.5rem;
  line-height: 1;
  font-weight: bold;
}

/* 第二行：呼吸动画 */
.breath-guide-section {
  padding: 2rem;
  background: linear-gradient(135deg, rgba(248, 252, 251, 0.9), rgba(232, 244, 243, 0.9));
  border-radius: 24px;
  border: 1px solid rgba(78, 205, 196, 0.2);
  box-shadow: 0 4px 20px rgba(78, 205, 196, 0.1);
  margin-top: 1rem;
}

.breath-visualizer {
  display: flex;
  align-items: center;
  gap: 3rem;
  width: 100%;
}

.breath-animation-container {
  position: relative;
  width: 280px;
  height: 280px;
  flex-shrink: 0;
}

.breath-circle {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: linear-gradient(135deg, #4ECDC4, #2A6F79);
  transition: all 1s ease-in-out;
  box-shadow: 0 0 50px rgba(78, 205, 196, 0.3);
}

.breath-info-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 2;
}

.breath-phase {
  font-size: 1.6rem;
  font-weight: 600;
  color: white;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.breath-timer {
  font-size: 3.5rem;
  font-weight: 700;
  color: white;
  font-family: 'Arial', sans-serif;
  text-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  margin-bottom: 0.5rem;
}

.breath-cycle {
  font-size: 1rem;
  color: white;
  background: rgba(255, 255, 255, 0.2);
  padding: 0.5rem 1.25rem;
  border-radius: 20px;
  backdrop-filter: blur(10px);
}

.breath-instructions {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.instruction-card {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 1.25rem;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 16px;
  border: 1px solid rgba(78, 205, 196, 0.1);
  opacity: 0.6;
  transition: all 0.3s ease;
}

.instruction-card.active {
  opacity: 1;
  background: rgba(255, 255, 255, 0.95);
  border-color: rgba(78, 205, 196, 0.3);
  transform: translateX(8px);
  box-shadow: 0 8px 20px rgba(78, 205, 196, 0.15);
}

.instruction-number {
  width: 46px;
  height: 46px;
  min-width: 46px;
  background: linear-gradient(135deg, #E8F4F3, #D0F0ED);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
  font-weight: 700;
  color: #2A6F79;
}

.instruction-card.active .instruction-number {
  background: linear-gradient(135deg, #4ECDC4, #2A6F79);
  color: white;
  box-shadow: 0 4px 12px rgba(78, 205, 196, 0.3);
}

.instruction-content h4 {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
  color: #2A6F79;
}

.instruction-content p {
  font-size: 0.95rem;
  color: #546E7A;
  line-height: 1.5;
}

/* 步骤3: 身心放松 */
.relaxation-section {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* 新增：放松部分顶部容器 */
.relaxation-top {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  padding: 2rem;
  background: linear-gradient(135deg, rgba(248, 252, 251, 0.9), rgba(232, 244, 243, 0.9));
  border-radius: 24px;
  border: 1px solid rgba(78, 205, 196, 0.2);
}

.body-visual-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
}

.body-silhouette {
  position: relative;
  width: 300px;
  height: 450px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 150px 150px 20px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem 0;
  border: 2px solid rgba(78, 205, 196, 0.1);
  box-shadow: 0 8px 30px rgba(78, 205, 196, 0.1);
}

.body-part {
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(42, 111, 121, 0.3);
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.3s ease;
  border-radius: 8px;
  border: 2px solid transparent;
  background: rgba(232, 244, 243, 0.5);
  width: 80px;
  height: 30px;
  left: 50%;
  transform: translateX(-50%);
}

.body-part.active {
  color: white;
  background: linear-gradient(135deg, #4ECDC4, #2A6F79);
  border-color: white;
  box-shadow: 0 4px 20px rgba(78, 205, 196, 0.3);
  z-index: 2;
  width: 100px;
  height: 40px;
}

.body-part.completed {
  color: #4ECDC4;
  background: rgba(78, 205, 196, 0.2);
  border-color: rgba(78, 205, 196, 0.3);
}

.focus-icon {
  font-size: 2.5rem;
  animation: gentlePulse 2s ease-in-out infinite;
}

@keyframes gentlePulse {
  0%, 100% {
    opacity: 0.8;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.1);
  }
}

.focus-info {
  display: flex;
  flex-direction: column;
  align-items: center; /* 子元素水平居中 */
  justify-content: center; /* 子元素垂直居中 */
  width: 100%; /* 确保宽度充满容器 */
}

.focus-label {
  font-size: 1.1rem; /* 从0.95rem增大到1.1rem */
  color: #546E7A;
  margin-bottom: 0.5rem; /* 增大间距 */
  font-weight: 500;
  text-align: center; /* 确保文字居中 */
  width: 100%; /* 确保宽度充满容器 */
}

.focus-part {
  font-size: 2rem; /* 从1.6rem增大到2rem */
  font-weight: 700;
  color: #2A6F79;
  margin-bottom: 0.75rem; /* 增大间距 */
  text-align: center; /* 确保文字居中 */
  width: 100%; /* 确保宽度充满容器 */
}

.focus-instruction {
  font-size: 1.2rem; /* 从0.95rem增大到1.2rem */
  color: #546E7A;
  line-height: 1.6; /* 增大行高 */
  text-align: center; /* 确保文字居中 */
  width: 100%; /* 确保宽度充满容器 */
  max-width: 300px; /* 限制最大宽度，避免过宽 */
  margin: 0 auto; /* 水平居中 */
}


.current-focus {
  display: flex;
  align-items: center;
  justify-content: center; /* 添加水平居中 */
  gap: 1.5rem;
  padding: 1.5rem 2rem;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 18px;
  border: 1px solid rgba(78, 205, 196, 0.2);
  min-width: auto;
  text-align: center; /* 添加文字居中 */
  width: 100%; /* 确保宽度充满容器 */
}

/* 修改：放松主体区域 */
.relaxation-main {
  display: flex;
  gap: 3rem;
  padding: 2rem;
  background: linear-gradient(135deg, rgba(248, 252, 251, 0.9), rgba(232, 244, 243, 0.9));
  border-radius: 24px;
  border: 1px solid rgba(78, 205, 196, 0.2);
}

.relaxation-steps {
  flex: 1;
  min-width: 300px;
}

.steps-icon {
  font-size: 1.5rem;
  color: #2A6F79;
}

.relaxation-steps h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: #2A6F79;
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  max-height: 380px;
  overflow-y: auto;
  padding-right: 1rem;
}

.steps-list::-webkit-scrollbar {
  width: 6px;
}

.steps-list::-webkit-scrollbar-track {
  background: rgba(232, 244, 243, 0.5);
  border-radius: 3px;
}

.steps-list::-webkit-scrollbar-thumb {
  background: rgba(78, 205, 196, 0.5);
  border-radius: 3px;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 12px;
  border: 1px solid rgba(78, 205, 196, 0.1);
  opacity: 0.6;
  transition: all 0.3s ease;
}

.step-item.current {
  opacity: 1;
  background: rgba(255, 255, 255, 0.95);
  border-color: rgba(78, 205, 196, 0.3);
  transform: translateX(4px);
  box-shadow: 0 4px 15px rgba(78, 205, 196, 0.15);
}

.step-item.completed {
  opacity: 0.8;
}

.step-index {
  width: 28px;
  height: 28px;
  min-width: 28px;
  background: rgba(232, 244, 243, 0.8);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.9rem;
  color: #546E7A;
}

.step-item.current .step-index {
  background: linear-gradient(135deg, #4ECDC4, #2A6F79);
  color: white;
  box-shadow: 0 4px 12px rgba(78, 205, 196, 0.3);
}

.step-item.completed .step-index {
  background: rgba(78, 205, 196, 0.2);
  color: #2A6F79;
}

.step-name {
  flex: 1;
  font-size: 1rem;
  font-weight: 500;
  color: #2C3E50;
}

.step-duration {
  font-size: 0.85rem;
  color: #78909C;
  font-style: italic;
}

.step-check {
  color: #4ECDC4;
  font-size: 1.2rem;
  font-weight: bold;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.step-item.completed .step-check {
  opacity: 1;
}

/* 步骤3音频选项 */
.audio-options {
  background: rgba(255, 255, 255, 0.6);
  border-radius: 18px;
  border: 1px solid rgba(78, 205, 196, 0.2);
  padding: 1.5rem 2rem;
  max-width: none;
  margin: 0;
}

.audio-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.audio-icon {
  font-size: 1.5rem;
  color: #2A6F79;
}

.audio-options h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: #2A6F79;
}

.audio-desc {
  color: #546E7A;
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

/* 新增：音效选择卡片样式 */
.audio-selection {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.audio-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1.2rem;
  background: rgba(255, 255, 255, 0.7);
  border: 2px solid rgba(78, 205, 196, 0.1);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  gap: 0.8rem;
}

.audio-card:hover {
  transform: translateY(-4px);
  border-color: rgba(78, 205, 196, 0.3);
  box-shadow: 0 8px 20px rgba(78, 205, 196, 0.1);
  background: rgba(255, 255, 255, 0.9);
}

.audio-card.selected {
  background: linear-gradient(135deg, rgba(232, 248, 245, 0.95), rgba(210, 240, 237, 0.95));
  border-color: #4ECDC4;
  box-shadow: 0 8px 20px rgba(78, 205, 196, 0.15);
}

.audio-card .audio-icon {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.audio-info h4 {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
  color: #2A6F79;
}

.audio-info p {
  font-size: 0.85rem;
  color: #546E7A;
  line-height: 1.4;
}

.audio-controls {
  display: flex;
  align-items: center;
  gap: 2rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}

.audio-btn {
  padding: 0.8rem 2rem;
  background: linear-gradient(135deg, #E8F4F3, #D0F0ED);
  border: 2px solid rgba(78, 205, 196, 0.3);
  border-radius: 12px;
  color: #2A6F79;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.audio-btn:hover {
  background: linear-gradient(135deg, #D0F0ED, #B8E4E0);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(78, 205, 196, 0.2);
}

.volume-control {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
  min-width: 250px;
}

.volume-slider {
  flex: 1;
  height: 6px;
  -webkit-appearance: none;
  background: rgba(232, 244, 243, 0.8);
  border-radius: 3px;
  outline: none;
}

.volume-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 20px;
  height: 20px;
  background: #4ECDC4;
  border-radius: 50%;
  cursor: pointer;
  border: 3px solid white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 新增：音频进度条样式 */
.audio-progress-container {
  margin-top: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.audio-progress-bar {
  width: 100%;
  height: 6px;
  -webkit-appearance: none;
  appearance: none;
  background: rgba(232, 244, 243, 0.8);
  border-radius: 3px;
  outline: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.audio-progress-bar:hover {
  height: 8px;
  background: rgba(78, 205, 196, 0.3);
}

.audio-progress-bar::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  background: #4ECDC4;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 2px 6px rgba(78, 205, 196, 0.3);
}

.audio-progress-bar::-moz-range-thumb {
  width: 16px;
  height: 16px;
  background: #4ECDC4;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 2px 6px rgba(78, 205, 196, 0.3);
}

.audio-time-display {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
  color: #78909C;
  padding: 0 0.25rem;
}

.current-time {
  font-weight: 500;
  color: #4ECDC4;
}

.duration {
  font-size: 0.8rem;
}

/* 步骤4: 准备就绪 */
.readiness-overview {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin-bottom: 2.5rem;
  max-width: 900px;
  margin-left: auto;
  margin-right: auto;
}

.readiness-card {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, rgba(248, 252, 251, 0.9), rgba(232, 244, 243, 0.9));
  border-radius: 18px;
  border: 1px solid rgba(78, 205, 196, 0.2);
  transition: all 0.3s ease;
}

.readiness-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(78, 205, 196, 0.15);
  border-color: rgba(78, 205, 196, 0.4);
}

.readiness-icon {
  font-size: 2rem;
  color: #4ECDC4;
}

.readiness-content h3 {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
  color: #2A6F79;
}

.readiness-content p {
  font-size: 0.9rem;
  color: #546E7A;
  line-height: 1.5;
}

.assessment-instructions {
  max-width: 900px;
  margin: 0 auto;
}

.instructions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
  margin-bottom: 2.5rem;
}

.instruction-item {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 1.25rem;
  background: linear-gradient(135deg, rgba(248, 252, 251, 0.9), rgba(232, 244, 243, 0.9));
  border-radius: 16px;
  border: 1px solid rgba(78, 205, 196, 0.1);
  transition: all 0.3s ease;
}

.instruction-item:hover {
  transform: translateY(-2px);
  border-color: rgba(78, 205, 196, 0.3);
  box-shadow: 0 8px 20px rgba(78, 205, 196, 0.1);
}

.item-icon {
  font-size: 1.8rem;
  color: #2A6F79;
}

.instruction-item h4 {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
  color: #2A6F79;
}

.instruction-item p {
  font-size: 0.9rem;
  color: #546E7A;
  line-height: 1.5;
}
.consent-section {
  background: linear-gradient(135deg, rgba(255, 253, 231, 0.9), rgba(255, 250, 204, 0.9));
  border-radius: 18px;
  border: 1px solid rgba(255, 193, 7, 0.3);
  padding: 1.5rem 2rem;
}

.consent-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.consent-icon {
  font-size: 1.5rem;
  color: #FF9800;
}

.consent-section h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: #FF9800;
}

.consent-content p {
  color: #5D4037;
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.consent-content p b {
  color: #2A6F79;
}

.consent-agreement {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.consent-agreement:hover {
  background: rgba(255, 255, 255, 0.9);
}

.consent-agreement input[type="checkbox"] {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  margin-top: 0.2rem;
  cursor: pointer;
  accent-color: #4ECDC4;
}

.consent-agreement span {
  color: #5D4037;
  line-height: 1.5;
  user-select: none;
  font-size: 0.95rem;
}

/* 导航控制区 */
.navigation-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem 3rem;
  background: rgba(255, 255, 255, 0.9);
  border-top: 1px solid rgba(78, 205, 196, 0.2);
  gap: 2rem;
  margin-top: auto;
}

.nav-left,
.nav-center,
.nav-right {
  flex: 1;
  display: flex;
  align-items: center;
}

.nav-center {
  justify-content: center;
}

.nav-right {
  justify-content: flex-end;
}

.nav-btn {
  padding: 0.9rem 2.25rem;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 160px;
  justify-content: center;
}

.nav-btn.back-btn {
  background: rgba(255, 255, 255, 0.9);
  color: #546E7A;
  border: 2px solid rgba(78, 205, 196, 0.3);
}

.nav-btn.back-btn:hover:not(:disabled) {
  background: rgba(232, 244, 243, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(78, 205, 196, 0.15);
}

.nav-btn.next-btn {
  background: linear-gradient(135deg, #4ECDC4, #2A6F79);
  color: white;
  box-shadow: 0 4px 20px rgba(78, 205, 196, 0.3);
}

.nav-btn.next-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(78, 205, 196, 0.4);
}

.nav-btn.start-btn {
  background: linear-gradient(135deg, #FF6B6B, #FF8E53);
  color: white;
  box-shadow: 0 4px 20px rgba(255, 107, 107, 0.3);
  font-size: 1.1rem;
  padding: 1rem 2.5rem;
}

.nav-btn.start-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(255, 107, 107, 0.4);
}

.nav-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

.step-progress {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(232, 244, 243, 0.7);
  padding: 0.8rem 1.5rem;
  border-radius: 20px;
  border: 1px solid rgba(78, 205, 196, 0.2);
}

.current-step {
  font-size: 1.2rem;
  font-weight: 700;
  color: #2A6F79;
}

.step-separator {
  font-size: 1.1rem;
  color: #78909C;
  margin: 0 0.25rem;
}

.total-steps {
  font-size: 1rem;
  color: #546E7A;
}

/* 响应式调整 */
@media (max-width: 1200px) {
  .main-container {
    padding: 1.5rem;
  }
  
  .nav-panel {
    flex: 0 0 280px;
  }
  
  .breath-visualizer {
    flex-direction: column;
    gap: 2rem;
  }
  
  .breath-animation-container {
    width: 250px;
    height: 250px;
  }
  
  .relaxation-main {
    flex-direction: column;
  }
  
  .relaxation-top {
    grid-template-columns: 1fr;
  }
  
  .current-focus {
    min-width: auto;
    width: 100%;
  }
  
  /* 步骤2头部布局在中等屏幕 */
  .breath-top-row {
    gap: 1.5rem;
  }
  
  .breath-tips-card {
    flex: 0 0 280px;
  }
}

@media (max-width: 992px) {
  .main-container {
    flex-direction: column;
  }
  
  .nav-panel {
    flex: none;
    width: 100%;
    margin-bottom: 1.5rem;
  }
  
  .progress-timeline {
    flex-direction: row;
    margin: 1.5rem 0;
  }
  
  .timeline-step {
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 0.5rem;
  }
  
  .timeline-connector {
    width: 100%;
    height: 2px;
    left: 50%;
    top: 18px;
    bottom: auto;
  }
  
  .env-check-grid {
    grid-template-columns: 1fr;
  }
  
  .instructions-grid {
    grid-template-columns: 1fr;
  }
  
  .readiness-overview {
    grid-template-columns: 1fr;
  }
  
  .audio-selection {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .navigation-bar {
    flex-direction: column;
    gap: 1rem;
  }
  
  .nav-left,
  .nav-center,
  .nav-right {
    width: 100%;
    justify-content: center;
  }
  
  /* 步骤2头部布局在平板端 */
  .breath-top-row {
    flex-direction: column;
  }
  
  .breath-description-card,
  .breath-tips-card {
    width: 100%;
    flex: none;
  }
  
  .breath-description-card {
    min-height: auto;
  }
  
  .breath-tips-card {
    min-height: auto;
  }
  
  .breath-visualizer {
    flex-direction: column;
  }
  
  .breath-animation-container {
    width: 220px;
    height: 220px;
  }
}

@media (max-width: 768px) {
  .step-content-area {
    padding: 1.5rem;
  }
  
  .step-header h2 {
    font-size: 1.8rem;
  }
  
  .step-icon {
    font-size: 2.5rem;
  }
  
  .breath-timer {
    font-size: 2.5rem;
  }
  
  .nav-btn {
    min-width: 140px;
    padding: 0.8rem 1.5rem;
  }
  
  /* 在768px以下，音频选择卡片改为单列 */
  .audio-selection {
    grid-template-columns: 1fr;
  }
  
  .breath-guide-section {
    padding: 1.5rem;
  }
  
  .breath-animation-container {
    width: 180px;
    height: 180px;
  }
  
  .relaxation-main {
    padding: 1.5rem;
  }
  
  .body-silhouette {
    width: 250px;
    height: 400px;
  }
  
   .current-focus {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
    padding: 1.25rem; /* 调整内边距 */
  }
  
  .focus-info {
    align-items: center;
    justify-content: center;
  }
  
  .focus-label {
    font-size: 1rem; /* 在移动端保持合适大小 */
  }
  
  .focus-part {
    font-size: 1.8rem; /* 在移动端保持合适大小 */
  }
  
  .focus-instruction {
    font-size: 1.1rem; /* 在移动端保持合适大小 */
  }

  .steps-list {
    max-height: 300px;
  }
  
  /* 步骤4的响应式调整 */
  .readiness-overview {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .instructions-grid {
    grid-template-columns: 1fr;
  }
  
  .instruction-item {
    padding: 1rem;
  }
  
  .item-icon {
    font-size: 1.5rem;
  }
  
  .instruction-item h4 {
    font-size: 1rem;
  }
  
  .consent-section {
    padding: 1.25rem 1.5rem;
  }
  
  .consent-agreement {
    padding: 0.8rem;
  }
  
  .consent-agreement span {
    font-size: 0.9rem;
  }
  
  /* 步骤2头部布局在手机端 */
  .breath-description-card {
    padding: 1.25rem 1.5rem;
    min-height: 120px;
  }
  
  .breath-tips-card {
    padding: 1.25rem 1.5rem;
    min-height: 120px;
  }
  
  .step-header-content {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
  
  .step-icon {
    font-size: 2.5rem;
  }
  
  .step-title h2 {
    font-size: 1.8rem;
  }
  
  .step-description {
    font-size: 1rem;
  }
  
  .tips-header {
    justify-content: center;
  }
  
  .instruction-card {
    padding: 1rem;
  }
  
  .instruction-number {
    width: 40px;
    height: 40px;
    min-width: 40px;
    font-size: 1.1rem;
  }
  
  .instruction-content h4 {
    font-size: 1.1rem;
  }
  
  .instruction-content p {
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .main-container {
    padding: 1rem;
  }
  
  .nav-panel {
    padding: 1.5rem;
  }
  
  .step-content-area {
    padding: 1.25rem;
  }
  
  .step-header {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
  
  .step-title h2 {
    font-size: 1.6rem;
  }
  
  .step-description {
    font-size: 1rem;
  }
  
  .env-card {
    padding: 1.5rem 1rem;
  }
  
  .env-icon-wrapper {
    width: 60px;
    height: 60px;
  }
  
  .env-icon {
    font-size: 2rem;
  }
  
  .env-title {
    font-size: 1.1rem;
  }
  
  .env-desc {
    font-size: 0.9rem;
  }
  
  .check-status {
    padding: 0.5rem 1rem;
    font-size: 0.85rem;
  }
  
  .breath-animation-container {
    width: 150px;
    height: 150px;
  }
  
  .breath-phase {
    font-size: 1.1rem;
  }
  
  .breath-timer {
    font-size: 2rem;
  }
  
  .breath-cycle {
    font-size: 0.9rem;
  }
  
  .instruction-card {
    padding: 0.8rem;
  }
  
  .instruction-number {
    width: 35px;
    height: 35px;
    min-width: 35px;
    font-size: 1rem;
  }
  
  .instruction-content h4 {
    font-size: 1rem;
  }
  
  .instruction-content p {
    font-size: 0.85rem;
  }
  
  .body-silhouette {
    width: 200px;
    height: 350px;
  }
  
  .body-part {
    width: 70px;
    height: 25px;
    font-size: 0.75rem;
  }
  
  .body-part.active {
    width: 85px;
    height: 35px;
  }
  
  .current-focus {
    padding: 1.25rem;
  }
  
  .focus-icon {
    font-size: 1.8rem;
  }
  
  .focus-part {
    font-size: 1.2rem;
  }
  
  .step-item {
    padding: 0.8rem 1rem;
  }
  
  .step-index {
    width: 24px;
    height: 24px;
    min-width: 24px;
    font-size: 0.8rem;
  }
  
  .step-name {
    font-size: 0.9rem;
  }
  
  .step-duration {
    font-size: 0.8rem;
  }
  
  .audio-card {
    padding: 1rem 0.8rem;
  }
  
  .audio-card .audio-icon {
    font-size: 2rem;
  }
  
  .audio-info h4 {
    font-size: 1rem;
  }
  
  .audio-info p {
    font-size: 0.8rem;
  }
  
  .audio-btn {
    width: 100%;
    justify-content: center;
    padding: 0.7rem 1.5rem;
  }
  
  .nav-btn {
    min-width: 120px;
    padding: 0.7rem 1.25rem;
  }
  
  .nav-btn.start-btn {
    font-size: 1rem;
    padding: 0.8rem 2rem;
  }
  
  .step-progress {
    padding: 0.6rem 1.25rem;
  }
  
  .current-step {
    font-size: 1.1rem;
  }
  
  /* 步骤2头部布局在小手机端 */
  .breath-top-row {
    gap: 1.5rem;
  }
  
  .breath-description-card,
  .breath-tips-card {
    min-height: auto;
  }
  
  .breath-tips-card {
    padding: 1.25rem;
  }
  
  .tips-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 0.5rem;
  }
  
  .tips-list {
    gap: 0.3rem;
  }
  
  .tips-list li {
    font-size: 0.9rem;
    padding-left: 1.25rem;
  }
}
</style>