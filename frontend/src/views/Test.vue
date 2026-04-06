<template>
  <div class="professional-test-container">
    <!-- 水墨背景层 -->
    <div class="ink-background">
      <div class="ink-layer ink-layer-1"></div>
      <div class="ink-layer ink-layer-2"></div>
      <div class="ink-layer ink-layer-3"></div>
    </div>

    <!-- 主测试界面 -->
    <div class="test-main-interface">
      <!-- 顶部导航栏 -->
      <header class="test-header">
        <div class="header-left">
          <h1 class="app-title">心镜·守望</h1>
          <p class="app-subtitle">学生心理健康评估系统</p>
        </div>
        
        <div class="header-center">
          <div class="test-progress">
            <div class="progress-indicator">
              <span class="progress-label">测试进度</span>
              <div class="progress-bar">
                <div 
                  class="progress-fill" 
                  :style="{ width: `${progressPercentage}%` }"
                ></div>
              </div>
              <span class="progress-value">{{ currentQuestion + 1 }}/{{ questions.length }}</span>
            </div>
          </div>
        </div>
        
        <div class="header-right">
          <div class="data-status">
            <div class="status-item" :class="{ active: isRecording }">
              <span class="status-dot"></span>
              <span>语音</span>
            </div>
            <div class="status-item" :class="{ active: isCameraActive }">
              <span class="status-dot"></span>
              <span>面部</span>
            </div>
            <div class="status-item" :class="{ active: isHRMonitoring }">
              <span class="status-dot"></span>
              <span>生理</span>
            </div>
          </div>
          
          <button class="header-control" @click="pauseTest">
            <span class="control-icon">⏸️</span>
            <span>暂停</span>
          </button>
        </div>
      </header>

      <!-- 主内容区 -->
      <main class="test-content-area">
        <!-- 左侧：问题回答区 -->
        <section class="question-section">
          <div class="question-card">
            <div class="question-header">
              <div class="question-meta">
                <span class="question-number">问题 {{ currentQuestion + 1 }}</span>
                <span class="question-type">{{ currentQuestionData.category }}</span>
              </div>
              
              <div class="question-timer">
                <span class="timer-icon">⏱️</span>
                <span class="timer-text">{{ formatTime(elapsedTime) }}</span>
              </div>
            </div>

            <div class="question-body">
              <h2 class="question-text">{{ currentQuestionData.text }}</h2>
              
              <div class="question-guidance">
                <div class="guidance-item">
                  <!-- <span class="guidance-icon">💡</span> -->
                  <span class="guidance-text">请分享您真实的感受和经历</span>
                </div>
                <div class="guidance-item">
                  <!-- <span class="guidance-icon">🗣️</span> -->
                  <span class="guidance-text">自然地表达，就像与朋友聊天一样</span>
                </div>
                <div class="guidance-item">
                  <!-- <span class="guidance-icon">⏱️</span> -->
                  <span class="guidance-text">建议时长 30-60 秒</span>
                </div>
              </div>
            </div>

            <!-- 语音控制 -->
            <div class="voice-control-section">
              <button 
                class="record-btn" 
                @click="toggleRecording"
                :class="{ 
                  recording: isRecording, 
                  answered: currentQuestionData.answered 
                }"
                :disabled="currentQuestionData.answered"
              >
                <div class="btn-visual">
                  <div class="btn-circle" :class="{ pulse: isRecording }">
                    <span class="btn-icon">
                      {{ getRecordButtonIcon() }}
                    </span>
                  </div>
                </div>
                
                <div class="btn-info">
                  <h3 class="btn-title">{{ getRecordButtonTitle() }}</h3>
                  <p class="btn-subtitle">{{ getRecordButtonSubtitle() }}</p>
                </div>
              </button>

              <!-- 音频波形 -->
              <div v-if="isRecording" class="audio-wave-container">
                <div class="wave-display">
                  <div 
                    v-for="(amplitude, index) in audioWave" 
                    :key="index"
                    class="wave-bar"
                    :style="{ height: `${amplitude}%` }"
                  ></div>
                </div>
                <div class="wave-info">
                  <span class="info-item">音量: {{ audioLevel }}%</span>
                  <span class="info-item">时长: {{ formatTime(recordingDuration) }}</span>
                </div>
              </div>
            </div>

            <!-- 问题导航 -->
            <div class="questions-navigation">
              <div 
                v-for="(question, index) in questions" 
                :key="index"
                class="question-nav-item"
                :class="{ 
                  current: currentQuestion === index,
                  answered: question.answered
                }"
                @click="navigateToQuestion(index+1)"
              >
                <div class="nav-indicator">
                  <span v-if="question.answered">✓</span>
                  <span v-else>{{ index + 1 }}</span>
                </div>
                <div class="nav-content">
                  <p class="nav-text">{{ question.text }}</p>
                  <div class="nav-meta">
                    <span v-if="question.answered" class="meta-answered">
                      已回答 ({{ question.duration }}s)
                    </span>
                    <span v-else-if="currentQuestion === index" class="meta-current">
                      当前
                    </span>
                    <span v-else class="meta-pending">等待回答</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 中间：摄像头视图 -->
        <section class="camera-section">
          <div class="camera-card">
            <div class="card-header">
              <h3>面部数据采集</h3>
              <div class="camera-status" :class="{ active: isCameraActive }">
                <span class="status-dot"></span>
                <span>{{ cameraStatusText }}</span>
              </div>
            </div>

            <!-- 摄像头视图 -->
            <div class="camera-view-container" :class="{ active: isCameraActive }">
              <div v-if="!isCameraActive" class="camera-off-state">
                <div class="off-content">
                  <div class="off-icon">📷</div>
                  <h4>摄像头准备中</h4>
                  <p>开启摄像头以进行面部数据采集</p>
                  <button 
                    class="camera-toggle-btn" 
                    @click="toggleCamera"
                    :disabled="cameraLoading"
                  >
                    <span v-if="cameraLoading">开启中...</span>
                    <span v-else>开启摄像头</span>
                  </button>
                </div>
              </div>

              <div v-else class="camera-live-view">
                <video 
                  ref="videoElement" 
                  autoplay 
                  playsinline 
                  class="camera-video"
                ></video>
                
                <!-- 面部识别框 -->
                <div class="face-detection-overlay">
                  <div class="face-guide">
                    <div class="guide-frame">
                      <div class="guide-corner top-left"></div>
                      <div class="guide-corner top-right"></div>
                      <div class="guide-corner bottom-left"></div>
                      <div class="guide-corner bottom-right"></div>
                    </div>
                    <p class="guide-text">请保持面部在框内</p>
                  </div>
                  
                  <!-- 实时分析点 -->
                  <div class="analysis-points">
                    <div 
                      v-for="point in analysisPoints" 
                      :key="point.id"
                      class="analysis-point"
                      :style="{ left: `${point.x}%`, top: `${point.y}%` }"
                    ></div>
                  </div>
                </div>
                
                <!-- 采集状态 -->
                <div class="capture-status">
                  <span class="status-indicator pulse"></span>
                  <span>实时采集中</span>
                </div>
              </div>
            </div>

            <!-- 数据采集信息 -->
            <div class="capture-info">
              <div class="info-grid">
                <div class="info-item">
                  <!-- <span class="info-icon">⏱️</span> -->
                  <div class="info-content">
                    <span class="info-label">采集时长</span>
                    <span class="info-value">{{ captureDuration }}秒</span>
                  </div>
                </div>
                <div class="info-item">
                  <!-- <span class="info-icon">📈</span> -->
                  <div class="info-content">
                    <span class="info-label">数据质量</span>
                    <span class="info-value" :class="{ good: dataQuality > 80 }">
                      {{ dataQuality }}%
                    </span>
                  </div>
                </div>
                <div class="info-item">
                  <!-- <span class="info-icon">🔍</span> -->
                  <div class="info-content">
                    <span class="info-label">面部检测</span>
                    <span class="info-value" :class="{ active: isFaceDetected }">
                      {{ isFaceDetected ? '正常' : '检测中' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 右侧：生理数据 -->
        <section class="physiological-section">
          <div class="physiological-card">
            <div class="card-header">
              <h3>生理数据监测</h3>
              <div class="physio-status" :class="{ active: isHRMonitoring }">
                <span class="status-dot"></span>
                <span>{{ physioStatusText }}</span>
              </div>
            </div>

            <!-- 心率显示 -->
            <div class="heart-rate-display">
              <div class="hr-visual">
                <div class="hr-value-box">
                  <span class="hr-value">{{ currentHeartRate }}</span>
                  <span class="hr-unit">BPM</span>
                </div>
                <div class="hr-trend" :class="hrTrend">
                  <span class="trend-icon">{{ getTrendIcon() }}</span>
                  <span class="trend-text">{{ getTrendText() }}</span>
                </div>
              </div>
              
              <!-- 心率波形图 -->
              <div class="heart-wave-graph">
                <canvas ref="hrCanvas" class="wave-canvas"></canvas>
                <div class="graph-info">
                  <span>心率波形</span>
                  <span>稳定性: {{ hrStability }}%</span>
                </div>
              </div>
            </div>

            <!-- 生理指标 -->
            <div class="physiological-metrics">
              <div class="metric-card">
                <!-- <div class="metric-icon">💓</div> -->
                <div class="metric-info">
                  <h5>平均心率</h5>
                  <p class="metric-value">{{ avgHeartRate }} BPM</p>
                </div>
              </div>
              
              <div class="metric-card">
                <!-- <div class="metric-icon">📈</div> -->
                <div class="metric-info">
                  <h5>心率变异性</h5>
                  <p class="metric-value">{{ hrv }} ms</p>
                </div>
              </div>
              
              <div class="metric-card">
                <!-- <div class="metric-icon">⚡</div> -->
                <div class="metric-info">
                  <h5>压力指数</h5>
                  <p class="metric-value">{{ stressIndex }}</p>
                </div>
              </div>
            </div>

            <!-- 数据完整性 -->
            <div class="data-completeness">
              <div class="completeness-header">
                <span>数据采集进度</span>
                <span class="completeness-value">{{ completeness }}%</span>
              </div>
              <div class="completeness-bar">
                <div 
                  class="completeness-fill" 
                  :style="{ width: `${completeness}%` }"
                ></div>
              </div>
              
              <div class="completeness-indicators">
                <div class="indicator" :class="{ active: isRecording }">
                  <!-- <span class="indicator-icon">🎤</span> -->
                  <span>语音</span>
                </div>
                <div class="indicator" :class="{ active: isCameraActive }">
                  <!-- <span class="indicator-icon">📷</span> -->
                  <span>面部</span>
                </div>
                <div class="indicator" :class="{ active: isHRMonitoring }">
                  <!-- <span class="indicator-icon">💓</span> -->
                  <span>生理</span>
                </div>
              </div>
            </div>

            <!-- 测试说明 -->
            <div class="test-instructions">
              <h4>测试指引</h4>
              <ul class="instructions-list">
                <li>请确保在安静环境中完成测试</li>
                <li>每个问题自然表达 30-60 秒</li>
                <li>保持放松状态，不要紧张</li>
                <li>面部请尽量保持在框内</li>
              </ul>
            </div>
          </div>
        </section>
      </main>

      <!-- 底部控制栏 -->
      <footer class="test-control-footer">
        <button 
          class="control-btn prev-btn" 
          @click="previousQuestion"
          :disabled="currentQuestion === 0 || isRecording"
        >
          <span class="btn-icon">←</span>
          上一题
        </button>
        
        <div class="control-center">
          <div class="test-summary">
            <span class="summary-text">已答 {{ answeredCount }} 题</span>
            <span class="summary-hint" v-if="!isLastQuestion">
              剩余 {{ remainingQuestions }} 题
            </span>
          </div>
        </div>
        
        <button 
          class="control-btn next-btn" 
          @click="nextQuestion"
          :disabled="!currentQuestionData.answered && currentQuestion < questions.length - 1"
        >
          <span v-if="!isLastQuestion">下一题</span>
          <span v-else>完成测试</span>
          <span class="btn-icon">→</span>
        </button>
      </footer>

      <!-- 完成测试模态框 -->
      <div v-if="showCompletionModal" class="completion-modal-overlay">
        <div class="completion-modal">
          <div class="modal-content">
            <div class="completion-icon">✨</div>
            <h2 class="completion-title">测试完成</h2>
            <p class="completion-text">感谢您分享内心的感受</p>
            <p class="completion-subtext">系统正在分析您提供的多模态数据</p>
            
            <div class="processing-progress">
              <div class="progress-steps">
                <div 
                  v-for="step in processingSteps" 
                  :key="step.id"
                  class="progress-step"
                  :class="{ active: currentProcessingStep >= step.id }"
                >
                  <div class="step-indicator">
                    <span v-if="currentProcessingStep > step.id">✓</span>
                    <span v-else>{{ step.id }}</span>
                  </div>
                  <span class="step-text">{{ step.text }}</span>
                </div>
              </div>
              
              <div class="processing-animation">
                <div class="ink-flow"></div>
              </div>
            </div>
            
            <button class="completion-btn" @click="viewResults">
              <span class="btn-icon">📊</span>
              <span>查看详细报告</span>
            </button>
          </div>
        </div>
      </div>

      <!-- 调试面板（开发时可见） -->
      <div v-if="showDebugPanel" class="debug-panel">
        <h4>🔧 调试面板</h4>
        <button @click="clearMockData">清除模拟数据</button>
        <button @click="exportMockData">导出模拟数据</button>
        <button @click="simulateWebSocketMessage">模拟WS消息</button>
        <button @click="triggerMockError">触发模拟错误</button>
        <button @click="toggleDebugPanel">关闭调试</button>
      </div>
    </div>
  </div>
</template>

<script>
import { io } from 'socket.io-client'
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { mentalHealthAPI } from '@/api/mentalHealth'
import { setupWebSocket } from '@/api/websocket'
import { Logger } from 'sass'

export default {
  name: 'ProfessionalTest',
  
  setup() {
    let frameSendInterval = null   // 用于存储定时器ID
    let lastDataQuality = 100

    const audioContext = ref(null)
    const audioStream = ref(null)
    const audioProcessor = ref(null)
    const audioDataBuffer = ref([])
    const sampleRate = 16000 // 16kHz采样率
    const audioChunks = ref([])
    
    const router = useRouter()
    
    // 调试模式
    const showDebugPanel = ref(false)
    
    // 测试状态
    const currentQuestion = ref(0)
    const isRecording = ref(false)
    const isCameraActive = ref(false)
    const cameraLoading = ref(false)
    const isHRMonitoring = ref(false)
    const elapsedTime = ref(0)
    const recordingDuration = ref(0)
    const captureDuration = ref(0)
    
    // 生理数据
    const currentHeartRate = ref(72)
    const avgHeartRate = ref(72)
    const hrv = ref(45)
    const stressIndex = ref(3.2)
    const hrTrend = ref('stable')
    const hrStability = ref(88)
    
    // 音频数据
    const audioLevel = ref(0)
    const audioWave = ref(Array(40).fill(20))
    
    // 摄像头数据
    const isFaceDetected = ref(true)
    const dataQuality = ref(0) 
    const analysisPoints = ref([])
    
    // 测试进度
    const completeness = ref(0)
    const showCompletionModal = ref(false)
    const currentProcessingStep = ref(0)
    
    // 问题数据
    const questions = ref([
      {
        id: 1,
        text: "请描述您最近一周的睡眠质量如何？有什么特别影响您睡眠的事情吗？",
        category: "睡眠状况",
        answered: false,
        duration: 0
      },
      {
        id: 2,
        text: "最近在学习或工作中，您是否感到有压力？可以具体说说是什么让您感到压力吗？",
        category: "压力感受",
        answered: false,
        duration: 0
      },
      {
        id: 3,
        text: "您和同学、同事或家人的关系最近怎么样？有没有让您感到困扰或温暖的事情？",
        category: "人际关系",
        answered: false,
        duration: 0
      },
      {
        id: 4,
        text: "最近有什么让您感到开心、满足或有成就感的事情吗？",
        category: "积极体验",
        answered: false,
        duration: 0
      },
      {
        id: 5,
        text: "当您感到焦虑或压力时，通常会如何应对？有什么特别的方法帮助您放松吗？",
        category: "应对方式",
        answered: false,
        duration: 0
      }
    ])
    
    // 处理步骤
    const processingSteps = ref([
      { id: 1, text: "语音情感分析" },
      { id: 2, text: "面部微表情识别" },
      { id: 3, text: "生理数据整合" },
      { id: 4, text: "综合分析评估" },
      { id: 5, text: "生成报告" }
    ])
    
    // DOM 引用
    const videoElement = ref(null)
    const hrCanvas = ref(null)
    
    // 媒体流
    let mediaRecorder = null
    let analyser = null
    let dataArray = null
    let animationFrame = null
    
    // 定时器
    let testTimer = null
    let recordingTimer = null
    let cameraTimer = null
    let hrTimer = null
    let canvasAnimation = null
    let webSocket = null
    const heartRateHistory = ref([])
    const MAX_HISTORY = 30
    
    // 计算属性
    const currentQuestionData = computed(() => questions.value[currentQuestion.value])
    const progressPercentage = computed(() => ((currentQuestion.value + 1) / questions.value.length) * 100)
    const isLastQuestion = computed(() => currentQuestion.value === questions.value.length - 1)
    const answeredCount = computed(() => questions.value.filter(q => q.answered).length)
    const remainingQuestions = computed(() => questions.value.length - answeredCount.value)

    const socket = io('http://localhost:5000')

    socket.on('heart_rate', (data) => {
      const newHr = data.heart_rate
      if (newHr && newHr > 30 && newHr < 200) {
        currentHeartRate.value = newHr
        // 更新历史数组
        heartRateHistory.value.push(newHr)
        if (heartRateHistory.value.length > MAX_HISTORY) {
          heartRateHistory.value.shift()
        }
        // 更新平均值和 HRV
        avgHeartRate.value = computeAvgHeartRate()
        hrv.value = computeHRV()
      }
    })

    let stressInterval = null
    let stressChangeAmplitude = 2.0
    let lastStressValue = 3.0
    const getStressAmplitude = () => {
      const historyLength = heartRateHistory.value.length
      // 历史越多，幅度越小：最大2.0，指数衰减到0.2，衰减系数0.95每10个数据点
      let amplitude = 2.0 * Math.pow(0.95, historyLength / 10)
      return Math.max(0.2, Math.min(2.0, amplitude))
    }

    // 启动压力模拟（震荡频率不变，但幅度递减）
    const startStressSimulation = () => {
      if (stressInterval) clearInterval(stressInterval)
      
      stressInterval = setInterval(() => {
        // 根据当前心率水平确定基础压力值
        let baseStress = 3.0
        if (currentHeartRate.value > 90) baseStress = 5.0
        else if (currentHeartRate.value > 75) baseStress = 4.0
        
        const amplitude = getStressAmplitude()
        const randomDelta = (Math.random() - 0.5) * amplitude * 2
        let newStress = baseStress + randomDelta
        newStress = Math.min(9.0, Math.max(1.0, newStress))
        stressIndex.value = parseFloat(newStress.toFixed(1))
        lastStressValue = stressIndex.value
      }, 5000) // 每5秒更新一次，频率不变，但幅度递减
    }

    
    const audioStatusText = computed(() => {
      if (isRecording.value) return '录音中'
      if (currentQuestionData.value.answered) return '已回答'
      return '准备录音'
    })
    
    const cameraStatusText = computed(() => {
      if (!isCameraActive.value) return '未开启'
      return isFaceDetected.value ? '采集中' : '检测中'
    })

    const computeAvgHeartRate = () => {
      if (heartRateHistory.value.length === 0) return 72
      const sum = heartRateHistory.value.reduce((a, b) => a + b, 0)
      return Math.round(sum / heartRateHistory.value.length)
    }

    const computeHRV = () => {
      if (heartRateHistory.value.length < 2) return 45
      const mean = computeAvgHeartRate()
      const variance = heartRateHistory.value.reduce((acc, hr) => acc + Math.pow(hr - mean, 2), 0) / heartRateHistory.value.length
      const stdDev = Math.sqrt(variance)
      // 将标准差映射到 20-80ms 范围（经验值）
      let hrvValue = Math.min(80, Math.max(20, stdDev * 2))
      return Math.round(hrvValue)
    }
    
    const physioStatusText = computed(() => {
      if (!isHRMonitoring.value) return '准备监测'
      return '监测中'
    })

    const sendFrameToBackend = async (blob) => {
      const formData = new FormData()
      formData.append('frame', blob, 'frame.jpg')
      
      try {
        const response = await fetch('http://localhost:5000/upload_frame', {
          method: 'POST',
          body: formData
        })
        const result = await response.json()
        if (result.success) {
          isFaceDetected.value = true
          // 波动小：在上次值基础上变化 -2 到 +2，并限制在 90-98 之间
          let delta = Math.floor(Math.random() * 5) - 2 // -2, -1, 0, 1, 2
          let newVal = lastDataQuality + delta
          newVal = Math.min(98, Math.max(90, newVal))
          dataQuality.value = newVal
          lastDataQuality = newVal
        } else {
          console.warn('后端返回失败:', result)
          isFaceDetected.value = false
          dataQuality.value = Math.floor(Math.random() * (85 - 75 + 1) + 75) // 失败时稍低
          lastDataQuality = dataQuality.value
        }
      } catch (error) {
        console.error('发送帧失败:', error)
        isFaceDetected.value = false
        dataQuality.value = Math.floor(Math.random() * (85 - 75 + 1) + 75)
        lastDataQuality = dataQuality.value
      }
    }
    
    // 方法
    const formatTime = (seconds) => {
      const mins = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${mins}:${secs.toString().padStart(2, '0')}`
    }
    
    const getRecordButtonIcon = () => {
      if (currentQuestionData.value.answered) return '✓'
      if (isRecording.value) return '⏹️'
      return '●'
    }
    
    const getRecordButtonTitle = () => {
      if (currentQuestionData.value.answered) return '已回答'
      if (isRecording.value) return '停止录音'
      return '开始回答'
    }
    
    const getRecordButtonSubtitle = () => {
      if (currentQuestionData.value.answered) return '点击继续或等待自动继续'
      if (isRecording.value) return '正在录音，请自然地表达...'
      return '点击开始回答当前问题'
    }
    
    const getTrendIcon = () => {
      if (hrTrend.value === 'rising') return '↗'
      if (hrTrend.value === 'falling') return '↘'
      return '→'
    }
    
    const getTrendText = () => {
      if (hrTrend.value === 'rising') return '心率上升'
      if (hrTrend.value === 'falling') return '心率下降'
      return '心率平稳'
    }
    
    // 开始测试
    const startTest = async () => {
      try {
        // 开始计时
        testTimer = setInterval(() => {
          elapsedTime.value++
        }, 1000)
        
        // 模拟启动测试会话
        const response = await mentalHealthAPI.startTest({
          user_id: 'test_user',
          timestamp: new Date().toISOString()
        })
        
        console.log('✅ 测试启动成功:', response.data)
        
        // 开始心率监测
        startHRMonitoring()

        startStressSimulation()
        
        // 初始化 WebSocket
        initializeWebSocket(response.data.sessionId)
        
      } catch (error) {
        console.error('测试初始化失败:', error)
      }
    }
    
    // 初始化 WebSocket
    const initializeWebSocket = (sessionId) => {
      webSocket = setupWebSocket(sessionId)
      
      webSocket.onMessage((data) => {
        console.log('📨 收到WebSocket消息:', data)
        // 这里可以处理WebSocket消息
        if (data.type === 'analysis_update') {
          // 更新UI显示
        }
      })
      
      webSocket.onOpen(() => {
        console.log('✅ WebSocket连接成功')
      })
      
      webSocket.connect()
    }
    
    // 录音控制
    const toggleRecording = async () => {
      if (isRecording.value) {
        stopRecording()
      } else {
        await startRecording()
      }
    }
    
    const startRecording = async () => {
      try {
        console.log('🎤 开始音频采集...')
        
        // 请求麦克风权限
        audioStream.value = await navigator.mediaDevices.getUserMedia({
          audio: {
            channelCount: 1, // 单声道
            sampleRate: sampleRate,
            echoCancellation: false,
            noiseSuppression: false,
            autoGainControl: false
          }
        })
        
        // 创建音频上下文
        audioContext.value = new (window.AudioContext || window.webkitAudioContext)({
          sampleRate: sampleRate
        })
        
        const source = audioContext.value.createMediaStreamSource(audioStream.value)
        
        // 创建脚本处理器
        audioProcessor.value = audioContext.value.createScriptProcessor(4096, 1, 1)
        
        // 音频处理回调
        audioProcessor.value.onaudioprocess = (audioProcessingEvent) => {
          if (!isRecording.value) return

          const inputBuffer = audioProcessingEvent.inputBuffer
          const channelData = inputBuffer.getChannelData(0) // 单声道

          // 分块参数
          const subChunkSize = 1024      // 每个子块样本数（16ms at 16kHz）
          const numSubChunks = Math.floor(channelData.length / subChunkSize)

          // 临时存储本次回调产生的所有子块音量（可选，也可直接 push）
          for (let chunkIdx = 0; chunkIdx < numSubChunks; chunkIdx++) {
            const start = chunkIdx * subChunkSize
            const end = start + subChunkSize
            let sum = 0
            for (let i = start; i < end; i++) {
              sum += channelData[i] * channelData[i]
            }
            const rms = Math.sqrt(sum / subChunkSize)
            // 映射到 0-100（系数可调）
            let volumePercent = Math.min(100, Math.max(0, Math.floor(rms * 6000)))
            
            // 更新波形数组（保持长度最多 40）
            audioWave.value.push(volumePercent)
            if (audioWave.value.length > 40) {
              audioWave.value.shift()
            }
            
            // 可选：将最后一个子块的音量作为当前整体音量显示
            if (chunkIdx === numSubChunks - 1) {
              audioLevel.value = volumePercent
            }
          }

          // 后续：将整个 channelData 转换为 Int16 并发送（保持原有发送逻辑）
          const int16Array = convertFloat32ToInt16(channelData)
          audioDataBuffer.value.push(...Array.from(int16Array))

          if (audioDataBuffer.value.length >= sampleRate * 2) {
            const dataToSend = [...audioDataBuffer.value]
            audioDataBuffer.value = []
            sendAudioChunkAsync(dataToSend, false)
          }
        }
        
        // 连接音频节点
        source.connect(audioProcessor.value)
        audioProcessor.value.connect(audioContext.value.destination)
        
        // 更新状态
        isRecording.value = true
        recordingDuration.value = 0
        audioDataBuffer.value = []
        audioChunks.value = []
        
        // 开始音频可视化
        startAudioVisualization()
        
        // 开始录音计时
        recordingTimer = setInterval(() => {
          recordingDuration.value++
          
          // 30秒后自动停止
          if (recordingDuration.value >= 30) {
            stopRecording()
          }
        }, 1000)
        
      } catch (error) {
        console.error('开始音频采集失败:', error)
        alert('无法开始音频采集，请检查麦克风权限')
        isRecording.value = false
      }
    }

    // 异步发送音频块
    const sendAudioChunkAsync = (audioData, isFinal = false) => {
      if (audioData.length === 0) return
      
      // 使用 Promise 但不 await，避免阻塞
      new Promise(async (resolve) => {
        try {
          const int16Array = new Int16Array(audioData)
          
          // 创建FormData
          const formData = new FormData()
          formData.append('audio_data', new Blob([int16Array], { type: 'application/octet-stream' }))
          formData.append('sample_rate', sampleRate.toString())
          formData.append('channels', '1')
          formData.append('timestamp', new Date().toISOString())
          formData.append('session_id', 'test_session')
          formData.append('question_id', currentQuestionData.value.id.toString())
          formData.append('is_final', isFinal.toString())
          formData.append('duration', recordingDuration.value.toString())
          
          // 发送到后端API
          const response = await fetch('http://localhost:5000/upload_audio', {
            method: 'POST',
            body: formData
          })
          
          const result = await response.json()
          
          if (result.success) {
            console.log('✅ 音频数据发送成功:', {
              samples: int16Array.length,
              duration: int16Array.length / sampleRate,
              is_final: isFinal
            })
            
            if (isFinal) {
              audioChunks.value.push({
                id: result.audio_id || Date.now().toString(),
                duration: int16Array.length / sampleRate,
                timestamp: new Date().toISOString()
              })
            }
          } else {
            console.warn('音频数据发送失败:', result.error)
          }
        } catch (error) {
          console.error('发送音频数据失败:', error)
        } finally {
          resolve()
        }
      })
    }

    const stopRecording = async () => {
      isRecording.value = false
      
      // 停止音频流
      if (audioStream.value) {
        audioStream.value.getTracks().forEach(track => track.stop())
      }
      
      // 断开音频处理器
      if (audioProcessor.value) {
        audioProcessor.value.disconnect()
      }
      
      // 关闭音频上下文
      if (audioContext.value && audioContext.value.state !== 'closed') {
        await audioContext.value.close()
      }
      
      // 异步发送剩余数据
      if (audioDataBuffer.value.length > 0) {
        const finalData = [...audioDataBuffer.value]
        audioDataBuffer.value = []
        sendAudioChunkAsync(finalData, true)
      }
      
      // 更新问题状态
      currentQuestionData.value.answered = true
      currentQuestionData.value.duration = recordingDuration.value
      
      // 更新数据完整性
      updateCompleteness()
      
      // 清理定时器
      if (recordingTimer) {
        clearInterval(recordingTimer)
        recordingTimer = null
      }
      
      if (animationFrame) {
        cancelAnimationFrame(animationFrame)
        animationFrame = null
      }
      
      // 2秒后自动进入下一题
      if (!isLastQuestion.value) {
        setTimeout(() => {
          nextQuestion()
        }, 2000)
      } else {
        // 最后一题完成
        setTimeout(() => {
          completeTest()
        }, 2000)
      }
    }
    
    const startAudioVisualization = () => {
      
    }

    const convertFloat32ToInt16 = (float32Array) => {
      const int16Array = new Int16Array(float32Array.length)
      for (let i = 0; i < float32Array.length; i++) {
        // 限制在[-1, 1]范围内
        const s = Math.max(-1, Math.min(1, float32Array[i]))
        // 转换为16位整数
        int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7FFF
      }
      return int16Array
    }

    // 更新音频波形显示
    const updateAudioWaveform = (audioData) => {
      // 计算RMS值
      let sum = 0
      for (let i = 0; i < audioData.length; i++) {
        sum += audioData[i] * audioData[i]
      }
      const rms = Math.sqrt(sum / audioData.length)
      
      // 转换为百分比
      audioLevel.value = Math.min(100, rms * 100)
      
      // 更新波形显示
      audioWave.value = audioWave.value.map((_, index) => {
        const time = Date.now() / 1000
        const value = Math.sin(time + index * 0.1) * 20 + 40
        const noise = audioData.length > index ? Math.abs(audioData[index]) * 30 : 0
        return Math.min(100, Math.max(20, value + noise))
      })
    }

    // 发送音频数据到后端
    const sendAudioDataToBackend = async (isFinal = false) => {
      if (audioDataBuffer.value.length === 0) return
      
      try {
        const int16Array = new Int16Array(audioDataBuffer.value)
        
        // 创建FormData
        const formData = new FormData()
        formData.append('audio_data', new Blob([int16Array], { type: 'application/octet-stream' }))
        formData.append('sample_rate', sampleRate.toString())
        formData.append('channels', '1')
        formData.append('timestamp', new Date().toISOString())
        formData.append('session_id', 'test_session')
        formData.append('question_id', currentQuestionData.value.id.toString())
        formData.append('is_final', isFinal.toString())
        formData.append('duration', recordingDuration.value.toString())
        
        // 发送到后端API
        const response = await fetch('http://localhost:5000/upload_audio', {
          method: 'POST',
          body: formData
        })
        
        const result = await response.json()
        
        if (result.success) {
          console.log('✅ 音频数据发送成功:', {
            samples: int16Array.length,
            duration: int16Array.length / sampleRate,
            is_final: isFinal
          })
          
          // 如果是最终数据，存储音频块信息
          if (isFinal) {
            audioChunks.value.push({
              id: result.audio_id || Date.now().toString(),
              duration: int16Array.length / sampleRate,
              timestamp: new Date().toISOString()
            })
          }
          
          // 清空当前缓冲区
          audioDataBuffer.value = []
        } else {
          console.warn('音频数据发送失败:', result.error)
        }
        
      } catch (error) {
        console.error('发送音频数据失败:', error)
      }
    }
    
    const submitAudioFeatures = async () => {
      try {
        // 模拟音频特征
        const audioFeatures = Array(21).fill(0).map(() => Math.random() * 2 - 1)
        
        await mentalHealthAPI.predictMentalHealth({
          audio_features: audioFeatures,
          timestamp: new Date().toISOString()
        })
        
        console.log('✅ 模拟提交音频特征')
      } catch (error) {
        console.error('提交音频特征失败:', error)
      }
    }
    
    const submitCompleteRecording = async () => {
      console.log('✅ 音频采集完成:', {
        chunks: audioChunks.value.length,
        total_duration: recordingDuration.value
      })
    }
    
    // 摄像头控制
    const toggleCamera = async () => {
      if (isCameraActive.value) {
        stopCamera()
      } else {
        await startCamera()
      }
    }
    
    const startCamera = async () => {
      if (cameraLoading.value) return
      cameraLoading.value = true

      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' }
        })

        // 注意：由于 <video> 元素在 v-if="isCameraActive" 内，需要先显示才能访问
        isCameraActive.value = true
        // 等待 DOM 更新（vue 的 nextTick）
        await new Promise(resolve => setTimeout(resolve, 50))

        if (videoElement.value) {
          videoElement.value.srcObject = stream
          videoElement.value.onloadedmetadata = () => {
            videoElement.value.play()
            cameraLoading.value = false
            captureDuration.value = 0
            if (cameraTimer) clearInterval(cameraTimer)
            cameraTimer = setInterval(() => {
              captureDuration.value++
              updateCompleteness()
            }, 1000)

            // 启动帧发送（每秒 2 帧）
            if (frameSendInterval) clearInterval(frameSendInterval)
            frameSendInterval = setInterval(() => {
              if (!isCameraActive.value || !videoElement.value) return
              const video = videoElement.value
              if (video.videoWidth === 0 || video.videoHeight === 0) return
              
              const canvas = document.createElement('canvas')
              canvas.width = video.videoWidth
              canvas.height = video.videoHeight
              const ctx = canvas.getContext('2d')
              ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
              canvas.toBlob((blob) => {
                if (blob) sendFrameToBackend(blob)
              }, 'image/jpeg', 0.7)
            }, 500)
          }
        } else {
          throw new Error('video 元素未找到')
        }
      } catch (err) {
        console.error('摄像头启动失败:', err)
        alert('无法访问摄像头，请检查权限设置')
        isCameraActive.value = false
        cameraLoading.value = false
      }
    }
    
    const stopCamera = () => {
      if (videoElement.value && videoElement.value.srcObject) {
        const tracks = videoElement.value.srcObject.getTracks()
        tracks.forEach(track => track.stop())
        videoElement.value.srcObject = null
      }
      isCameraActive.value = false
      if (cameraTimer) clearInterval(cameraTimer)
      if (frameSendInterval) clearInterval(frameSendInterval)
      captureDuration.value = 0
      updateCompleteness()
    }
    
    const generateAnalysisPoints = () => {
      // 生成面部分析点
      analysisPoints.value = Array.from({ length: 12 }, (_, i) => ({
        id: i,
        x: 30 + Math.random() * 40,
        y: 30 + Math.random() * 40
      }))
    }
    
    const submitFaceFeatures = async () => {
      try {
        // 模拟面部特征
        const faceFeatures = Array(13).fill(0).map(() => Math.random() * 2 - 1)
        
        await mentalHealthAPI.predictMentalHealth({
          face_features: faceFeatures,
          timestamp: new Date().toISOString()
        })
        
        console.log('✅ 模拟提交面部特征')
      } catch (error) {
        console.error('提交面部特征失败:', error)
      }
    }
    

    const sendHeartRateData = async (hrData) => {
      if (!isHRMonitoring.value) return

      try {
        const formData = new FormData()
        formData.append('heart_rate', hrData.heart_rate.toString())
        formData.append('avg_heart_rate', hrData.avg_heart_rate.toString())
        formData.append('hrv', hrData.hrv.toString())
        formData.append('stress_index', hrData.stress_index.toString())
        formData.append('trend', hrData.trend)
        formData.append('stability', hrData.stability.toString())
        formData.append('timestamp', new Date().toISOString())
        formData.append('session_id', 'test_session')         // 与音频/视频保持一致
        formData.append('question_id', currentQuestionData.value.id.toString())

        const response = await fetch('http://localhost:5000/upload_heartrate', {
          method: 'POST',
          body: formData
        })

        const result = await response.json()
        if (result.success) {
          console.log('✅ 心率数据发送成功:', hrData)
        } else {
          console.warn('心率数据发送失败:', result.error)
        }
      } catch (error) {
        console.error('发送心率数据失败:', error)
      }
    }

    // 心率监测
    const startHRMonitoring = () => {
      isHRMonitoring.value = true
      drawHeartRateWave()
      
      // 添加定时器，每 3 秒更新一次心率趋势和稳定性
      if (hrTimer) clearInterval(hrTimer)  // 避免重复
      hrTimer = setInterval(() => {
        updateHRTrend()
      }, 2000)
    }
    
    const updateHRTrend = () => {
      const rand = Math.random()
      if (rand < 0.4) hrTrend.value = 'stable'
      else if (rand < 0.7) hrTrend.value = 'rising'
      else hrTrend.value = 'falling'
      
      // 更新稳定性
      hrStability.value = Math.max(0, Math.min(100, 100 - hrv.value + + Math.round(Math.random() * 10)))
    }
    
    const submitHRFeatures = async () => {
      try {
        // 模拟心率特征
        const hrFeatures = Array(9).fill(0).map(() => Math.random() * 2 - 1)
        
        await mentalHealthAPI.predictMentalHealth({
          hr_features: hrFeatures,
          timestamp: new Date().toISOString()
        })
        
        console.log('✅ 模拟提交心率特征')
      } catch (error) {
        console.error('提交心率特征失败:', error)
      }
    }
    
    const drawHeartRateWave = () => {
      if (!hrCanvas.value) return

      const canvas = hrCanvas.value
      const ctx = canvas.getContext('2d')
      const width = canvas.width
      const height = canvas.height

      // 滑动窗口（显示 50 个点）
      const waveData = Array(50).fill(height / 2)
      
      let phase = 0           // 当前相位（弧度）
      let lastTimestamp = null
      
      const baseAmplitude = 15  // 基础振幅（像素）
      
      const draw = (timestamp) => {
        if (!isHRMonitoring.value) return
        
        if (!lastTimestamp) {
          lastTimestamp = timestamp
          requestAnimationFrame(draw)
          return
        }
        
        // 时间差（秒），限制最大值避免跳跃过大
        let deltaTime = (timestamp - lastTimestamp) / 1000
        deltaTime = Math.min(0.05, deltaTime)
        lastTimestamp = timestamp
        
        // 获取当前心率并限制范围
        let hr = currentHeartRate.value
        hr = Math.min(180, Math.max(40, hr))
        const frequency = hr / 60 * 1.5   // 心跳频率（Hz）
        
        // 相位增量：2π * 频率 * 时间差
        phase += 2 * Math.PI * frequency * deltaTime
        if (phase > 2 * Math.PI) phase -= 2 * Math.PI
        
        // 振幅：心率越高振幅越大（模拟心跳力度）
        let amplitude = baseAmplitude + (hr - 60) * 0.3
        amplitude = Math.min(40, Math.max(8, amplitude))
        
        // 波形值 = 中线 + 振幅 * sin(相位)
        const centerY = height / 2
        let waveValue = centerY + amplitude * Math.sin(phase)
        
        // 添加微小噪声（稳定性越差噪声越大）
        const noiseAmplitude = (100 - hrStability.value) / 100 * 3
        waveValue += (Math.random() - 0.5) * noiseAmplitude
        waveValue = Math.min(height - 5, Math.max(5, waveValue))
        
        // 更新滑动窗口
        waveData.shift()
        waveData.push(waveValue)
        
        // 绘制网格和波形
        ctx.clearRect(0, 0, width, height)
        
        // 网格线
        ctx.strokeStyle = 'rgba(78, 205, 196, 0.1)'
        ctx.lineWidth = 1
        for (let i = 0; i <= 3; i++) {
          const y = (height / 3) * i
          ctx.beginPath()
          ctx.moveTo(0, y)
          ctx.lineTo(width, y)
          ctx.stroke()
        }
        
        // 波形
        ctx.beginPath()
        ctx.moveTo(0, waveData[0])
        for (let i = 1; i < waveData.length; i++) {
          const x = (i / waveData.length) * width
          ctx.lineTo(x, waveData[i])
        }
        ctx.strokeStyle = '#4ECDC4'
        ctx.lineWidth = 2
        ctx.stroke()
        
        canvasAnimation = requestAnimationFrame(draw)
      }
      
      canvasAnimation = requestAnimationFrame(draw)
    }
    
    // 问题导航
    const navigateToQuestion = (index) => {
      const arrayIndex = index - 1
      console.log('导航调试: 请求跳转至索引', index, '对应问题文本:', questions.value[arrayIndex]?.text)
      if (arrayIndex < 0 ||  arrayIndex >= questions.value.length) return
      if (isRecording.value) {
        alert('请先停止当前录音')
        return
      }
      
      currentQuestion.value = arrayIndex
      recordingDuration.value = 0
      audioWave.value = Array(40).fill(20)
    }
    
    const previousQuestion = () => {
      if (currentQuestion.value > 0) {
        navigateToQuestion(currentQuestion.value - 1)
      }
    }
    
    const nextQuestion = () => {
      if (currentQuestion.value < questions.value.length - 1) {
        navigateToQuestion(currentQuestion.value + 1)
      } else if (answeredCount.value === questions.value.length) {
        completeTest()
      }
    }
    
    // 数据完整性
    const updateCompleteness = () => {
      const parts = []
      if (isCameraActive.value) parts.push(40)
      if (isRecording.value) parts.push(30)
      if (isHRMonitoring.value) parts.push(30)
      
      completeness.value = parts.length > 0 
        ? Math.min(100, Math.round(parts.reduce((a, b) => a + b, 0) + (answeredCount.value * 5)))
        : 0
    }
    
    // 完成测试
    const completeTest = async () => {
      // 停止所有监测...
      if (isRecording.value) stopRecording()
      if (isCameraActive.value) stopCamera()
      if (isHRMonitoring.value) {
        isHRMonitoring.value = false
        clearInterval(hrTimer)
        if (canvasAnimation) cancelAnimationFrame(canvasAnimation)
      }

      try {
        const response = await fetch('http://localhost:5000/predict', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ use_realtime: true })
        })
        const result = await response.json()

        if (result.success) {
          // 生成睡眠质量随机数（6.0 - 9.0，保留一位小数）
          const sleepQuality = (Math.random() * 3 + 6).toFixed(1)

          console.log('存储的睡眠质量:', sleepQuality)
          localStorage.setItem('last_test_report', JSON.stringify({
            ...result,
            avgHeartRate: avgHeartRate.value,
            hrv: hrv.value,
            sleepQuality: parseFloat(sleepQuality),
            timestamp: Date.now()
          }))
          // 立即读取验证
          const stored = localStorage.getItem('last_test_report')
          console.log('验证存储:', JSON.parse(stored).sleepQuality)
        } else {
          console.error('预测失败:', result.error)
        }
      } catch (error) {
        console.error('获取预测结果失败:', error)
      }
      
      // 显示完成模态框
      showCompletionModal.value = true
      startProcessing()
    }

    
    const startProcessing = () => {
      let step = 0
      const processingInterval = setInterval(() => {
        if (step < processingSteps.value.length) {
          currentProcessingStep.value = step + 1
          step++
        } else {
          clearInterval(processingInterval)
        }
      }, 1000)
    }
    
    const viewResults = () => {
      router.push('/report')
    }

    // 模拟数据兜底函数（可选）
    const getMockReportData = () => ({
      success: true,
      prediction: 1,
      prediction_class: '轻度压力',
      score: 45,
      confidence: 0.75,
      probabilities: [0.2, 0.5, 0.2, 0.1],
      contributions: { face: 35, audio: 40, hr: 25 },
      explanation: '模拟报告：请完成真实测试后查看详细分析。'
    })
    
    const pauseTest = () => {
      // 暂停测试逻辑
      alert('测试已暂停')
    }
    
    // 调试方法
    const clearMockData = () => {
      mentalHealthAPI.clearMockData()
      alert('模拟数据已清除')
    }
    
    const exportMockData = () => {
      const data = mentalHealthAPI.getMockData()
      console.log('📊 模拟数据:', data)
      alert('数据已导出到控制台')
    }
    
    const simulateWebSocketMessage = () => {
      if (webSocket) {
        webSocket.simulateMessage('debug_message', {
          message: '这是模拟消息',
          timestamp: new Date().toISOString()
        })
        alert('已发送模拟WebSocket消息')
      }
    }
    
    const triggerMockError = () => {
      if (webSocket) {
        webSocket.simulateError()
        alert('已触发模拟错误')
      }
    }
    
    const toggleDebugPanel = () => {
      showDebugPanel.value = !showDebugPanel.value
    }
    
    // 生命周期
    onMounted(() => {
      // 初始化画布
      if (hrCanvas.value) {
        hrCanvas.value.width = hrCanvas.value.offsetWidth
        hrCanvas.value.height = hrCanvas.value.offsetHeight
      }
      
      // 监听窗口大小变化
      window.addEventListener('resize', handleResize)
      
      // 页面加载后，直接开始测试
      startTest()
      
    })
    
    onUnmounted(() => {
      // 清理所有资源
      if (audioStream && typeof audioStream.getTracks === 'function') {
          audioStream.getTracks().forEach(track => track.stop())
      }
      
      if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop()
      }
      
      if (testTimer) clearInterval(testTimer)
      if (recordingTimer) clearInterval(recordingTimer)
      if (cameraTimer) clearInterval(cameraTimer)
      if (hrTimer) clearInterval(hrTimer)
      if (animationFrame) cancelAnimationFrame(animationFrame)
      if (canvasAnimation) cancelAnimationFrame(canvasAnimation)
      
      if (frameSendInterval) clearInterval(frameSendInterval)
      if (videoElement.value && videoElement.value.srcObject) {
        const tracks = videoElement.value.srcObject.getTracks()
        tracks.forEach(track => track.stop())
      }

      if (webSocket) {
        webSocket.close()
      }
      
      window.removeEventListener('resize', handleResize)
      if (videoElement.value && videoElement.value.srcObject) {
        const tracks = videoElement.value.srcObject.getTracks()
        tracks.forEach(track => track.stop())
      }
    })
    
    const handleResize = () => {
      if (hrCanvas.value) {
        hrCanvas.value.width = hrCanvas.value.offsetWidth
        hrCanvas.value.height = hrCanvas.value.offsetHeight
      }
    }
    
    return {
      // 状态
      showDebugPanel,
      currentQuestion,
      isRecording,
      isCameraActive,
      cameraLoading,
      isHRMonitoring,
      elapsedTime,
      recordingDuration,
      captureDuration,
      currentHeartRate,
      avgHeartRate,
      hrv,
      stressIndex,
      hrTrend,
      hrStability,
      audioLevel,
      audioWave,
      isFaceDetected,
      dataQuality,
      analysisPoints,
      completeness,
      showCompletionModal,
      currentProcessingStep,
      
      // 数据
      questions,
      processingSteps,
      currentQuestionData,
      progressPercentage,
      isLastQuestion,
      answeredCount,
      remainingQuestions,
      audioStatusText,
      cameraStatusText,
      physioStatusText,
      
      // DOM引用
      videoElement,
      hrCanvas,
      
      // 方法
      toggleRecording,
      getRecordButtonIcon,
      getRecordButtonTitle,
      getRecordButtonSubtitle,
      formatTime,
      getTrendIcon,
      getTrendText,
      toggleCamera,
      navigateToQuestion,
      previousQuestion,
      nextQuestion,
      pauseTest,
      viewResults,
      
      // 调试方法
      clearMockData,
      exportMockData,
      simulateWebSocketMessage,
      triggerMockError,
      toggleDebugPanel
    }
  }
}
</script>

<style scoped>
/* 基础样式 */
.professional-test-container {
  min-height: 100vh;
  width: 100%;
  position: relative;
  overflow-x: hidden;
  font-family: 'Noto Serif SC', 'Ma Shan Zheng', -apple-system, BlinkMacSystemFont, sans-serif;
  color: #2C3E50;
}

/* 水墨背景层 */
.ink-background {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
  pointer-events: none;
}

.ink-layer {
  position: absolute;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  opacity: 0.08;
  animation: inkFloat 20s ease-in-out infinite;
}

.ink-layer-1 {
  background-image: url('/images/ink-backgrounds/ink-wave-animated.gif');
  animation-delay: 0s;
}

.ink-layer-2 {
  background-image: url('/images/ink-backgrounds/test-bg-main.jpg');
  animation-delay: 5s;
  opacity: 0.05;
}

.ink-layer-3 {
  background-image: url('/images/ink-backgrounds/lotus-flower.png');
  background-position: bottom right;
  background-size: contain;
  animation-delay: 10s;
  opacity: 0.03;
}

@keyframes inkFloat {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-20px) scale(1.02); }
}

/* 主测试界面 */
.test-main-interface {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px);
}

/* 顶部导航栏 */
.test-header {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  padding: 20px 40px;
  border-bottom: 1px solid rgba(78, 205, 196, 0.2);
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.05);
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 200px;
}

.app-title {
  font-size: 1.8rem;
  color: #2A6F79;
  margin: 0;
  font-weight: 600;
  font-family: 'Ma Shan Zheng', cursive;
  letter-spacing: 2px;
  position: relative;
  display: inline-block;
}

.app-title::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, #4ECDC4, transparent);
  border-radius: 1px;
}

.app-subtitle {
  font-size: 0.9rem;
  color: #78909C;
  margin: 0;
  font-weight: 300;
  letter-spacing: 1px;
}

.header-center {
  flex: 1;
  max-width: 500px;
  margin: 0 40px;
}

.test-progress {
  width: 100%;
}

.progress-indicator {
  display: flex;
  align-items: center;
  gap: 15px;
  width: 100%;
}

.progress-label {
  font-size: 0.9rem;
  color: #546E7A;
  font-weight: 500;
  min-width: 60px;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: rgba(232, 244, 243, 0.8);
  border-radius: 3px;
  overflow: hidden;
  position: relative;
}

.progress-bar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, 
    transparent 0%, 
    rgba(255, 255, 255, 0.3) 50%, 
    transparent 100%);
  background-size: 200% 100%;
  animation: shine 2s linear infinite;
}

@keyframes shine {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4ECDC4, #2A6F79);
  border-radius: 3px;
  transition: width 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
  z-index: 2;
}

.progress-value {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2A6F79;
  min-width: 50px;
  text-align: right;
  font-family: 'Arial', sans-serif;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 30px;
  min-width: 200px;
  justify-content: flex-end;
}

.data-status {
  display: flex;
  gap: 15px;
}

.status-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  opacity: 0.5;
  transition: all 0.3s ease;
  position: relative;
  cursor: help;
}

.status-item.active {
  opacity: 1;
  transform: translateY(-2px);
}

.status-item.active .status-dot {
  background: #4ECDC4;
  box-shadow: 0 0 0 3px rgba(78, 205, 196, 0.2);
  animation: statusPulse 2s ease-in-out infinite;
}

@keyframes statusPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #B0BEC5;
  transition: all 0.3s ease;
}

.status-item span:last-child {
  font-size: 0.8rem;
  color: #546E7A;
  font-weight: 500;
}

.header-control {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 20px;
  background: rgba(232, 244, 243, 0.8);
  color: #2A6F79;
  border: 1px solid rgba(78, 205, 196, 0.3);
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.header-control:hover {
  background: rgba(78, 205, 196, 0.1);
  border-color: rgba(78, 205, 196, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.control-icon {
  font-size: 1.1rem;
}

/* 主内容区 */
.test-content-area {
  flex: 1;
  display: grid;
  grid-template-columns: 1.2fr 1.5fr 1.2fr;
  gap: 30px;
  padding: 30px;
  max-width: 2000px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
  min-height: calc(100vh - 140px);
}

@media (max-width: 1600px) {
  .test-content-area {
    grid-template-columns: 1.2fr 1.5fr 1.2fr;
  }
}

@media (max-width: 1400px) {
  .test-content-area {
    grid-template-columns: 1.2fr 1.5fr 1fr;
  }
}

@media (max-width: 1200px) {
  .test-content-area {
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto auto;
  }
  
  .question-section { grid-column: 1; grid-row: 1; }
  .camera-section { grid-column: 2; grid-row: 1; }
  .physiological-section { grid-column: 1 / span 2; grid-row: 2; }
}

@media (max-width: 768px) {
  .test-content-area {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto auto;
    gap: 20px;
    padding: 20px;
  }
  
  .question-section { grid-column: 1; grid-row: 1; }
  .camera-section { grid-column: 1; grid-row: 2; }
  .physiological-section { grid-column: 1; grid-row: 3; }
  
  .test-header {
    padding: 15px 20px;
    flex-wrap: wrap;
    gap: 15px;
  }
  
  .header-left, .header-center, .header-right {
    min-width: 100%;
  }
  
  .header-center {
    margin: 10px 0;
  }
}

/* 通用卡片样式 */
.question-card,
.camera-card,
.physiological-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 30px;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(78, 205, 196, 0.15);
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 600px;
  position: relative;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.question-card:hover,
.camera-card:hover,
.physiological-card:hover {
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  transform: translateY(-5px);
  border-color: rgba(78, 205, 196, 0.3);
}

.question-card::before,
.camera-card::before,
.physiological-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #4ECDC4, #2A6F79);
  opacity: 0.8;
  border-radius: 24px 24px 0 0;
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  padding-bottom: 20px;
  border-bottom: 2px solid rgba(78, 205, 196, 0.1);
  position: relative;
}

.card-header h3 {
  font-size: 1.3rem;
  color: #2A6F79;
  margin: 0;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
}

.camera-status,
.physio-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  color: #546E7A;
  font-weight: 500;
  padding: 6px 12px;
  background: rgba(232, 244, 243, 0.8);
  border-radius: 15px;
  border: 1px solid rgba(78, 205, 196, 0.2);
  transition: all 0.3s ease;
}

.camera-status.active,
.physio-status.active {
  background: rgba(78, 205, 196, 0.1);
  color: #2A6F79;
  border-color: rgba(78, 205, 196, 0.4);
  box-shadow: 0 4px 12px rgba(78, 205, 196, 0.1);
}

.camera-status.active .status-dot,
.physio-status.active .status-dot {
  background: #4ECDC4;
  box-shadow: 0 0 0 3px rgba(78, 205, 196, 0.2);
  animation: statusPulse 2s ease-in-out infinite;
}

/* 左侧：问题回答区 */
.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  padding-bottom: 20px;
  border-bottom: 2px solid rgba(78, 205, 196, 0.1);
}

.question-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.question-number {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2A6F79;
  background: rgba(78, 205, 196, 0.1);
  padding: 6px 12px;
  border-radius: 20px;
  display: inline-block;
}

.question-type {
  font-size: 0.9rem;
  color: #78909C;
  font-weight: 500;
  padding: 6px 12px;
  background: rgba(232, 244, 243, 0.8);
  border-radius: 20px;
  border: 1px solid rgba(78, 205, 196, 0.2);
}

.question-timer {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1rem;
  color: #546E7A;
  font-weight: 500;
  padding: 8px 16px;
  background: rgba(248, 252, 251, 0.8);
  border-radius: 20px;
  border: 1px solid rgba(78, 205, 196, 0.2);
}

.timer-icon {
  font-size: 1.1rem;
  opacity: 0.8;
}

/* 问题主体 */
.question-body {
  margin-bottom: 30px;
}

.question-text {
  font-size: 1.5rem;
  color: #2C3E50;
  line-height: 1.6;
  margin-bottom: 25px;
  font-weight: 500;
  text-align: center;
  padding: 0 20px;
}

.question-guidance {
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: linear-gradient(135deg, rgba(248, 252, 251, 0.9), rgba(232, 244, 243, 0.9));
  border-radius: 16px;
  padding: 20px;
  border: 1px solid rgba(78, 205, 196, 0.2);
  margin-top: 20px;
}

.guidance-item {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #546E7A;
  font-size: 0.95rem;
  line-height: 1.5;
}

.guidance-icon {
  font-size: 1.2rem;
  opacity: 0.8;
  min-width: 24px;
}

/* 语音控制区 */
.voice-control-section {
  margin: 30px 0;
  text-align: center;
}

.record-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 20px;
  width: 100%;
  transition: all 0.3s ease;
  border-radius: 20px;
  position: relative;
  overflow: hidden;
}

.record-btn:not(:disabled):hover {
  background: rgba(248, 252, 251, 0.8);
  transform: translateY(-2px);
}

.record-btn:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.record-btn.recording {
  animation: recordingGlow 2s ease-in-out infinite;
}

@keyframes recordingGlow {
  0%, 100% { 
    box-shadow: 0 0 0 0 rgba(78, 205, 196, 0.4);
  }
  50% { 
    box-shadow: 0 0 0 10px rgba(78, 205, 196, 0);
  }
}

.btn-visual {
  position: relative;
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-circle {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #4ECDC4, #2A6F79);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 
    0 10px 30px rgba(78, 205, 196, 0.3),
    inset 0 2px 4px rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.btn-circle::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, 
    transparent 30%, 
    rgba(255, 255, 255, 0.1) 50%, 
    transparent 70%);
  animation: shineRotate 3s linear infinite;
}

@keyframes shineRotate {
  0% { transform: translateX(-100%) rotate(45deg); }
  100% { transform: translateX(100%) rotate(45deg); }
}

.btn-circle.pulse {
  animation: circlePulse 1.5s ease-in-out infinite;
}

@keyframes circlePulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.record-btn.answered .btn-circle {
  background: linear-gradient(135deg, #7ED321, #5BA829);
  box-shadow: 0 10px 30px rgba(127, 211, 33, 0.3);
}

.btn-icon {
  font-size: 3rem;
  color: white;
  position: relative;
  z-index: 2;
}

.btn-info {
  text-align: center;
}

.btn-title {
  font-size: 1.4rem;
  color: #2A6F79;
  margin-bottom: 8px;
  font-weight: 600;
}

.btn-subtitle {
  font-size: 0.95rem;
  color: #78909C;
  line-height: 1.5;
  max-width: 300px;
  margin: 0 auto;
}

.audio-wave-container {
  margin-top: 30px;
  background: rgba(248, 252, 251, 0.8);
  border-radius: 16px;
  padding: 20px;
  border: 1px solid rgba(78, 205, 196, 0.2);
}

.wave-display {
  display: flex;
  align-items: flex-end;
  height: 80px;
  gap: 2px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  border: 1px solid rgba(78, 205, 196, 0.1);
  margin-bottom: 15px;
}

.wave-bar {
  flex: 1;
  min-height: 4px;
  background: linear-gradient(to top, #4ECDC4, #2A6F79);
  border-radius: 2px 2px 0 0;
  transition: height 0.3s ease;
}

.wave-info {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  color: #546E7A;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

/* 问题导航 */
.questions-navigation {
  flex: 1;
  overflow-y: auto;
  margin-top: 30px;
  padding-right: 10px;
}

.questions-navigation::-webkit-scrollbar {
  width: 6px;
}

.questions-navigation::-webkit-scrollbar-track {
  background: rgba(232, 244, 243, 0.5);
  border-radius: 3px;
}

.questions-navigation::-webkit-scrollbar-thumb {
  background: rgba(78, 205, 196, 0.5);
  border-radius: 3px;
}

.question-nav-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: rgba(248, 252, 251, 0.8);
  border-radius: 12px;
  border: 2px solid transparent;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.question-nav-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(to bottom, #4ECDC4, #2A6F79);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.question-nav-item:hover::before {
  opacity: 1;
}

.question-nav-item:hover {
  background: rgba(232, 244, 243, 0.9);
  transform: translateX(4px);
  border-color: rgba(78, 205, 196, 0.1);
}

.question-nav-item.current {
  background: rgba(78, 205, 196, 0.1);
  border-color: rgba(78, 205, 196, 0.3);
  box-shadow: 0 4px 12px rgba(78, 205, 196, 0.1);
}

.question-nav-item.answered {
  background: rgba(127, 211, 33, 0.1);
  border-color: rgba(127, 211, 33, 0.2);
}

.nav-indicator {
  width: 36px;
  height: 36px;
  min-width: 36px;
  background: rgba(78, 205, 196, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: #2A6F79;
  transition: all 0.3s ease;
  position: relative;
  z-index: 1;
}

.question-nav-item.current .nav-indicator {
  background: linear-gradient(135deg, #4ECDC4, #2A6F79);
  color: white;
  box-shadow: 0 4px 12px rgba(78, 205, 196, 0.3);
}

.question-nav-item.answered .nav-indicator {
  background: #7ED321;
  color: white;
  box-shadow: 0 4px 12px rgba(127, 211, 33, 0.3);
}

.nav-content {
  flex: 1;
  min-width: 0;
  position: relative;
  z-index: 1;
}

.nav-text {
  font-size: 0.9rem;
  color: #2C3E50;
  line-height: 1.4;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.nav-meta {
  font-size: 0.8rem;
  font-weight: 500;
}

.meta-answered {
  color: #7ED321;
  display: flex;
  align-items: center;
  gap: 5px;
}

.meta-current {
  color: #4ECDC4;
  display: flex;
  align-items: center;
  gap: 5px;
}

.meta-pending {
  color: #78909C;
  font-size: 0.75rem;
}

/* 中间：摄像头视图 */
.camera-view-container {
  flex: 1;
  margin-bottom: 25px;
  display: flex;
  flex-direction: column;
  min-height: 400px;
  background: linear-gradient(135deg, rgba(248, 252, 251, 0.9), rgba(232, 244, 243, 0.9));
  border-radius: 20px;
  border: 2px dashed rgba(78, 205, 196, 0.3);
  overflow: hidden;
  position: relative;
}

.camera-view-container.active {
  border-style: solid;
  border-color: rgba(78, 205, 196, 0.5);
}

.camera-off-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 40px;
  position: relative;
  z-index: 1;
}

.camera-off-state::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('/images/ink-backgrounds/lotus-flower.png') center/contain no-repeat;
  opacity: 0.05;
  z-index: 0;
}

.off-content {
  position: relative;
  z-index: 2;
  max-width: 300px;
}

.off-icon {
  font-size: 5rem;
  color: rgba(78, 205, 196, 0.5);
  margin-bottom: 20px;
  animation: gentleFloat 3s ease-in-out infinite;
}

@keyframes gentleFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.camera-off-state h4 {
  font-size: 1.4rem;
  color: #2A6F79;
  margin-bottom: 10px;
  font-weight: 600;
}

.camera-off-state p {
  color: #546E7A;
  line-height: 1.5;
  margin-bottom: 25px;
}

.camera-toggle-btn {
  background: linear-gradient(135deg, #4ECDC4, #2A6F79);
  color: white;
  border: none;
  border-radius: 25px;
  padding: 12px 30px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(78, 205, 196, 0.3);
  position: relative;
  overflow: hidden;
}

.camera-toggle-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #2A6F79, #4ECDC4);
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: 1;
}

.camera-toggle-btn:hover:not(:disabled)::before {
  opacity: 1;
}

.camera-toggle-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(78, 205, 196, 0.4);
}

.camera-toggle-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.camera-toggle-btn span {
  position: relative;
  z-index: 2;
}

/* 摄像头实时视图 */
.camera-live-view {
  flex: 1;
  position: relative;
  background: #1A2B3A;
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.camera-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transform: scaleX(-1);
  filter: brightness(1.05) contrast(1.1);
}

.face-detection-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.face-guide {
  width: 400px;
  height: 500px;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.guide-frame {
  width: 100%;
  height: 100%;
  border: 2px solid rgba(255, 255, 255, 0.6);
  border-radius: 20%;
  position: relative;
  animation: frameFloat 3s ease-in-out infinite;
}

@keyframes frameFloat {
  0%, 100% { 
    border-color: rgba(255, 255, 255, 0.6);
    transform: scale(1);
  }
  50% { 
    border-color: rgba(255, 255, 255, 0.9);
    transform: scale(1.02);
  }
}

.guide-corner {
  position: absolute;
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.8);
}

.guide-corner.top-left {
  top: -2px;
  left: -2px;
  border-right: none;
  border-bottom: none;
  border-top-left-radius: 6px;
}

.guide-corner.top-right {
  top: -2px;
  right: -2px;
  border-left: none;
  border-bottom: none;
  border-top-right-radius: 6px;
}

.guide-corner.bottom-left {
  bottom: -2px;
  left: -2px;
  border-right: none;
  border-top: none;
  border-bottom-left-radius: 6px;
}

.guide-corner.bottom-right {
  bottom: -2px;
  right: -2px;
  border-left: none;
  border-top: none;
  border-bottom-right-radius: 6px;
}

.guide-text {
  position: absolute;
  bottom: -40px;
  color: white;
  font-size: 0.9rem;
  text-align: center;
  background: rgba(0, 0, 0, 0.7);
  padding: 8px 16px;
  border-radius: 20px;
  backdrop-filter: blur(4px);
  width: auto;
  margin: 0;
  white-space: nowrap;
}

.analysis-points {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.analysis-point {
  position: absolute;
  width: 6px;
  height: 6px;
  background: rgba(78, 205, 196, 0.8);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  box-shadow: 
    0 0 0 2px rgba(78, 205, 196, 0.3),
    0 0 8px rgba(78, 205, 196, 0.5);
  animation: pointPulse 1.5s ease-in-out infinite;
}

@keyframes pointPulse {
  0%, 100% { 
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.8;
  }
  50% { 
    transform: translate(-50%, -50%) scale(1.3);
    opacity: 1;
  }
}

.capture-status {
  position: absolute;
  top: 20px;
  right: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.9rem;
  backdrop-filter: blur(4px);
  z-index: 10;
}

.status-indicator {
  width: 8px;
  height: 8px;
  background: #4ECDC4;
  border-radius: 50%;
}

.status-indicator.pulse {
  animation: statusPulse 2s ease-in-out infinite;
}

@keyframes statusPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

/* 数据采集信息 */
.capture-info {
  margin-top: 20px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px;
  background: rgba(248, 252, 251, 0.8);
  border-radius: 12px;
  border: 1px solid rgba(78, 205, 196, 0.2);
  transition: all 0.3s ease;
}

.info-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(78, 205, 196, 0.1);
  border-color: rgba(78, 205, 196, 0.4);
}

.info-icon {
  font-size: 1.5rem;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 10px;
  color: #2A6F79;
  flex-shrink: 0;
}

.info-content {
  flex: 1;
  min-width: 0;
}

.info-label {
  display: block;
  font-size: 0.8rem;
  color: #78909C;
  margin-bottom: 4px;
  font-weight: 500;
}

.info-value {
  display: block;
  font-size: 1.1rem;
  color: #2C3E50;
  font-weight: 600;
  font-family: 'Arial', sans-serif;
}

.info-value.good {
  color: #7ED321;
}

.info-value.active {
  color: #4ECDC4;
  animation: valuePulse 2s ease-in-out infinite;
}

@keyframes valuePulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

/* 右侧：生理数据 */
.heart-rate-display {
  text-align: center;
  margin-bottom: 25px;
  padding: 25px;
  background: linear-gradient(135deg, rgba(248, 252, 251, 0.9), rgba(232, 244, 243, 0.9));
  border-radius: 20px;
  border: 1px solid rgba(78, 205, 196, 0.2);
}

.hr-visual {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.hr-value-box {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 8px;
  position: relative;
}

.hr-value {
  font-size: 3.5rem;
  font-weight: 700;
  color: #2A6F79;
  font-family: 'Arial', sans-serif;
  line-height: 1;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: relative;
}

.hr-value::after {
  content: '';
  position: absolute;
  bottom: 5px;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, 
    transparent 0%, 
    #4ECDC4 20%, 
    #2A6F79 50%, 
    #4ECDC4 80%, 
    transparent 100%);
  border-radius: 2px;
  opacity: 0.8;
}

.hr-unit {
  font-size: 1.3rem;
  color: #78909C;
  font-weight: 500;
  margin-left: 5px;
}

.hr-trend {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
  background: rgba(232, 244, 243, 0.8);
  border: 1px solid rgba(78, 205, 196, 0.2);
  transition: all 0.3s ease;
}

.hr-trend.rising {
  background: rgba(255, 107, 107, 0.1);
  color: #FF6B6B;
  border-color: rgba(255, 107, 107, 0.2);
}

.hr-trend.falling {
  background: rgba(78, 205, 196, 0.1);
  color: #2A6F79;
  border-color: rgba(78, 205, 196, 0.3);
}

.hr-trend.stable {
  background: rgba(255, 167, 38, 0.1);
  color: #FFA726;
  border-color: rgba(255, 167, 38, 0.2);
}

.trend-icon {
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
}

/* 心率波形图 */
.heart-wave-graph {
  margin-top: 20px;
  position: relative;
}

.wave-canvas {
  width: 100%;
  height: 120px;
  background: rgba(248, 252, 251, 0.8);
  border-radius: 12px;
  border: 1px solid rgba(78, 205, 196, 0.2);
  display: block;
}

.graph-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  font-size: 0.85rem;
  color: #546E7A;
}

/* 生理指标 */
.physiological-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin: 25px 0;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px;
  background: rgba(248, 252, 251, 0.8);
  border-radius: 12px;
  border: 1px solid rgba(78, 205, 196, 0.2);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.metric-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 3px;
  height: 100%;
  background: linear-gradient(to bottom, #4ECDC4, #2A6F79);
  opacity: 0.5;
  border-radius: 3px 0 0 3px;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(78, 205, 196, 0.1);
  border-color: rgba(78, 205, 196, 0.4);
}

.metric-icon {
  font-size: 1.8rem;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 12px;
  color: #2A6F79;
  flex-shrink: 0;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
}

.metric-info {
  flex: 1;
  min-width: 0;
}

.metric-info h5 {
  font-size: 0.85rem;
  color: #2A6F79;
  margin-bottom: 4px;
  font-weight: 600;
}

.metric-value {
  font-size: 1.2rem;
  font-weight: 700;
  color: #2C3E50;
  font-family: 'Arial', sans-serif;
}

/* 数据完整性 */
.data-completeness {
  background: rgba(248, 252, 251, 0.8);
  border-radius: 16px;
  padding: 20px;
  border: 1px solid rgba(78, 205, 196, 0.2);
  margin: 25px 0;
}

.completeness-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 0.9rem;
  color: #546E7A;
  font-weight: 500;
}

.completeness-value {
  font-weight: 600;
  color: #2A6F79;
  font-family: 'Arial', sans-serif;
  background: rgba(78, 205, 196, 0.1);
  padding: 4px 12px;
  border-radius: 20px;
  border: 1px solid rgba(78, 205, 196, 0.2);
}

.completeness-bar {
  height: 8px;
  background: rgba(232, 244, 243, 0.8);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 20px;
  position: relative;
}

.completeness-bar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, 
    transparent 0%, 
    rgba(255, 255, 255, 0.3) 50%, 
    transparent 100%);
  background-size: 200% 100%;
  animation: shine 2s linear infinite;
}

.completeness-fill {
  height: 100%;
  background: linear-gradient(90deg, #4ECDC4, #2A6F79);
  border-radius: 4px;
  transition: width 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
  z-index: 2;
}

.completeness-indicators {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  opacity: 0.5;
  transition: all 0.3s ease;
  flex: 1;
  padding: 10px;
  border-radius: 10px;
  background: transparent;
}

.indicator.active {
  opacity: 1;
  transform: scale(1.1);
  background: rgba(78, 205, 196, 0.1);
  border: 1px solid rgba(78, 205, 196, 0.2);
  box-shadow: 0 4px 12px rgba(78, 205, 196, 0.1);
}

.indicator-icon {
  font-size: 1.5rem;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(232, 244, 243, 0.8);
  border-radius: 50%;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.indicator.active .indicator-icon {
  background: rgba(78, 205, 196, 0.2);
  border-color: rgba(78, 205, 196, 0.4);
  box-shadow: 0 4px 12px rgba(78, 205, 196, 0.2);
  animation: iconPulse 2s ease-in-out infinite;
}

@keyframes iconPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.indicator span:last-child {
  font-size: 0.8rem;
  color: #546E7A;
  font-weight: 500;
}

/* 测试说明 */
.test-instructions {
  background: linear-gradient(135deg, rgba(248, 252, 251, 0.9), rgba(232, 244, 243, 0.9));
  border-radius: 16px;
  padding: 20px;
  border: 1px solid rgba(78, 205, 196, 0.2);
  margin-top: 20px;
}

.test-instructions h4 {
  font-size: 1.1rem;
  color: #2A6F79;
  margin-bottom: 15px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
}

.test-instructions h4::before {
  content: '📋';
  font-size: 1.2rem;
}

.instructions-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.instructions-list li {
  font-size: 0.9rem;
  color: #546E7A;
  line-height: 1.5;
  padding-left: 24px;
  position: relative;
}

.instructions-list li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #4ECDC4;
  font-weight: bold;
  width: 20px;
  text-align: center;
}

/* 底部控制栏 */
.test-control-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 40px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(78, 205, 196, 0.2);
  position: sticky;
  bottom: 0;
  z-index: 100;
  box-shadow: 0 -4px 30px rgba(0, 0, 0, 0.05);
}

.control-btn {
  padding: 14px 32px;
  border-radius: 25px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  min-width: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  position: relative;
  overflow: hidden;
}

.control-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, 
    rgba(255, 255, 255, 0.1) 0%, 
    rgba(255, 255, 255, 0.3) 50%, 
    rgba(255, 255, 255, 0.1) 100%);
  background-size: 200% 100%;
  animation: shine 3s linear infinite;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.control-btn:hover:not(:disabled)::before {
  opacity: 1;
}

.prev-btn {
  background: white;
  color: #546E7A;
  border: 2px solid rgba(78, 205, 196, 0.3);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.prev-btn:hover:not(:disabled) {
  background: rgba(232, 244, 243, 0.5);
  border-color: rgba(78, 205, 196, 0.5);
  transform: translateX(-4px);
  box-shadow: 0 8px 25px rgba(78, 205, 196, 0.2);
}

.next-btn {
  background: linear-gradient(135deg, #4ECDC4, #2A6F79);
  color: white;
  box-shadow: 0 4px 15px rgba(78, 205, 196, 0.3);
}

.next-btn:hover:not(:disabled) {
  transform: translateX(4px);
  box-shadow: 0 8px 25px rgba(78, 205, 196, 0.4);
}

.control-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.control-btn:disabled::before {
  display: none;
}

.btn-icon {
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  position: relative;
  z-index: 2;
}

.control-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.test-summary {
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.summary-text {
  font-size: 1.1rem;
  color: #2A6F79;
  font-weight: 600;
}

.summary-hint {
  font-size: 0.9rem;
  color: #78909C;
  font-weight: 500;
}

/* 完成测试模态框 */
.completion-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(20px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.completion-modal {
  background: linear-gradient(135deg, #F9FCFB, #E8F4F3);
  border-radius: 32px;
  padding: 50px;
  max-width: 600px;
  width: 100%;
  text-align: center;
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(78, 205, 196, 0.2);
  position: relative;
  overflow: hidden;
  animation: modalSlideUp 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes modalSlideUp {
  from { 
    opacity: 0;
    transform: translateY(50px) scale(0.9);
  }
  to { 
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.completion-modal::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 6px;
  background: linear-gradient(90deg, 
    #4ECDC4, #2A6F79, #4ECDC4, #2A6F79, #4ECDC4);
  background-size: 200% 100%;
  animation: gradientFlow 3s linear infinite;
}

.completion-icon {
  font-size: 5rem;
  margin-bottom: 20px;
  animation: 
    gentleFloat 3s ease-in-out infinite,
    iconGlow 2s ease-in-out infinite;
}

@keyframes iconGlow {
  0%, 100% { 
    filter: drop-shadow(0 0 10px rgba(78, 205, 196, 0.5));
  }
  50% { 
    filter: drop-shadow(0 0 20px rgba(78, 205, 196, 0.8));
  }
}

.completion-title {
  font-size: 2.5rem;
  color: #2A6F79;
  margin-bottom: 10px;
  font-weight: 600;
  letter-spacing: 1px;
}

.completion-text {
  font-size: 1.3rem;
  color: #546E7A;
  margin-bottom: 5px;
  line-height: 1.5;
}

.completion-subtext {
  font-size: 1rem;
  color: #78909C;
  margin-bottom: 40px;
  line-height: 1.5;
}

.processing-progress {
  margin: 40px 0;
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  margin-bottom: 30px;
  position: relative;
}

.progress-steps::before {
  content: '';
  position: absolute;
  top: 20px;
  left: 40px;
  right: 40px;
  height: 3px;
  background: rgba(232, 244, 243, 0.8);
  z-index: 1;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  position: relative;
  z-index: 2;
  flex: 1;
}

.step-indicator {
  width: 40px;
  height: 40px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: #B0BEC5;
  border: 3px solid rgba(232, 244, 243, 0.8);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.5s ease;
  position: relative;
  z-index: 2;
}

.progress-step.active .step-indicator {
  background: linear-gradient(135deg, #4ECDC4, #2A6F79);
  color: white;
  border-color: transparent;
  box-shadow: 0 4px 20px rgba(78, 205, 196, 0.4);
  animation: stepPulse 2s ease-in-out infinite;
}

@keyframes stepPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.step-text {
  font-size: 0.85rem;
  color: #78909C;
  font-weight: 500;
  text-align: center;
  max-width: 100px;
  line-height: 1.4;
  transition: all 0.5s ease;
}

.progress-step.active .step-text {
  color: #2A6F79;
  font-weight: 600;
}

.processing-animation {
  height: 60px;
  position: relative;
  overflow: hidden;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(78, 205, 196, 0.2);
}

.ink-flow {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  width: 0;
  background: linear-gradient(90deg, 
    rgba(78, 205, 196, 0.8), 
    rgba(42, 111, 121, 0.8), 
    rgba(78, 205, 196, 0.8));
  background-size: 200% 100%;
  animation: 
    flowProgress 3s linear infinite,
    gradientFlow 2s linear infinite;
  border-radius: 10px;
}

@keyframes flowProgress {
  0% { width: 0%; left: 0; }
  50% { width: 100%; left: 0; }
  100% { width: 0%; left: 100%; }
}

.completion-btn {
  background: linear-gradient(135deg, #4ECDC4, #2A6F79);
  color: white;
  border: none;
  border-radius: 30px;
  padding: 18px 50px;
  font-size: 1.2rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 30px rgba(78, 205, 196, 0.3);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  width: 100%;
  margin-top: 30px;
  position: relative;
  overflow: hidden;
}

.completion-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #2A6F79, #4ECDC4);
  opacity: 0;
  transition: opacity 0.4s ease;
  z-index: 1;
}

.completion-btn:hover::before {
  opacity: 1;
}

.completion-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(78, 205, 196, 0.4);
}

.completion-btn .btn-icon {
  position: relative;
  z-index: 2;
}

.completion-btn span:last-child {
  position: relative;
  z-index: 2;
}

/* 调试面板 */
.debug-panel {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(78, 205, 196, 0.3);
  border-radius: 12px;
  padding: 20px;
  z-index: 1000;
  max-width: 300px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.debug-panel h4 {
  color: #2A6F79;
  margin-bottom: 15px;
  font-size: 1.1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.debug-panel button {
  display: block;
  width: 100%;
  padding: 10px 15px;
  margin-bottom: 8px;
  background: rgba(78, 205, 196, 0.1);
  border: 1px solid rgba(78, 205, 196, 0.3);
  border-radius: 8px;
  color: #2A6F79;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.debug-panel button:hover {
  background: rgba(78, 205, 196, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(78, 205, 196, 0.1);
}

.debug-panel button:last-child {
  margin-bottom: 0;
  background: rgba(255, 107, 107, 0.1);
  border-color: rgba(255, 107, 107, 0.2);
  color: #FF6B6B;
}

.debug-panel button:last-child:hover {
  background: rgba(255, 107, 107, 0.2);
}

/* 响应式调整 */
@media (max-width: 1400px) {
  .test-content-area {
    grid-template-columns: 1.2fr 1.5fr 1.2fr;
  }
  
  .question-text {
    font-size: 1.3rem;
  }
  
  .hr-value {
    font-size: 3rem;
  }
}

@media (max-width: 1200px) {
  .test-content-area {
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto auto;
  }
  
  .info-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .physiological-metrics {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .debug-panel {
    position: relative;
    bottom: auto;
    right: auto;
    max-width: 100%;
    margin-top: 20px;
  }
}

@media (max-width: 768px) {
  .test-content-area {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto auto;
  }
  
  .question-card,
  .camera-card,
  .physiological-card {
    min-height: auto;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .physiological-metrics {
    grid-template-columns: 1fr;
  }
  
  .progress-steps {
    flex-wrap: wrap;
    gap: 20px;
  }
  
  .progress-step {
    flex: 0 0 calc(50% - 20px);
  }
  
  .test-header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .header-left,
  .header-center,
  .header-right {
    width: 100%;
  }
  
  .progress-indicator {
    flex-direction: column;
    gap: 10px;
  }
  
  .data-status {
    justify-content: center;
  }
  
  .test-control-footer {
    flex-direction: column;
    gap: 15px;
    padding: 20px;
  }
  
  .control-btn {
    width: 100%;
  }
  
  .debug-panel {
    position: relative;
    bottom: auto;
    right: auto;
    max-width: 100%;
    margin: 20px;
  }
}

@media (max-width: 480px) {
  .completion-modal {
    padding: 30px 20px;
  }
  
  .completion-title {
    font-size: 2rem;
  }
  
  .question-text {
    font-size: 1.2rem;
  }
  
  .hr-value {
    font-size: 2.5rem;
  }
  
  .btn-circle {
    width: 100px;
    height: 100px;
  }
  
  .btn-icon {
    font-size: 2.5rem;
  }
}
</style>