<template>
  <div class="report-container">
    <!-- 加载组件 -->
    <Loading 
      :show="loading" 
      :title="'正在生成评估报告'" 
      :subtitle="'AI正在分析您的多模态数据，请稍候...'" 
    />

    <!-- 主报告区域 -->
    <div class="report-wrapper" ref="reportWrapper">
      <!-- 头部 -->
      <header class="report-header">
        <div class="header-content">
          <div class="header-brand">
            <h1 class="brand-title">心镜·守望</h1>
            <p class="brand-subtitle">心理健康智能评估系统</p>
          </div>
          
          <div class="header-info">
            <div class="info-item">
              <span class="info-label">报告编号</span>
              <span class="info-value">{{ reportId }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">评估时间</span>
              <span class="info-value">{{ evaluateTime }}</span>
            </div>
          </div>
        </div>
        
        <div class="header-actions">
          <button 
            class="btn-export" 
            @click="exportToPdf" 
            :disabled="exporting"
            :class="{ 'exporting': exporting }"
          >
            <span class="btn-icon">📥</span>
            <span class="btn-text">{{ exporting ? '正在生成...' : '导出专业报告' }}</span>
          </button>
        </div>
      </header>

      <!-- 主内容网格 -->
      <main class="report-content" ref="reportContent">
        <!-- 左侧列 -->
        <section class="left-column">
          <!-- 个人信息卡片 -->
          <div class="card profile-card">
            <div class="profile-header">
              <div class="avatar-container">
                <div class="avatar">
                  <img 
                    src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='40' r='20' fill='%23e0f7fa'/%3E%3Ccircle cx='50' cy='85' r='30' fill='%23e0f7fa'/%3E%3C/svg%3E" 
                    alt="用户头像"
                  >
                </div>
                <div class="profile-info">
                  <h3>保密用户</h3>
                  <p class="user-id">ID: {{ reportId }}</p>
                </div>
              </div>
            </div>

            <!-- 综合评分 -->
            <div class="overall-score">
              <div class="score-display">
                <div class="score-number" :class="getScoreClass(reportData.score)">
                  {{ reportData.score }}
                </div>
                <div class="score-label">综合评分</div>
              </div>
              <div class="score-details">
                <div class="detail-item">
                  <span class="detail-label">等级</span>
                  <span class="detail-value" :class="getScoreClass(reportData.score)">
                    {{ getScoreLevel(reportData.score).level }}
                  </span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">置信度</span>
                  <span class="detail-value">{{ (reportData.confidence * 100).toFixed(1) }}%</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 多模态贡献度分析 -->
          <div class="card contribution-card">
            <div class="card-header">
              <h3>多模态贡献度分析</h3>
              <span class="card-subtitle">各数据源对评估的贡献权重</span>
            </div>
            
            <div class="contributions-horizontal">
              <div 
                v-for="(value, key) in reportData.contributions" 
                :key="key"
                class="contribution-item-h"
              >
                <div class="contrib-info">
                  <span class="contrib-icon">{{ getContributionIcon(key) }}</span>
                  <span class="contrib-label">{{ getContributionLabel(key) }}</span>
                </div>
                
                <div class="contrib-details">
                  <div class="contrib-bar">
                    <div 
                      class="contrib-fill" 
                      :style="{ width: `${Math.round(value*10000)/10000}%` }"
                    ></div>
                  </div>
                  <div class="contrib-value">
                    <span class="value-number">{{ Math.round(value*10000)/10000 }}%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 对测评者的话 -->
          <div class="card message-card">
            <div class="message-header">
              <span class="message-icon">💌</span>
              <h3>给测评者的话</h3>
            </div>
            
            <div class="message-content">
              <p>亲爱的朋友，</p>
              <p>感谢您对自己的心理健康给予关注。完成这次评估，本身就是对自己的关爱和负责的表现。</p>
              
              <p>无论评估结果如何，请记住以下要点：</p>
              <ul>
                <li><strong>动态视角</strong>：心理健康是一个动态的过程，今天的状态不代表永远。您有改变和改善的能力。</li>
                <li><strong>正常波动</strong>：每个人都有情绪起伏，这是完全正常的人类经历。</li>
                <li><strong>寻求帮助</strong>：寻求帮助是勇气的表现，不是软弱，专业支持很重要。</li>
                <li><strong>微小改变</strong>：微小的改变也能带来积极的影响。</li>
              </ul>
              
              <p>心理健康与身体健康同样重要。无论面对什么挑战，记住您不是孤独的。</p>
              
              <div class="signature">
                <p>—— 心镜·守望团队</p>
                <p class="date">2026年4月</p>
              </div>
            </div>
          </div>
        </section>

        <!-- 中间列 -->
        <section class="center-column">
          <!-- AI评估结论 -->
          <div class="card conclusion-card">
            <div class="card-header">
              <h3>AI综合评估结论</h3>
              <span class="confidence-badge">置信度: {{ (reportData.confidence * 100).toFixed(1) }}%</span>
            </div>
            
            <div class="prediction-display" :class="getPredictionClass(reportData.score)">
              <div class="prediction-title">心理状态评估</div>
              <div class="prediction-value">{{ getPredictionLevel(reportData.score) }}</div>
              <div class="prediction-score">压力指数: <span>{{ reportData.stressIndex }}</span> 分</div>
            </div>
            
            <div class="explanation-text">
              <p>{{ reportData.explanation }}</p>
            </div>
          </div>

          <!-- 情绪分布图 -->
          <div class="card emotion-card">
            <div class="card-header">
              <h3>情绪状态分布</h3>
              <span class="card-subtitle">实时情绪构成分析</span>
            </div>
            
            <div class="chart-container">
              <div class="chart-wrapper">
                <canvas ref="emotionChart" class="emotion-chart"></canvas>
              </div>
              <div class="emotion-legend">
                <div 
                  v-for="(value, emotion) in reportData.emotionRatio" 
                  :key="emotion"
                  class="legend-item"
                >
                  <span 
                    class="legend-color" 
                    :style="{ backgroundColor: emotionColors[emotion] }"
                  ></span>
                  <span class="legend-label">{{ emotionLabels[emotion] }}</span>
                  <span class="legend-value">{{ value }}%</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 生理指标趋势 -->
          <div class="card hrv-card">
            <div class="card-header">
              <h3>生理指标趋势</h3>
              <span class="card-subtitle">心率变异性(HRV)分析</span>
            </div>
            
            <div class="hrv-chart-wrapper">
              <canvas ref="waveChart" class="wave-chart"></canvas>
            </div>
            
            <div class="hrv-metrics">
              <div class="hrv-metric">
                <span class="metric-value">{{ reportData.physiologicalMetrics?.avgHeartRate || 72 }}</span>
                <span class="metric-label">平均心率(bpm)</span>
              </div>
              <div class="hrv-metric">
                <span class="metric-value positive">{{ reportData.physiologicalMetrics?.hrv || 45 }}ms</span>
                <span class="metric-label">HRV指数</span>
              </div>
              <div class="hrv-metric">
                <span class="metric-value">{{ reportData.physiologicalMetrics?.sleepQuality || 7.2 }}/10</span>
                <span class="metric-label">睡眠质量</span>
              </div>
            </div>
          </div>

          <!-- 心理健康风险评估 -->
          <div class="card risk-card">
            <div class="card-header">
              <h3>心理健康风险评估</h3>
              <span class="card-subtitle">风险等级评估</span>
            </div>
            
            <div class="risk-grid">
              <div 
                v-for="(risk, key) in reportData.riskAssessment" 
                :key="key"
                class="risk-item"
                :class="getRiskClass(risk)"
              >
                <span class="risk-label">{{ getRiskLabel(key) }}</span>
                <span class="risk-value">{{ risk }}</span>
              </div>
            </div>
          </div>
        </section>

        <!-- 右侧列 -->
        <section class="right-column">
          <!-- 心理健康援助资源 -->
          <div class="card resource-card">
            <div class="card-header">
              <h3>心理健康援助资源</h3>
              <span class="card-subtitle">如需帮助，可联系以下专业资源</span>
            </div>
            
            <div class="resource-links-vertical">
              <!-- 国家机构 -->
              <a href="https://www.nhc.gov.cn/" target="_blank" class="resource-link" @click.prevent="openLink('https://www.nhc.gov.cn/')">
                <span class="link-icon">🏥</span>
                <div class="link-content">
                  <strong>国家卫生健康委员会</strong>
                  <p>心理健康与精神卫生政策官方网站</p>
                </div>
              </a>
              
              <a href="https://www.cma.org.cn/" target="_blank" class="resource-link" @click.prevent="openLink('https://www.cma.org.cn/')">
                <span class="link-icon">👨‍⚕️</span>
                <div class="link-content">
                  <strong>中华医学会精神医学分会</strong>
                  <p>专业精神科医生资源与学术支持</p>
                </div>
              </a>
              
              <a href="https://www.xlzx.cn/" target="_blank" class="resource-link" @click.prevent="openLink('https://www.xlzx.cn/')">
                <span class="link-icon">🧠</span>
                <div class="link-content">
                  <strong>中国心理学会</strong>
                  <p>专业心理咨询与治疗认证机构</p>
                </div>
              </a>
              
              <!-- 热线服务 -->
              <div class="hotline-section">
                <h4>心理援助热线</h4>
                <div class="hotline-list">
                  <div class="hotline-item">
                    <span class="hotline-name">全国心理援助热线</span>
                    <span class="hotline-number">400-161-9995</span>
                    <span class="hotline-desc">24小时免费服务</span>
                  </div>
                  <div class="hotline-item">
                    <span class="hotline-name">北京市心理援助热线</span>
                    <span class="hotline-number">010-82951332</span>
                  </div>
                  <div class="hotline-item">
                    <span class="hotline-name">上海市心理援助热线</span>
                    <span class="hotline-number">021-12320-5</span>
                  </div>
                  <div class="hotline-item">
                    <span class="hotline-name">广州市心理援助热线</span>
                    <span class="hotline-number">020-81899120</span>
                  </div>
                  <div class="hotline-item">
                    <span class="hotline-name">深圳市心理援助热线</span>
                    <span class="hotline-number">0755-25629459</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 详细免责声明 -->
          <div class="card disclaimer-card">
            <div class="disclaimer-header">
              <span class="disclaimer-icon">⚠️</span>
              <h3>免责声明与使用须知</h3>
            </div>
            
            <div class="disclaimer-content">
              <div class="disclaimer-section">
                <h4>评估性质说明</h4>
                <p>本报告基于多模态数据分析生成，其结论由AI模型提供，仅供参考和自我觉察，<strong>不能替代专业心理医生或精神科医师的诊断与治疗</strong>。</p>
                <p>本系统提供的评估结果基于现有数据和算法模型，可能存在误差，不应作为医疗决策的唯一依据。</p>
              </div>

              <div class="disclaimer-section">
                <h4>使用限制</h4>
                <p>心理健康状态是动态变化的，单次评估结果不能代表您的全部心理状况。如感不适，请务必寻求线下专业帮助。</p>
                <p>本报告不适用于以下情况：</p>
                <ul>
                  <li>急性心理危机或自杀倾向</li>
                  <li>严重精神疾病发作期</li>
                  <li>法律诉讼或司法鉴定需求</li>
                  <li>职业资格或入学评估</li>
                </ul>
              </div>

              <div class="disclaimer-section">
                <h4>数据安全与隐私</h4>
                <p>您所有的评估数据均被加密处理，我们承诺保护您的隐私安全。</p>
                <p>数据存储遵循《中华人民共和国个人信息保护法》等相关法律法规，评估数据仅用于改善服务质量，不会向第三方共享。</p>
              </div>

              <div class="disclaimer-section">
                <h4>用户责任</h4>
                <p>使用本服务即表示您已阅读、理解并同意：</p>
                <ul>
                  <li>您应对自身心理健康状况负责</li>
                  <li>如有需要，应及时寻求专业医疗帮助</li>
                  <li>不得将本报告用于非法目的</li>
                  <li>不得将评估结果作为医疗诊断依据</li>
                </ul>
              </div>

              <div class="disclaimer-section">
                <h4>紧急情况处理</h4>
                <p>如遇紧急心理危机，请立即：</p>
                <ol>
                  <li>拨打当地心理危机干预热线</li>
                  <li>前往最近的精神卫生中心或综合医院心理科</li>
                  <li>联系亲友或社区工作人员寻求支持</li>
                  <li>紧急情况下请拨打110或120</li>
                </ol>
              </div>
              
              <div class="disclaimer-footer">
                <div class="footer-left">
                  <span>最终解释权归 心镜·守望 所有</span>
                  <span>版本号: v1.0.1 (2026版)</span>
                </div>
                <div class="footer-right">
                  <span>评估时间: {{ evaluateTime }}</span>
                  <span>报告有效期: 30天</span>
                </div>
              </div>
            </div>
          </div>
        </section>

                <!-- 新增：全宽个性化建议卡片，作为 .report-content 的直接子元素 -->
        <div class="card suggestion-card full-width">
          <div class="card-header">
            <h3>个性化建议与指导</h3>
            <span class="score-badge" :class="getScoreClass(reportData.score)">
              {{ getScoreLevel(reportData.score).level }}水平方案
            </span>
          </div>
          
          <div class="suggestion-content">
            <div class="suggestion-grid-2col">
              <div 
                v-for="(suggestion, index) in reportData.suggestions" 
                :key="index"
                class="suggestion-item"
              >
                <span class="suggestion-number">{{ index + 1 }}</span>
                <span class="suggestion-text">{{ suggestion }}</span>
              </div>
            </div>
          </div>
        </div>
      <!-- 新增：全宽个性化建议卡片，作为 .report-content 的直接子元素
      <div class="card suggestion-card full-width">
        <div class="card-header">
          <h3>个性化建议与指导</h3>
          <span class="score-badge" :class="getScoreClass(reportData.score)">
            {{ getScoreLevel(reportData.score).level }}水平方案
          </span>
        </div>
        
        <div class="suggestion-content">
          <div class="suggestion-grid-2col">
            <div 
              v-for="(suggestion, index) in reportData.suggestions" 
              :key="index"
              class="suggestion-item"
            >
              <span class="suggestion-number">{{ index + 1 }}</span>
              <span class="suggestion-text">{{ suggestion }}</span>
            </div>
          </div>
        </div>
      </div> -->

      </main>

      <!-- 页脚 -->
      <footer class="report-footer">
        <div class="footer-content">
          <p class="copyright">© 2026 心镜·守望 · 心理健康评估系统 </p>
          <p class="disclaimer">本报告内容保密，仅限本人查阅，建议妥善保管。</p>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Chart, registerables } from 'chart.js'
import Loading from '@/components/Loading.vue'
import { generatePdfReport } from '@/utils/pdfExport.js'

// 注册Chart.js组件
Chart.register(...registerables)

// 路由相关
const route = useRoute()
const router = useRouter()

// 响应式状态
const loading = ref(true)
const exporting = ref(false)
const reportWrapper = ref(null)
const reportContent = ref(null)

// 报告ID和时间 - 更新为2026年
const reportId = ref(route.params.id || 'PSY-' + Date.now().toString().slice(-8))
const evaluateTime = ref('2026-04-04 21:11') // 根据截图设置具体时间

// 图表引用
const emotionChart = ref(null)
const waveChart = ref(null)
const chartInstances = []

// 情绪颜色和标签映射
const emotionLabels = {
  calm: '平静',
  happy: '愉悦',
  anxiety: '焦虑',
  tired: '疲惫',
  neutral: '中性'
}

const emotionColors = {
  calm: '#4ECDC4',
  happy: '#FFD700',
  anxiety: '#FF6B6B',
  tired: '#95A5A6',
  neutral: '#B2DFDB'
}



// 报告数据
const reportData = ref({
  prediction: '',
  confidence: 0.88,
  score: 72,
  contributions: { face: 40, audio: 30, hr: 30 },
  emotionRatio: { calm: 40, happy: 25, anxiety: 20, tired: 10, neutral: 5 },
  explanation: '评估显示您当前心理健康状况总体良好，情绪稳定性较好，社会支持网络健全。建议继续保持健康的生活习惯，并关注压力管理。',
  physiologicalMetrics: {
    avgHeartRate: 72,
    hrv: 45,
    sleepQuality: 7.2,
    activityLevel: 6500
  },
  riskAssessment: {
    depressionRisk: '低',
    anxietyRisk: '中',
    burnoutRisk: '低',
    overallRisk: '低'
  },
  suggestions: [
    '建立规律的作息时间，保证7-8小时睡眠',
    '每周进行3次中等强度运动，每次30分钟',
    '学习压力管理技巧，如深呼吸、正念冥想',
    '定期与亲友沟通，分享感受和压力',
    '每季度进行一次心理状态自我评估',
    '培养一项放松的爱好，如阅读或绘画',
    '注意饮食均衡，避免过度摄入咖啡因',
    '合理安排工作和休息，避免连续加班'
  ]
})

// 工具函数
const getScoreLevel = (score) => {
  if (score >= 80) return { level: '优秀', color: '#4ECDC4' }
  if (score >= 70) return { level: '良好', color: '#4ECDC4' }
  if (score >= 60) return { level: '中等', color: '#FFD700' }
  if (score >= 40) return { level: '需关注', color: '#FFA726' }
  return { level: '需干预', color: '#FF6B6B' }
}

const getEmotionRatio = (stress) => {
  // stress: 0 ~ 5
  let calm = Math.max(0, 50 - stress * 8)      // 50 -> 10
  let happy = Math.max(0, 30 - stress * 6)     // 30 -> 0
  let anxiety = Math.min(50, stress * 10)      // 0 -> 50
  let tired = Math.min(40, stress * 8)         // 0 -> 40
  let neutral = 100 - calm - happy - anxiety - tired
  
  // 归一化确保总和为100
  const total = calm + happy + anxiety + tired + neutral
  if (total !== 100) {
    const factor = 100 / total
    calm *= factor
    happy *= factor
    anxiety *= factor
    tired *= factor
    neutral *= factor
  }
  return {
    calm: Math.round(calm),
    happy: Math.round(happy),
    anxiety: Math.round(anxiety),
    tired: Math.round(tired),
    neutral: Math.round(neutral)
  }
}

const getPredictionLevel = (score) => {
  if (score >= 80) return '健康'
  if (score >= 60) return '轻度压力'
  if (score >= 40) return '中度压力'
  return '重度压力'
}

const getPredictionClass = (score) => {
  if (score >= 80) return 'prediction-healthy'
  if (score >= 60) return 'prediction-mild'
  if (score >= 40) return 'prediction-moderate'
  return 'prediction-severe'
}

const getScoreClass = (score, returnColor = false) => {
  if (score >= 80) return returnColor ? '#4ECDC4' : 'score-excellent'
  if (score >= 70) return returnColor ? '#4ECDC4' : 'score-good'
  if (score >= 60) return returnColor ? '#FFD700' : 'score-medium'
  if (score >= 40) return returnColor ? '#FFA726' : 'score-warning'
  return returnColor ? '#FF6B6B' : 'score-danger'
}

const getRiskClass = (risk) => {
  const riskMap = {
    '低': 'risk-low',
    '中': 'risk-medium', 
    '高': 'risk-high',
    '较低': 'risk-low',
    '较高': 'risk-high'
  }
  return riskMap[risk] || 'risk-low'
}

const getRiskLabel = (key) => {
  const labelMap = {
    depressionRisk: '抑郁风险',
    anxietyRisk: '焦虑风险', 
    burnoutRisk: '倦怠风险',
    overallRisk: '总体风险',
    stressLevel: '压力水平'
  }
  return labelMap[key] || key
}

const getRiskByScore = (score) => {
  if (score >= 70) {
    return {
      overallRisk: '低',
      depressionRisk: '低',
      anxietyRisk: '低',
      burnoutRisk: '低'
    }
  } else if (score >= 50) {
    return {
      overallRisk: '中',
      depressionRisk: '低',
      anxietyRisk: '中',
      burnoutRisk: '低'
    }
  } else {
    return {
      overallRisk: '高',
      depressionRisk: '中',
      anxietyRisk: '高',
      burnoutRisk: '中'
    }
  }
}

const getContributionLabel = (key) => {
  const labelMap = {
    face: '面部表情',
    audio: '语音情感',
    hr: '生理信号',
    behavior: '行为模式'
  }
  return labelMap[key] || key
}

const getContributionIcon = (key) => {
  const iconMap = {
    face: '😊',
    audio: '🎤',
    hr: '❤️',
    behavior: '👤'
  }
  return iconMap[key] || '📊'
}

// 打开链接
const openLink = (url) => {
  window.open(url, '_blank', 'noopener,noreferrer')
}

// 加载报告数据
// 加载报告数据
const loadReportData = async () => {
  loading.value = true
  try {
    const stored = localStorage.getItem('last_test_report')
    if (!stored) throw new Error('未找到测试数据，请先完成评估')
    

    const report = JSON.parse(stored)
    console.log('报告原始 JSON:', JSON.stringify(report, null, 2))

    // 1. 计算压缩压力指数（原始分数越高压力越低）
    const stress = ((100 - report.score) / 100) * 5
    const stressIndex = Math.round(stress * 10) / 10

    // 2. 动态生成情绪比例
    const getEmotionRatio = (stress) => {
      let calm = Math.max(0, 50 - stress * 8)
      let happy = Math.max(0, 30 - stress * 6)
      let anxiety = Math.min(50, stress * 10)
      let tired = Math.min(40, stress * 8)
      let neutral = 100 - calm - happy - anxiety - tired
      // 确保非负并归一化
      calm = Math.max(0, calm)
      happy = Math.max(0, happy)
      anxiety = Math.max(0, anxiety)
      tired = Math.max(0, tired)
      neutral = Math.max(0, neutral)
      const total = calm + happy + anxiety + tired + neutral
      if (total !== 100) {
        const factor = 100 / total
        calm *= factor
        happy *= factor
        anxiety *= factor
        tired *= factor
        neutral *= factor
      }
      return {
        calm: Math.round(calm),
        happy: Math.round(happy),
        anxiety: Math.round(anxiety),
        tired: Math.round(tired),
        neutral: Math.round(neutral)
      }
    }
    const emotionRatio = getEmotionRatio(stressIndex)

    // 3. 根据分数生成风险评估
    const getRiskByScore = (score) => {
      if (score >= 70) {
        return {
          overallRisk: '低',
          depressionRisk: '低',
          anxietyRisk: '低',
          burnoutRisk: '低'
        }
      } else if (score >= 40) {
        return {
          overallRisk: '中',
          depressionRisk: '低',
          anxietyRisk: '中',
          burnoutRisk: '低'
        }
      } else {
        return {
          overallRisk: '高',
          depressionRisk: '中',
          anxietyRisk: '高',
          burnoutRisk: '中'
        }
      }
    }
    const risk = getRiskByScore(report.score)

    // 4. 映射所有数据
    reportData.value = {
      prediction: report.prediction_class || getPredictionLevel(report.score),
      confidence: report.confidence,
      score: report.score,
      contributions: report.contributions,
      stressIndex: stressIndex,        // 压力指数 0-5
      stressLevel: stressIndex,                 // 独立压力指数
      emotionRatio: emotionRatio,               // 动态情绪比例
      explanation: report.explanation,
      physiologicalMetrics: {
        avgHeartRate: report.avgHeartRate ?? 72,
        hrv: report.hrv ?? 45,
        sleepQuality: report.sleepQuality ?? 7.5
      },
      riskAssessment: {
        depressionRisk: risk.depressionRisk,
        anxietyRisk: risk.anxietyRisk,
        burnoutRisk: risk.burnoutRisk,
        overallRisk: risk.overallRisk
      },
      suggestions: generateSuggestions(report.score)
    }

    await nextTick()
    initCharts()
  } catch (error) {
    console.error('加载报告失败:', error)
    reportData.value = getDefaultReportData()
  } finally {
    loading.value = false
  }
}

const generateSuggestions = (score) => {
  if (score >= 70) {
    return [
      '建立规律的作息时间，保证7-8小时睡眠',
      '每周进行3次中等强度运动，每次30分钟',
      '学习压力管理技巧，如深呼吸、正念冥想',
      '定期与亲友沟通，分享感受和压力',
      '每季度进行一次心理状态自我评估',
      '培养一项放松的爱好，如阅读或绘画',
      '注意饮食均衡，避免过度摄入咖啡因',
      '合理安排工作和休息，避免连续加班'
    ];
  }
  
  if (score >= 50) {
    return [
      '增加每日运动量，建议每周150分钟中等强度运动',
      '确保规律作息，固定睡眠和起床时间',
      '尝试每日10-15分钟的冥想或深呼吸练习',
      '减少咖啡因和糖分摄入，保持均衡饮食',
      '学习时间管理技巧，避免任务堆积',
      '定期进行户外活动，接触自然环境',
      '培养积极社交，与朋友保持联系',
      '设置合理的休息间隔，避免长时间工作'
    ];
  }
  
  return [
    '考虑咨询专业心理健康专家进行评估',
    '建立每日放松时间，进行深呼吸或冥想',
    '识别主要压力源并制定应对策略',
    '确保充足睡眠，创造良好的睡眠环境',
    '练习正念，关注当下感受而非担忧未来',
    '寻求社会支持，与信任的人分享感受',
    '避免通过酒精或不健康方式应对压力',
    '如有需要，考虑短期休假调整状态'
  ];
};


// 初始化图表
const initCharts = () => {
  // 清理旧图表
  chartInstances.forEach(chart => chart.destroy())
  chartInstances.length = 0

  // 1. 情绪环形图
  if (emotionChart.value && reportData.value.emotionRatio) {
    const ctx = emotionChart.value.getContext('2d')
    const chart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: Object.keys(reportData.value.emotionRatio).map(key => emotionLabels[key]),
        datasets: [{
          data: Object.values(reportData.value.emotionRatio),
          backgroundColor: Object.keys(reportData.value.emotionRatio).map(key => emotionColors[key] || '#B2DFDB'),
          borderWidth: 0,
          hoverOffset: 8
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '65%',
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (context) => `${context.label}: ${context.raw}%`
            }
          }
        }
      }
    })
    chartInstances.push(chart)
  }

  // 2. 心率波形图
  if (waveChart.value) {
    const ctx = waveChart.value.getContext('2d')
    const baseHR = 72
    const waveData = Array.from({ length: 50 }, (_, i) => 
      baseHR + Math.sin(i * 0.3) * 8 + Math.random() * 3
    )

    const chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: waveData.map((_, i) => ''),
        datasets: [{
          data: waveData,
          borderColor: '#4ECDC4',
          backgroundColor: 'rgba(78, 205, 196, 0.1)',
          tension: 0.4,
          pointRadius: 0,
          fill: true,
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { display: false },
          y: { 
            display: false,
            min: 60,
            max: 100
          }
        },
        plugins: {
          legend: { display: false },
          tooltip: { enabled: false }
        }
      }
    })
    chartInstances.push(chart)
  }
}

// 导出PDF
const exportToPdf = async () => {
  if (exporting.value) return
  
  exporting.value = true
  try {
    const userInfo = {
      name: '保密用户',
      testDate: evaluateTime.value
    }
    
    await generatePdfReport(reportData.value, userInfo, `心理评估报告_${reportId.value}`)
    
    setTimeout(() => {
      alert('专业报告已生成并开始下载！')
    }, 500)
    
  } catch (error) {
    console.error('导出PDF失败:', error)
    alert('导出失败，请稍后重试')
  } finally {
    exporting.value = false
  }
}

// 生命周期
onMounted(() => {
  loadReportData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  chartInstances.forEach(chart => chart.destroy())
  window.removeEventListener('resize', handleResize)
})

// 窗口调整大小处理
const handleResize = () => {
  chartInstances.forEach(chart => chart.resize())
}
</script>

<style scoped>
/* 自定义属性 - 浅青色水墨画主题 */
:root {
  --color-primary: #2A6F79; /* 深青瓷色 */
  --color-primary-light: #E0F2F1; /* 极浅青 */
  --color-primary-dark: #1A4A4F; /* 墨青色 */
  --color-secondary: #B2DFDB; /* 浅青灰 */
  --color-accent: #4ECDC4; /* 青绿色 */
  --color-warning: #FFA726; /* 琥珀色 */
  --color-danger: #FF6B6B; /* 浅朱红 */
  --color-text-primary: #1A4A4F;
  --color-text-secondary: #2A6F79;
  --color-text-light: #4A8A94;
  --color-bg-main: #F8FDFC;
  --color-bg-card: #FFFFFF;
  --color-bg-hover: #F0FAF9;
  --color-border: #B2DFDB;
  --color-border-light: #E0F2F1;
  --color-shadow: rgba(42, 111, 121, 0.1);
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 20px;
  --radius-full: 9999px;
  --shadow-sm: 0 2px 8px var(--color-shadow);
  --shadow-md: 0 4px 12px var(--color-shadow);
  --shadow-lg: 0 8px 24px var(--color-shadow);
  --shadow-xl: 0 12px 32px var(--color-shadow);
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 12px;
  --spacing-lg: 16px;
  --spacing-xl: 24px;
  --spacing-2xl: 32px;
  --transition-fast: 150ms ease;
  --transition-normal: 250ms ease;
  --transition-slow: 350ms ease;
  --font-family-main: 'Microsoft YaHei', 'PingFang SC', 'Hiragino Sans GB', sans-serif;
  --font-family-title: 'STKaiti', 'KaiTi', 'SimKai', serif;
  --font-family-mono: 'Consolas', 'Monaco', 'Courier New', monospace;
}

/* 容器样式 */
.report-container {
  min-height: 100vh;
  background: linear-gradient(135deg, 
    var(--color-primary-light) 0%,
    rgba(232, 244, 243, 0.98) 50%,
    rgba(248, 250, 252, 0.98) 100%
  );
  padding: 20px;
  font-family: var(--font-family-main);
  color: var(--color-text-primary);
  background-image: 
    radial-gradient(circle at 20% 80%, rgba(78, 205, 196, 0.05) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(42, 111, 121, 0.05) 0%, transparent 50%);
}

.report-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  background: var(--color-bg-card);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  overflow: hidden;
  position: relative;
  border: 1px solid var(--color-border);
}

/* 头部样式 */
.report-header {
  background: linear-gradient(135deg, var(--color-primary-dark), var(--color-primary));
  color: white;
  padding: var(--spacing-xl) var(--spacing-2xl);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--spacing-lg);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
}

.report-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(circle at 10% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 20%),
    radial-gradient(circle at 90% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 20%);
  pointer-events: none;
}

.header-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-2xl);
  position: relative;
  z-index: 1;
}

.header-brand {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.brand-title {
  font-family: var(--font-family-title);
  font-size: 3rem;
  font-weight: normal;
  letter-spacing: 2px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  margin: 0;
  line-height: 1.1;
  background: linear-gradient(45deg, #FFFFFF, #E0F2F1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-subtitle {
  font-size: 1rem;
  opacity: 0.9;
  letter-spacing: 1px;
  margin: 0;
  color: #B2DFDB;
}

.header-info {
  display: flex;
  gap: var(--spacing-xl);
  font-size: 0.9rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  opacity: 0.8;
  font-size: 0.85rem;
  color: #B2DFDB;
}

.info-value {
  font-weight: 500;
  font-family: var(--font-family-mono);
  color: white;
}

/* 导出按钮 */
.header-actions {
  display: flex;
  align-items: center;
  position: relative;
  z-index: 1;
}

.btn-export {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: 12px 24px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: var(--radius-lg);
  color: white;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-normal);
  min-width: 160px;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.btn-export::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left var(--transition-slow);
}

.btn-export:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.btn-export:hover:not(:disabled)::before {
  left: 100%;
}

.btn-export:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.btn-export.exporting {
  background: rgba(255, 255, 255, 0.1);
}

.btn-icon {
  font-size: 1.2rem;
}

.report-content {
  display: grid;
  grid-template-columns: 320px 1fr 380px; /* 当前是三列布局 */
  gap: var(--spacing-lg);
  padding: var(--spacing-lg);
  min-height: 600px;
  max-width: 1400px;
  margin: 0 auto;
}

/* 列布局 */
.left-column,
.center-column,
.right-column {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

/* 通用卡片样式 */
.card {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--color-border);
  transition: all var(--transition-normal);
  position: relative;
  overflow: hidden;
}

.card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--color-primary), var(--color-accent));
  opacity: 0;
  transition: opacity var(--transition-normal);
}

.card:hover::before {
  opacity: 1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-sm);
  border-bottom: 2px solid var(--color-border-light);
  position: relative;
}

.card-header h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--color-primary-dark);
  margin: 0;
  position: relative;
  padding-left: var(--spacing-md);
}

.card-header h3::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 16px;
  background: var(--color-primary);
  border-radius: var(--radius-sm);
}

.card-subtitle {
  font-size: 0.875rem;
  color: var(--color-text-light);
  font-weight: 400;
}

/* 左侧列样式 */
/* 个人信息卡片 */
.profile-card {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.profile-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: var(--spacing-md);
}

.avatar-container {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  width: 100%;
}

.avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  padding: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(42, 111, 121, 0.2);
}

.avatar img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: white;
  border: 3px solid white;
}

.profile-info {
  flex: 1;
  text-align: left;
}

.profile-info h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-xs) 0;
}

.user-id {
  font-size: 0.875rem;
  color: var(--color-text-light);
  font-family: var(--font-family-mono);
}

/* 综合评分 */
.overall-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background: var(--color-bg-main);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  position: relative;
  overflow: hidden;
}

.overall-score::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--color-primary), var(--color-accent));
}

.score-display {
  text-align: center;
}

.score-number {
  font-size: 3rem;
  font-weight: bold;
  margin-bottom: var(--spacing-xs);
  font-family: var(--font-family-mono);
  line-height: 1;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.score-excellent { color: var(--color-accent); }
.score-good { color: var(--color-accent); }
.score-medium { color: #FFD700; }
.score-warning { color: var(--color-warning); }
.score-danger { color: var(--color-danger); }

.score-label {
  font-size: 0.875rem;
  color: var(--color-text-light);
  font-weight: 500;
}

.score-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
  width: 100%;
}

.detail-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: var(--spacing-sm);
  background: white;
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border-light);
}

.detail-label {
  font-size: 0.75rem;
  color: var(--color-text-light);
  margin-bottom: 4px;
}

.detail-value {
  font-size: 1rem;
  font-weight: 600;
  font-family: var(--font-family-mono);
}

/* 贡献度分析 */
.contribution-card {
  margin-top: 0;
  display: flex;
  flex-direction: column;
}

.contributions-horizontal {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.contribution-item-h {
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-light);
  transition: all var(--transition-normal);
  background: var(--color-bg-main);
}

.contribution-item-h:hover {
  background: var(--color-bg-hover);
  border-color: var(--color-primary);
  transform: translateX(4px);
}

.contrib-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.contrib-icon {
  font-size: 1.5rem;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(78, 205, 196, 0.1);
  border-radius: 50%;
  border: 2px solid rgba(78, 205, 196, 0.3);
}

.contrib-label {
  font-weight: 600;
  color: var(--color-text-primary);
  flex: 1;
}

.contrib-details {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.contrib-bar {
  flex: 1;
  height: 8px;
  background: var(--color-border);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.contrib-fill {
  height: 100%;
  border-radius: var(--radius-full);
  background: linear-gradient(90deg, var(--color-primary), var(--color-accent));
  transition: width var(--transition-slow) ease-out;
  box-shadow: 0 2px 4px rgba(78, 205, 196, 0.3);
}

.contrib-value {
  min-width: 60px;
  text-align: right;
}

.value-number {
  font-size: 1.1rem;
  font-weight: 600;
  font-family: var(--font-family-mono);
  color: var(--color-primary-dark);
}

/* 对测评者的话 */
.message-card {
  border: 2px solid var(--color-accent);
  background: linear-gradient(135deg, rgba(224, 242, 241, 0.1), rgba(255, 255, 255, 0.9));
  margin-top: var(--spacing-lg);
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 750px;
  max-height: 850px;
  padding: 0;
}

.message-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-lg);
  padding-bottom: var(--spacing-sm);
  border-bottom: 2px solid var(--color-border);
}

.message-icon {
  font-size: 2rem;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(78, 205, 196, 0.2);
  border-radius: 50%;
  border: 2px solid rgba(78, 205, 196, 0.4);
}

.message-header h3 {
  font-size: 1.3rem;
  color: var(--color-primary-dark);
  margin: 0;
}

.message-content {
  color: var(--color-text-primary);
  line-height: 1.7;
  font-size: 0.95rem;
  flex: 1;
  padding: 0 var(--spacing-lg) var(--spacing-lg) var(--spacing-lg);
}

.message-content p {
  margin: var(--spacing-md) 0;
  text-align: justify;
}

.message-content ul {
  margin: var(--spacing-md) 0;
  padding-left: var(--spacing-xl);
}

.message-content li {
  margin: var(--spacing-xs) 0;
  position: relative;
}

.message-content li::before {
  content: '•';
  color: var(--color-accent);
  font-weight: bold;
  position: absolute;
  left: -1em;
}

.signature {
  text-align: right;
  margin-top: var(--spacing-xl);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border);
  font-style: italic;
  color: var(--color-text-light);
}

.signature p {
  margin: 4px 0;
}

.signature .date {
  font-size: 0.9rem;
  color: var(--color-text-light);
}

/* 中间列样式 */
/* AI评估结论 */
.conclusion-card {
  position: relative;
  overflow: hidden;
}

.prediction-display {
  padding: 1.8rem;
  border-radius: var(--radius-lg);
  text-align: center;
  color: white;
  margin: 1.2rem 0;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(42, 111, 121, 0.3);
}

.prediction-display::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(circle at 20% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 40%),
    radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 40%);
}

.prediction-healthy { 
  background: linear-gradient(135deg, #4ECDC4, #2A6F79);
  box-shadow: 0 8px 32px rgba(78, 205, 196, 0.3);
}
.prediction-mild { 
  background: linear-gradient(135deg, #FFD700, #D4A017);
  box-shadow: 0 8px 32px rgba(255, 215, 0, 0.3);
}
.prediction-moderate { 
  background: linear-gradient(135deg, #FFA726, #D2691E);
  box-shadow: 0 8px 32px rgba(255, 167, 38, 0.3);
}
.prediction-severe { 
  background: linear-gradient(135deg, #FF6B6B, #8B0000);
  box-shadow: 0 8px 32px rgba(255, 107, 107, 0.3);
}

.prediction-title {
  font-size: 1.1rem;
  opacity: 0.9;
  margin-bottom: 0.5rem;
  position: relative;
  z-index: 1;
}

.prediction-value {
  font-size: 2.8rem;
  font-weight: bold;
  margin: 0.5rem 0;
  position: relative;
  z-index: 1;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.prediction-score {
  font-size: 1.2rem;
  opacity: 0.9;
  margin-top: 1rem;
  position: relative;
  z-index: 1;
}

.prediction-score span {
  font-weight: bold;
  font-family: var(--font-family-mono);
  font-size: 1.4rem;
}

.explanation-text {
  font-size: 0.95rem;
  line-height: 1.7;
  color: var(--color-text-primary);
  padding: var(--spacing-lg);
  background: var(--color-bg-main);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  margin-top: var(--spacing-lg);
}

/* 情绪分布图 */
.emotion-card {
  margin-top: var(--spacing-lg);
}

.chart-container {
  display: flex;
  align-items: center;
  gap: var(--spacing-xl);
  margin-bottom: var(--spacing-lg);
}

.chart-wrapper {
  position: relative;
  height: 180px;
  width: 180px;
  flex-shrink: 0;
}

.emotion-chart {
  width: 100% !important;
  height: 100% !important;
}

.emotion-legend {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background: var(--color-bg-main);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: 0.9rem;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.legend-label {
  flex: 1;
  color: var(--color-text-primary);
  font-weight: 500;
}

.legend-value {
  font-weight: 600;
  font-family: var(--font-family-mono);
  color: var(--color-primary-dark);
  min-width: 40px;
  text-align: right;
}

/* 生理指标趋势 */
.hrv-card {
  margin-top: var(--spacing-lg);
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 363px;
  max-height: 413px;
}

.hrv-chart-wrapper {
  position: relative;
  height: 150px;
  width: 100%;
  margin-bottom: var(--spacing-lg);
}

.wave-chart {
  width: 100% !important;
  height: 100% !important;
}

.hrv-metrics {
  display: flex;
  justify-content: space-around;
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border);
}

.hrv-metric {
  text-align: center;
  padding: var(--spacing-sm);
  background: var(--color-bg-main);
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border-light);
  flex: 1;
  margin: 0 var(--spacing-xs);
}

.hrv-metric .metric-value {
  font-size: 1.5rem;
  font-weight: bold;
  display: block;
  margin-bottom: var(--spacing-xs);
  font-family: var(--font-family-mono);
  color: var(--color-primary-dark);
}

.hrv-metric .metric-value.positive {
  color: var(--color-accent);
}

.hrv-metric .metric-label {
  font-size: 0.875rem;
  color: var(--color-text-light);
}

/* 心理健康风险评估 */
.risk-card {
  margin-top: var(--spacing-lg);
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 363px;
  max-height: 413px;
}

.risk-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
}

.risk-item {
  padding: var(--spacing-lg);
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  border: 1px solid var(--color-border);
  transition: all var(--transition-normal);
  background: white;
  min-height: 80px;
  justify-content: center;
}

.risk-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.risk-low {
  background: rgba(78, 205, 196, 0.1);
  border-color: rgba(78, 205, 196, 0.3);
}

.risk-medium {
  background: rgba(255, 167, 38, 0.1);
  border-color: rgba(255, 167, 38, 0.3);
}

.risk-high {
  background: rgba(255, 107, 107, 0.1);
  border-color: rgba(255, 107, 107, 0.3);
}

.risk-label {
  font-size: 0.9rem;
  color: var(--color-text-light);
  margin-bottom: var(--spacing-xs);
  font-weight: 500;
}

.risk-value {
  font-size: 1.3rem;
  font-weight: bold;
  font-family: var(--font-family-mono);
}

.risk-low .risk-value { color: var(--color-accent); }
.risk-medium .risk-value { color: var(--color-warning); }
.risk-high .risk-value { color: var(--color-danger); }

.suggestion-card {
  border-color: var(--color-accent);
  border-width: 2px;
  margin-top: var(--spacing-lg);
  /* 新增/修改以下代码以实现全宽 */
  grid-column: 1 / -1; /* 横跨所有列 */
  width: calc(100% + 2 * var(--spacing-lg)); /* 宽度补偿内边距 */
  margin-left: calc(-1 * var(--spacing-lg)); /* 向左扩展以消除左留白 */
  margin-right: calc(-1 * var(--spacing-lg)); /* 向右扩展以消除右留白 */
  position: relative; /* 确保定位正确 */
  z-index: 1; /* 确保在正确层级 */
  border-radius: 0 var(--radius-lg) var(--radius-lg) 0; /* 调整圆角：左上、左下为0 */
}

.suggestion-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.suggestion-grid-2col {
  display: grid;
  grid-template-columns: repeat(2, 1fr); /* 改为3列布局 */
  grid-template-rows: auto; /* 行数改为自动适应，可选项 */
  gap: var(--spacing-md);
}

.suggestion-item {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background: var(--color-bg-main);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  transition: all var(--transition-normal);
  min-height: 100px;
}

.suggestion-item:hover {
  background: var(--color-bg-hover);
  border-color: var(--color-primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.suggestion-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: var(--color-primary);
  color: white;
  border-radius: 50%;
  font-size: 0.85rem;
  font-weight: bold;
  flex-shrink: 0;
  margin-top: 2px;
  box-shadow: 0 4px 8px rgba(42, 111, 121, 0.2);
}

.suggestion-text {
  flex: 1;
  font-size: 0.95rem;
  line-height: 1.5;
  color: var(--color-text-primary);
  font-weight: 500;
}

/* 右侧列样式 */
.right-column {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  width: 380px;
}

/* 心理健康援助资源 */
.resource-card {
  border-color: #4ECDC4;
  border-width: 2px;
  display: flex;
  flex-direction: column;
  height: auto;
  min-height: 750px;
  max-height: 850px;
  overflow-y: auto;
}

.resource-card::-webkit-scrollbar {
  width: 6px;
}

.resource-card::-webkit-scrollbar-track {
  background: var(--color-bg-main);
  border-radius: 3px;
}

.resource-card::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 3px;
}

.resource-links-vertical {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  flex: 1;
}

.resource-link {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  background: var(--color-bg-main);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  text-decoration: none;
  color: var(--color-text-primary);
  transition: all var(--transition-normal);
  cursor: pointer;
  min-height: 90px;
}

.resource-link:hover {
  background: var(--color-bg-hover);
  border-color: var(--color-primary);
  transform: translateX(4px);
  text-decoration: none;
  color: var(--color-primary-dark);
  box-shadow: var(--shadow-sm);
}

.link-icon {
  font-size: 2rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(78, 205, 196, 0.1);
  border-radius: 50%;
  flex-shrink: 0;
  border: 2px solid rgba(78, 205, 196, 0.3);
}

.link-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.link-content strong {
  font-weight: 600;
  color: var(--color-primary-dark);
  font-size: 1.1rem;
}

.link-content p {
  font-size: 0.85rem;
  color: var(--color-text-light);
  margin: 0;
  line-height: 1.4;
}

/* 热线服务 */
.hotline-section {
  margin-top: var(--spacing-lg);
  padding-top: var(--spacing-md);
  border-top: 2px solid var(--color-border-light);
}

.hotline-section h4 {
  font-size: 1.1rem;
  color: var(--color-primary-dark);
  margin-bottom: var(--spacing-md);
  padding-left: var(--spacing-sm);
  border-left: 4px solid var(--color-accent);
}

.hotline-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  background: var(--color-bg-main);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  border: 1px solid var(--color-border);
}

.hotline-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-md);
  background: white;
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border-light);
  transition: all var(--transition-normal);
}

.hotline-item:hover {
  background: var(--color-bg-hover);
  border-color: var(--color-primary);
}

.hotline-name {
  font-size: 0.9rem;
  color: var(--color-text-primary);
  font-weight: 500;
  flex: 1;
}

.hotline-number {
  font-size: 1rem;
  font-weight: bold;
  color: var(--color-primary-dark);
  font-family: var(--font-family-mono);
  margin: 0 var(--spacing-md);
}

.hotline-desc {
  font-size: 0.8rem;
  color: var(--color-text-light);
  background: rgba(78, 205, 196, 0.1);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  border: 1px solid rgba(78, 205, 196, 0.3);
}

/* 在线平台 */
.online-platforms {
  margin-top: var(--spacing-lg);
  padding-top: var(--spacing-md);
  border-top: 2px solid var(--color-border-light);
}

.online-platforms h4 {
  font-size: 1.1rem;
  color: var(--color-primary-dark);
  margin-bottom: var(--spacing-md);
  padding-left: var(--spacing-sm);
  border-left: 4px solid var(--color-accent);
}

.platform-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-sm);
  background: var(--color-bg-main);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  border: 1px solid var(--color-border);
}

.platform-link {
  display: block;
  text-align: center;
  padding: var(--spacing-md);
  background: white;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  text-decoration: none;
  color: var(--color-primary-dark);
  font-weight: 500;
  transition: all var(--transition-normal);
  font-size: 0.9rem;
}

.platform-link:hover {
  background: var(--color-primary);
  color: white;
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
  border-color: var(--color-primary);
}

.disclaimer-card {
  background: linear-gradient(135deg, #FFF9C4, #FFECB3);
  border: 2px solid #FFD54F;
  border-left: 6px solid #FFA726;
  margin-top: var(--spacing-lg);
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 750px;
  max-height: 850px;
  overflow-y: auto;
  padding: 0;
}

.disclaimer-card::-webkit-scrollbar {
  width: 6px;
}

.disclaimer-card::-webkit-scrollbar-track {
  background: rgba(255, 213, 79, 0.1);
  border-radius: 3px;
}

.disclaimer-card::-webkit-scrollbar-thumb {
  background: rgba(255, 167, 38, 0.5);
  border-radius: 3px;
}

.disclaimer-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
  padding: var(--spacing-md) 0;
  border-bottom: 2px solid rgba(255, 167, 38, 0.3);
  position: sticky;
  top: 0;
  background: linear-gradient(135deg, #FFF9C4, #FFECB3);
  z-index: 10;
}

.disclaimer-icon {
  font-size: 2rem;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 167, 38, 0.2);
  border-radius: 50%;
  border: 2px solid rgba(255, 167, 38, 0.4);
}

.disclaimer-header h3 {
  color: #F57C00;
  margin: 0;
  font-size: 1.4rem;
  font-weight: 600;
}

.disclaimer-content {
  color: #5D4037;
  font-size: 0.85rem;
  line-height: 1.6;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  padding: var(--spacing-md);
}

.disclaimer-section {
  padding: var(--spacing-md);
  background: rgba(255, 255, 255, 0.5);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 167, 38, 0.3);
}

/* 个性化建议卡片样式 */
.suggestion-card {
  grid-column: 1 / -1;
  background: linear-gradient(135deg, #E8F5E9, #F1F8E9);
  border: 2px solid #81C784;
  border-left: 6px solid #4CAF50;
  margin-bottom: var(--spacing-lg);
}

.suggestion-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: var(--spacing-md);
  border-bottom: 2px solid rgba(76, 175, 80, 0.3);
  margin-bottom: var(--spacing-md);
}

.suggestion-card h3 {
  color: #2E7D32;
  font-size: 1.3rem;
  margin: 0;
}

.score-badge {
  display: inline-block;
  padding: 6px 16px;
  border-radius: var(--radius-full);
  font-size: 0.85rem;
  font-weight: 600;
  color: white;
}

.score-badge.score-excellent,
.score-badge.score-good {
  background: linear-gradient(135deg, #4ECDC4, #45B7AA);
}

.score-badge.score-medium {
  background: linear-gradient(135deg, #FFD700, #FFC700);
  color: #333;
}

.score-badge.score-warning {
  background: linear-gradient(135deg, #FFA726, #FB8C00);
}

.score-badge.score-danger {
  background: linear-gradient(135deg, #FF6B6B, #FF5252);
}

.suggestion-content {
  padding: var(--spacing-md) 0;
}

.suggestion-grid-2col {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-md);
}

.suggestion-item {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background: rgba(255, 255, 255, 0.6);
  border-radius: var(--radius-md);
  border-left: 4px solid #4CAF50;
  transition: all var(--transition-normal);
}

.suggestion-item:hover {
  background: rgba(255, 255, 255, 0.9);
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.2);
}

.suggestion-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4CAF50, #388E3C);
  color: white;
  font-weight: 600;
  font-size: 0.95rem;
  flex-shrink: 0;
}

.suggestion-text {
  color: #2E7D32;
  line-height: 1.6;
  font-size: 0.95rem;
}

@media (max-width: 1200px) {
  .suggestion-grid-2col {
    grid-template-columns: 1fr;
  }
}

.disclaimer-section h4 {
  color: #D84315;
  font-size: 1rem;
  margin-bottom: var(--spacing-md);
  padding-bottom: var(--spacing-xs);
  border-bottom: 1px solid rgba(255, 167, 38, 0.3);
}

.disclaimer-section p {
  margin: var(--spacing-sm) 0;
  text-align: justify;
}

.disclaimer-section ul,
.disclaimer-section ol {
  margin: var(--spacing-sm) 0;
  padding-left: var(--spacing-xl);
}

.disclaimer-section li {
  margin: var(--spacing-xs) 0;
  position: relative;
}

.disclaimer-section ul li::before {
  content: '•';
  color: #FFA726;
  font-weight: bold;
  position: absolute;
  left: -1em;
}

.disclaimer-section ol {
  list-style-type: decimal;
}

.disclaimer-section ol li {
  padding-left: var(--spacing-xs);
}

.disclaimer-content strong {
  color: #D84315;
  font-weight: 600;
}

.disclaimer-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  margin-top: var(--spacing-xl);
  padding-top: var(--spacing-lg);
  border-top: 2px solid rgba(255, 167, 38, 0.3);
  font-size: 0.8rem;
  color: #8D6E63;
  gap: var(--spacing-md);
}

.disclaimer-footer .footer-left,
.disclaimer-footer .footer-right {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  min-width: 150px;
}

.disclaimer-footer span {
  display: block;
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: var(--radius-sm);
  border: 1px solid rgba(255, 167, 38, 0.3);
  font-family: var(--font-family-mono);
}

/* 页脚 */
.report-footer {
  padding: var(--spacing-lg) var(--spacing-2xl);
  border-top: 1px solid var(--color-border);
  background: var(--color-bg-main);
  text-align: center;
  grid-column: 1 / -1;
  margin-top: var(--spacing-lg);
}

.footer-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.copyright {
  font-size: 0.9rem;
  color: var(--color-text-light);
  margin: 0;
  font-weight: 500;
}

.disclaimer {
  font-size: 0.8rem;
  color: var(--color-text-light);
  margin: 0;
  font-style: italic;
  line-height: 1.4;
}

/* 置信度徽章 */
.confidence-badge {
  font-size: 0.875rem;
  color: var(--color-text-light);
  background: var(--color-bg-main);
  padding: 6px 14px;
  border-radius: var(--radius-full);
  border: 1px solid var(--color-border);
  font-family: var(--font-family-mono);
  white-space: nowrap;
  font-weight: 500;
}

/* 分数徽章 */
.score-badge {
  display: inline-block;
  padding: 6px 16px;
  border-radius: var(--radius-full);
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: rgba(78, 205, 196, 0.1);
  color: var(--color-primary-dark);
  border: 1px solid rgba(78, 205, 196, 0.3);
  white-space: nowrap;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .report-content {
     max-width: 100%; /* 移除固定宽度限制 */
  padding: var(--spacing-lg) 0; /* 只保留上下内边距 */
  }
  
  .chart-container {
    flex-direction: column;
    align-items: stretch;
  }
  
  .chart-wrapper {
    width: 100%;
    height: 200px;
  }
  
  .emotion-legend {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .brand-title {
    font-size: 2.5rem;
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-md);
  }
  
  .header-info {
    flex-direction: column;
    gap: var(--spacing-sm);
  }
  
  .hrv-metrics {
    flex-direction: column;
    gap: var(--spacing-md);
  }
  
  .risk-grid {
    grid-template-columns: 1fr;
  }
  
  .suggestion-grid-2col {
    grid-template-columns: 1fr;
    grid-template-rows: auto;
  }
  
  .right-column {
    width: 100%;
  }
  
  .disclaimer-footer {
    flex-direction: column;
    align-items: stretch;
    gap: var(--spacing-md);
  }
  
  .disclaimer-footer .footer-left,
  .disclaimer-footer .footer-right {
    min-width: 100%;
  }
}

@media (max-width: 768px) {
  .report-container {
    padding: var(--spacing-sm);
  }
  
  .report-wrapper {
    border-radius: var(--radius-lg);
  }
  
  .report-header {
    padding: var(--spacing-lg);
    flex-direction: column;
    align-items: stretch;
    gap: var(--spacing-lg);
  }
  
  .header-actions {
    width: 100%;
  }
  
  .btn-export {
    width: 100%;
  }
  
  .brand-title {
    font-size: 2rem;
  }
  
  .report-content {
    padding: var(--spacing-md);
    gap: var(--spacing-md);
  }
  
  .card {
    padding: var(--spacing-md);
  }
  
  .chart-wrapper {
    height: 180px;
  }
  
  .hrv-chart-wrapper {
    height: 140px;
  }
  
  .prediction-value {
    font-size: 2.2rem;
  }
  
  .prediction-score span {
    font-size: 1.2rem;
  }
  
  .suggestion-item {
    min-height: 90px;
  }
  
  .platform-list {
    grid-template-columns: 1fr;
  }
  
  .resource-link {
    min-height: 80px;
    padding: var(--spacing-md);
  }
  
  .link-icon {
    width: 50px;
    height: 50px;
    font-size: 1.8rem;
  }
  
  .link-content strong {
    font-size: 1rem;
  }
}
</style>