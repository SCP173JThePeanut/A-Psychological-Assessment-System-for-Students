/**
 * 水墨动画工具库
 * 提供各种水墨风格动画效果
 */

// 创建飘落竹叶
export function createFallingLeaves(container, count = 15) {
  if (!container) return
  
  // 清理旧的竹叶
  container.innerHTML = ''
  
  for (let i = 0; i < count; i++) {
    const leaf = document.createElement('div')
    leaf.className = 'falling-leaf'
    
    // 随机属性
    const left = Math.random() * 100
    const size = 10 + Math.random() * 20
    const duration = 10 + Math.random() * 20
    const delay = Math.random() * 20
    const opacity = 0.2 + Math.random() * 0.3
    const rotation = Math.random() * 360
    
    leaf.style.cssText = `
      left: ${left}vw;
      width: ${size}px;
      height: ${size}px;
      opacity: ${opacity};
      animation-delay: ${delay}s;
      animation-duration: ${duration}s;
      transform: rotate(${rotation}deg);
      background: #2d5a27;
      clip-path: polygon(50% 0%, 0% 100%, 100% 100%);
      position: absolute;
      animation: leaf-fall linear infinite;
    `
    
    container.appendChild(leaf)
  }
}

// 创建水墨涟漪
export function createInkRipple(container, options = {}) {
  if (!container) return null
  
  const ripple = document.createElement('div')
  ripple.className = 'ink-ripple'
  
  const {
    x = 50,
    y = 50,
    size = 100,
    color = '#6dd5ed',
    duration = 2000
  } = options
  
  ripple.style.cssText = `
    position: absolute;
    left: ${x}%;
    top: ${y}%;
    width: ${size}px;
    height: ${size}px;
    border: 2px solid ${color};
    border-radius: 50%;
    transform: translate(-50%, -50%);
    animation: ink-ripple ${duration}ms ease-out forwards;
    pointer-events: none;
  `
  
  container.appendChild(ripple)
  
  // 动画结束后移除
  setTimeout(() => {
    if (ripple.parentNode === container) {
      container.removeChild(ripple)
    }
  }, duration)
  
  return ripple
}

// 创建墨水扩散效果
export function createInkDiffusion(container, options = {}) {
  if (!container) return null
  
  const blot = document.createElement('div')
  blot.className = 'ink-blot'
  
  const {
    x = 50,
    y = 50,
    size = 300,
    color = '#2d5a27',
    duration = 30000
  } = options
  
  blot.style.cssText = `
    position: absolute;
    left: ${x}%;
    top: ${y}%;
    width: ${size}px;
    height: ${size}px;
    background: ${color};
    border-radius: 50%;
    filter: blur(40px);
    opacity: 0.1;
    transform: translate(-50%, -50%);
    animation: ink-diffuse ${duration}ms infinite linear;
  `
  
  container.appendChild(blot)
  return blot
}

// 创建波形动画
export function createWaveAnimation(bars, speed = 200) {
  let animationId = null
  
  const animate = () => {
    bars.value = bars.value.map(() => 10 + Math.random() * 60)
    animationId = setTimeout(animate, speed)
  }
  
  animate()
  
  return {
    stop: () => {
      if (animationId) {
        clearTimeout(animationId)
        animationId = null
      }
    }
  }
}

// 创建呼吸动画
export function createBreathingAnimation(element, options = {}) {
  if (!element) return null
  
  const {
    duration = 4000,
    minScale = 1,
    maxScale = 1.2
  } = options
  
  let startTime = null
  let animationId = null
  
  const animate = (timestamp) => {
    if (!startTime) startTime = timestamp
    const elapsed = timestamp - startTime
    const progress = (elapsed % duration) / duration
    
    // 正弦波，0-π为吸气，π-2π为呼气
    const scale = progress < 0.5
      ? minScale + (maxScale - minScale) * Math.sin(progress * Math.PI)
      : maxScale - (maxScale - minScale) * Math.sin(progress * Math.PI)
    
    element.style.transform = `scale(${scale})`
    animationId = requestAnimationFrame(animate)
  }
  
  animationId = requestAnimationFrame(animate)
  
  return {
    stop: () => {
      if (animationId) {
        cancelAnimationFrame(animationId)
        animationId = null
      }
    }
  }
}

// 创建心跳动画
export function createHeartbeatAnimation(element, options = {}) {
  if (!element) return null
  
  const {
    duration = 1500,
    minScale = 1,
    maxScale = 1.1
  } = options
  
  let startTime = null
  let animationId = null
  
  const animate = (timestamp) => {
    if (!startTime) startTime = timestamp
    const elapsed = timestamp - startTime
    const progress = (elapsed % duration) / duration
    
    // 心跳效果：快速收缩然后缓慢恢复
    const scale = progress < 0.3
      ? minScale + (maxScale - minScale) * (progress / 0.3)
      : maxScale - (maxScale - minScale) * ((progress - 0.3) / 0.7)
    
    element.style.transform = `scale(${scale})`
    animationId = requestAnimationFrame(animate)
  }
  
  animationId = requestAnimationFrame(animate)
  
  return {
    stop: () => {
      if (animationId) {
        cancelAnimationFrame(animationId)
        animationId = null
      }
    }
  }
}

// 创建墨点动画
export function createInkDotsAnimation(container, count = 12, options = {}) {
  if (!container) return []
  
  const dots = []
  const {
    baseDistance = 40,
    color = '#f8b8d0'
  } = options
  
  for (let i = 0; i < count; i++) {
    const dot = document.createElement('div')
    dot.className = 'ink-dot'
    
    dot.style.cssText = `
      position: absolute;
      width: 8px;
      height: 8px;
      background: ${color};
      border-radius: 50%;
      opacity: 0.3;
      filter: blur(1px);
      transform-origin: center;
    `
    
    container.appendChild(dot)
    dots.push(dot)
  }
  
  let animationId = null
  const startTime = Date.now()
  
  const animate = () => {
    const time = (Date.now() - startTime) / 1000
    
    dots.forEach((dot, index) => {
      const angle = (index / dots.length) * Math.PI * 2
      const distance = baseDistance + Math.sin(time + index) * 10
      const x = Math.cos(angle) * distance
      const y = Math.sin(angle) * distance
      const opacity = 0.3 + Math.sin(time + index) * 0.2
      
      dot.style.transform = `translate(${x}px, ${y}px)`
      dot.style.opacity = opacity
    })
    
    animationId = requestAnimationFrame(animate)
  }
  
  animationId = requestAnimationFrame(animate)
  
  return {
    dots,
    stop: () => {
      if (animationId) {
        cancelAnimationFrame(animationId)
        animationId = null
      }
    }
  }
}