<template>
  <div class="splash-page">
    <!-- 背景层 -->
    <div class="splash-bg"></div>
    
    <!-- 主内容容器 -->
    <div class="splash-container">
      <!-- 内容区 -->
      <div class="splash-content">
        <h1 class="splash-title">心镜·守望</h1>
        <p class="splash-subtitle">面向学生心理健康的多模态可解释性实时评估系统</p>
        <p class="splash-desc">以心为镜，守望成长 —— 实时感知情绪，科学守护心灵</p>
        
        <button class="btn-start" @click="goToRelaxGuide">
          <span class="btn-icon"></span>
          开始评估
        </button>
        
        <div class="splash-hint">
          <p>请确保在安静、私密的环境中进行评估</p>
          <p>整个评估过程约需5-7分钟</p>
        </div>
      </div>
      
      <!-- 页脚 -->
      <footer class="splash-footer">
        <p>心镜·守望心理健康评估系统 © 2026</p>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goToRelaxGuide = () => {
  router.push('/relax-guide')
}
</script>

<style scoped>
/* 页面容器 */
.splash-page {
  width: 100%;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, 
    rgba(248, 250, 252, 0.95) 0%, 
    rgba(232, 244, 243, 0.95) 100%
  );
  padding: 20px;
}

/* 背景 */
.splash-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 30%, rgba(78, 205, 196, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(42, 111, 121, 0.08) 0%, transparent 50%);
  animation: bgFloat 20s infinite ease-in-out;
  z-index: 0;
}

@keyframes bgFloat {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(-10px, 10px) scale(1.02); }
  66% { transform: translate(10px, -5px) scale(0.98); }
}

/* 主容器 - 使用响应式宽度 */
.splash-container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 1200px; /* 增大最大宽度 */
  min-height: 90vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  animation: contentAppear 0.8s ease-out;
}

/* 内容区 - 使用响应式宽度 */
.splash-content {
  width: 100%;
  max-width: 800px; /* 增加内容区最大宽度 */
  text-align: center;
  padding: 60px 40px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(42, 111, 121, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  margin: 0 auto;
}

@keyframes contentAppear {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 标题 */
.splash-title {
  font-family: 'Ma Shan Zheng', cursive;
  font-size: clamp(3rem, 8vw, 4.5rem); /* 使用clamp实现响应式字体 */
  color: #2A6F79;
  margin: 0 0 1rem 0;
  letter-spacing: 0.3rem;
  line-height: 1.1;
  text-shadow: 0 2px 8px rgba(255, 255, 255, 0.6);
}

/* 副标题 */
.splash-subtitle {
  font-size: clamp(1rem, 2vw, 1.4rem);
  color: #2C3E50;
  margin: 0 auto 1rem;
  line-height: 1.6;
  font-weight: 500;
  opacity: 0.9;
  max-width: 800px;
  padding: 0 20px;
}

/* 描述 */
.splash-desc {
  font-size: clamp(0.9rem, 1.5vw, 1.1rem);
  color: #546E7A;
  margin: 0 auto 3rem;
  line-height: 1.6;
  font-style: italic;
  opacity: 0.9;
  max-width: 600px;
  padding: 0 20px;
}

/* 开始按钮 */
.btn-start {
  position: relative;
  padding: 18px 50px;
  background: linear-gradient(135deg, #4ECDC4, #2A6F79);
  color: white;
  border: none;
  border-radius: 50px;
  font-size: clamp(1rem, 1.5vw, 1.2rem);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  display: inline-flex;
  align-items: center;
  gap: 0.8rem;
  box-shadow: 0 8px 30px rgba(78, 205, 196, 0.3);
  overflow: hidden;
  z-index: 1;
  margin: 0 auto 3rem;
  min-width: 200px;
  justify-content: center;
}

.btn-start:hover {
  transform: translateY(-5px) scale(1.05);
  box-shadow: 0 20px 40px rgba(78, 205, 196, 0.4);
}

.btn-icon {
  font-size: 1.2rem;
  filter: drop-shadow(0 2px 3px rgba(0,0,0,0.2));
}

/* 提示信息 */
.splash-hint {
  width: 100%;
  max-width: 600px;
  margin: 2rem auto 0;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(232, 244, 243, 0.5);
  color: #546E7A;
  font-size: clamp(0.85rem, 1.2vw, 0.95rem);
  line-height: 1.5;
}

.splash-hint p {
  margin: 0.3rem 0;
  opacity: 0.8;
}

/* 页脚 */
.splash-footer {
  position: absolute;
  bottom: 20px;
  left: 0;
  right: 0;
  text-align: center;
  color: #78909C;
  font-size: clamp(0.7rem, 1vw, 0.8rem);
  opacity: 0.6;
  z-index: 1;
  padding: 0 20px;
}

/* 响应式断点 */
@media (max-width: 1200px) {
  .splash-container {
    max-width: 100%;
    padding: 30px 15px;
  }
  
  .splash-content {
    padding: 50px 30px;
    max-width: 90%;
  }
}

@media (max-width: 768px) {
  .splash-page {
    padding: 10px;
  }
  
  .splash-container {
    padding: 20px 10px;
    min-height: 85vh;
  }
  
  .splash-content {
    padding: 40px 20px;
    max-width: 95%;
  }
  
  .splash-title {
    font-size: 2.5rem;
    letter-spacing: 0.2rem;
  }
  
  .splash-subtitle {
    font-size: 1rem;
  }
  
  .splash-desc {
    font-size: 0.9rem;
  }
  
  .btn-start {
    padding: 16px 40px;
    font-size: 1rem;
  }
  
  .splash-footer {
    position: relative;
    bottom: auto;
    margin-top: 30px;
  }
}

@media (max-width: 480px) {
  .splash-content {
    padding: 30px 15px;
  }
  
  .splash-title {
    font-size: 2rem;
  }
  
  .splash-subtitle {
    font-size: 0.9rem;
    padding: 0 10px;
  }
  
  .splash-desc {
    font-size: 0.8rem;
    padding: 0 10px;
  }
  
  .btn-start {
    padding: 14px 30px;
    font-size: 0.9rem;
    min-width: 180px;
  }
}
</style>