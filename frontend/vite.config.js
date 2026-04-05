import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  // 配置路径别名（方便导入文件）
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  // 开发服务器配置
  server: {
    port: 8080, // 启动端口（避免冲突）
    open: true, // 启动后自动打开浏览器
    cors: true  // 允许跨域（对接API用）
  }
})