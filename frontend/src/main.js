import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// 导入全局样式
import '@/assets/styles/reset.css'
import '@/assets/styles/variables.css'

// 创建Vue实例
const app = createApp(App)

// 挂载路由
app.use(router)

// 全局配置（可选，如全局提示）
app.config.globalProperties.$message = (msg, type = 'info') => {
  alert(`${type === 'error' ? '❌ ' : '✅ '}${msg}`)
}

// 挂载到DOM
app.mount('#app')