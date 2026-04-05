// src/api/websocket.js - 模拟WebSocket版本
export class MockWebSocketService {
  constructor(url) {
    this.url = url
    this.mockConnected = false
    this.messageHandlers = []
    this.openHandlers = []
    this.closeHandlers = []
    this.errorHandlers = []
    this.messageQueue = []
    this.intervalId = null
    
    console.log('🔧 使用模拟WebSocket服务')
  }
  
  connect() {
    console.log('🔄 模拟WebSocket连接中...', this.url)
    
    // 模拟连接延迟
    setTimeout(() => {
      this.mockConnected = true
      console.log('✅ 模拟WebSocket连接成功')
      
      // 触发连接成功回调
      this.openHandlers.forEach(callback => callback())
      
      // 开始模拟接收消息
      this.startMockMessaging()
    }, 1000)
  }
  
  startMockMessaging() {
    if (this.intervalId) clearInterval(this.intervalId)
    
    this.intervalId = setInterval(() => {
      if (!this.mockConnected) {
        clearInterval(this.intervalId)
        return
      }
      
      // 随机发送模拟消息
      if (Math.random() > 0.7) {
        this.sendMockMessage()
      }
    }, 3000)
  }
  
  sendMockMessage() {
    const messageTypes = [
      {
        type: 'analysis_update',
        data: {
          emotion: ['平静', '专注', '思考', '放松'][Math.floor(Math.random() * 4)],
          confidence: 0.7 + Math.random() * 0.3,
          timestamp: new Date().toISOString()
        }
      },
      {
        type: 'data_quality',
        data: {
          audio: 80 + Math.random() * 20,
          video: 85 + Math.random() * 15,
          overall: 90 + Math.random() * 10
        }
      },
      {
        type: 'progress_update',
        data: {
          progress: Math.floor(Math.random() * 100),
          currentQuestion: Math.floor(Math.random() * 5) + 1,
          totalQuestions: 5
        }
      }
    ]
    
    const message = messageTypes[Math.floor(Math.random() * messageTypes.length)]
    this.receiveMockMessage(message)
  }
  
  receiveMockMessage(message) {
    this.messageHandlers.forEach(callback => {
      try {
        callback(message)
      } catch (error) {
        console.error('处理模拟消息失败:', error)
      }
    })
  }
  
  send(data) {
    if (!this.mockConnected) {
      console.warn('⚠️ 模拟WebSocket未连接，消息存入队列:', data)
      this.messageQueue.push(data)
      return
    }
    
    console.log('📤 模拟WebSocket发送消息:', data)
    
    // 模拟服务器响应
    setTimeout(() => {
      this.receiveMockMessage({
        type: 'acknowledgment',
        data: {
          received: true,
          timestamp: new Date().toISOString(),
          original: data
        }
      })
    }, 200)
  }
  
  onMessage(callback) {
    this.messageHandlers.push(callback)
  }
  
  onOpen(callback) {
    this.openHandlers.push(callback)
  }
  
  onClose(callback) {
    this.closeHandlers.push(callback)
  }
  
  onError(callback) {
    this.errorHandlers.push(callback)
  }
  
  reconnect() {
    console.log('🔄 模拟WebSocket重连中...')
    setTimeout(() => {
      this.mockConnected = true
      this.openHandlers.forEach(callback => callback())
      console.log('✅ 模拟WebSocket重连成功')
    }, 2000)
  }
  
  close() {
    this.mockConnected = false
    if (this.intervalId) clearInterval(this.intervalId)
    this.closeHandlers.forEach(callback => callback())
    console.log('🔌 模拟WebSocket已关闭')
  }
  
  // 添加模拟错误
  simulateError() {
    this.errorHandlers.forEach(callback => callback(new Error('模拟WebSocket错误')))
  }
  
  // 手动发送模拟消息
  simulateMessage(type, data) {
    this.receiveMockMessage({ type, data })
  }
}

// 创建模拟WebSocket实例
export const setupWebSocket = (testId) => {
  const wsUrl = import.meta.env.VITE_WS_URL || `ws://localhost:3000/ws/test/${testId}`
  return new MockWebSocketService(wsUrl)
}

// 导出模拟WebSocket服务
export default MockWebSocketService