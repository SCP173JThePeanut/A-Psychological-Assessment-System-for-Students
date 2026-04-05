// src/api/mentalHealth.js - 模拟数据版本
import { ref } from 'vue'

// 本地存储模拟数据
const mockTests = ref([])
const mockSessions = ref({})

// 从本地存储加载数据
const loadFromStorage = () => {
  const saved = localStorage.getItem('mock_mental_health_data')
  if (saved) {
    const data = JSON.parse(saved)
    mockTests.value = data.tests || []
    mockSessions.value = data.sessions || {}
  }
}

// 保存到本地存储
const saveToStorage = () => {
  const data = {
    tests: mockTests.value,
    sessions: mockSessions.value,
    lastUpdated: new Date().toISOString()
  }
  localStorage.setItem('mock_mental_health_data', JSON.stringify(data))
}

// 模拟网络延迟
const simulateNetworkDelay = () => {
  return new Promise(resolve => setTimeout(resolve, 300 + Math.random() * 700))
}

// 模拟成功响应
const mockSuccessResponse = (data = null) => ({
  success: true,
  data,
  timestamp: new Date().toISOString()
})

// 模拟API接口
export const mentalHealthAPI = {
  // 启动测试 - 模拟版本
  startTest: async (data) => {
    await simulateNetworkDelay()
    
    const sessionId = `mock_session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    
    mockSessions.value[sessionId] = {
      sessionId,
      userId: data?.user_id || 'anonymous',
      startedAt: new Date().toISOString(),
      status: 'active',
      questions: [],
      metadata: data
    }
    
    saveToStorage()
    
    console.log('✅ 模拟：启动测试会话', sessionId)
    return mockSuccessResponse({ sessionId })
  },
  
  // 提交问题回答 - 模拟版本
  submitQuestionAnswer: async (data) => {
    await simulateNetworkDelay()
    
    const { sessionId, questionId, answer } = data
    const session = mockSessions.value[sessionId]
    
    if (session) {
      if (!session.questions) session.questions = []
      session.questions.push({
        questionId,
        answer,
        timestamp: new Date().toISOString(),
        status: 'answered'
      })
      
      saveToStorage()
    }
    
    console.log('✅ 模拟：提交问题回答', { sessionId, questionId })
    return mockSuccessResponse({ saved: true })
  },
  
  // 上传音频数据 - 模拟版本
  submitAudio: async (formData) => {
    await simulateNetworkDelay()
    
    const sessionId = formData.get('sessionId')
    const questionId = formData.get('questionId')
    
    console.log('✅ 模拟：上传音频数据', { sessionId, questionId })
    
    return mockSuccessResponse({
      audioId: `audio_${Date.now()}`,
      size: 1024 * 1024, // 模拟1MB
      duration: 45, // 模拟45秒
      uploadedAt: new Date().toISOString()
    })
  },
  
  // 上传视频帧 - 模拟版本
  submitVideoFrame: async (formData) => {
    await simulateNetworkDelay()
    
    const sessionId = formData.get('sessionId')
    
    console.log('✅ 模拟：上传视频帧', { sessionId })
    
    return mockSuccessResponse({
      frameId: `frame_${Date.now()}`,
      features: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
      timestamp: new Date().toISOString()
    })
  },
  
  // 获取测试结果 - 模拟版本
  getTestResults: async (testId) => {
    await simulateNetworkDelay()
    
    // 生成模拟分析结果
    const mockResult = {
      testId,
      overallScore: 75 + Math.random() * 20,
      prediction: ['正常', '轻度压力', '中度压力', '高度压力'][Math.floor(Math.random() * 4)],
      confidence: 0.7 + Math.random() * 0.3,
      components: {
        voice: {
          score: 70 + Math.random() * 20,
          analysis: ['语调平稳', '语速适中', '表达清晰'][Math.floor(Math.random() * 3)]
        },
        face: {
          score: 80 + Math.random() * 15,
          analysis: ['表情自然', '眼神交流正常', '面部肌肉放松'][Math.floor(Math.random() * 3)]
        },
        heart: {
          score: 75 + Math.random() * 20,
          analysis: ['心率稳定', '变异度正常'][Math.floor(Math.random() * 2)]
        }
      },
      recommendations: [
        '保持规律的作息时间',
        '适当进行户外运动',
        '与朋友家人多交流',
        '尝试冥想或深呼吸练习'
      ],
      generatedAt: new Date().toISOString()
    }
    
    console.log('✅ 模拟：获取测试结果', { testId })
    return mockSuccessResponse(mockResult)
  },
  
  // 获取分析报告 - 模拟版本
  getAnalysisReport: async (testId) => {
    await simulateNetworkDelay()
    
    const mockReport = {
      testId,
      title: '心理健康评估报告',
      summary: '根据多模态数据分析，您的心理状态整体良好，但存在一定的压力积累。',
      details: {
        emotionalState: {
          status: '稳定',
          description: '情绪表达自然，情感反应适度。'
        },
        stressLevel: {
          level: 3,
          description: '中等压力水平，需要适当放松。'
        },
        copingAbility: {
          score: 7.5,
          description: '应对能力良好，有一定自我调节能力。'
        }
      },
      suggestions: [
        { type: '运动', suggestion: '每周进行3-5次中等强度运动' },
        { type: '社交', suggestion: '每周与朋友交流2-3次' },
        { type: '休息', suggestion: '保证每天7-8小时睡眠' }
      ],
      generatedAt: new Date().toISOString()
    }
    
    console.log('✅ 模拟：获取分析报告', { testId })
    return mockSuccessResponse(mockReport)
  },
  
  // 调用模型API - 模拟版本
  predictMentalHealth: async (features) => {
    await simulateNetworkDelay()
    
    const mockPrediction = {
      prediction: Math.random() > 0.7 ? '需要关注' : '状态良好',
      confidence: 0.6 + Math.random() * 0.3,
      features: {
        voice: features.voice_features || [],
        face: features.face_features || [],
        heart: features.heart_features || []
      },
      analysis: {
        voice: ['平静', '略有紧张', '自然'][Math.floor(Math.random() * 3)],
        face: ['放松', '专注', '略有疲惫'][Math.floor(Math.random() * 3)],
        heart: ['稳定', '轻微波动'][Math.floor(Math.random() * 2)]
      }
    }
    
    console.log('✅ 模拟：模型预测', mockPrediction)
    return mockSuccessResponse(mockPrediction)
  },
  
  // 新增：获取所有模拟数据
  getMockData: () => {
    return {
      tests: mockTests.value,
      sessions: mockSessions.value
    }
  },
  
  // 新增：清除模拟数据
  clearMockData: () => {
    mockTests.value = []
    mockSessions.value = {}
    localStorage.removeItem('mock_mental_health_data')
    return mockSuccessResponse({ cleared: true })
  }
}

// 初始化时加载数据
loadFromStorage()

export default mentalHealthAPI