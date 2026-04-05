/**
 * 安抚话术工具库
 * 提供针对不同问题类型的安抚话术
 */

// 话术分类
export const comfortCategories = {
  wellbeing: '身心健康',
  positive: '积极体验',
  relationship: '人际关系',
  coping: '应对方式',
  current: '当前情绪',
  general: '通用'
}

// 安抚话术库
export const comfortMessages = {
  wellbeing: [
    { icon: '🌙', text: '感谢您分享关于睡眠的感受，这很重要', duration: 3000 },
    { icon: '✨', text: '每一夜的休息，都是身心的修复', duration: 3000 },
    { icon: '🌿', text: '关注身心的状态，是爱自己的开始', duration: 3000 },
    { icon: '💤', text: '让疲惫找到出口，让身心得以休憩', duration: 3000 }
  ],
  positive: [
    { icon: '🌻', text: '能发现生活中的美好，是很棒的能力', duration: 3000 },
    { icon: '🌈', text: '这些喜悦的时刻，是心灵的阳光', duration: 3000 },
    { icon: '🌟', text: '记住这些温暖，它们会在需要时发光', duration: 3000 },
    { icon: '🎁', text: '生活赠予的小确幸，值得被珍藏', duration: 3000 }
  ],
  relationship: [
    { icon: '🤝', text: '关系的质量，深深影响着我们的内心', duration: 3000 },
    { icon: '💕', text: '在关系中感受被理解，是一种滋养', duration: 3000 },
    { icon: '🌉', text: '每一段关系，都是心灵的桥梁', duration: 3000 },
    { icon: '🤲', text: '给予与接受，都是关系的温度', duration: 3000 }
  ],
  coping: [
    { icon: '🧘', text: '您有自己的方式照顾自己，这很珍贵', duration: 3000 },
    { icon: '🌿', text: '放松的时刻，是给自己的温柔礼物', duration: 3000 },
    { icon: '🛀', text: '找到让自己舒适的方式，很重要', duration: 3000 },
    { icon: '🌅', text: '在忙碌中为自己留白，是智慧', duration: 3000 }
  ],
  current: [
    { icon: '🌸', text: '此刻的心情，无论是什么，都值得被看见', duration: 3000 },
    { icon: '💭', text: '感谢您诚实地表达此刻的感受', duration: 3000 },
    { icon: '🌊', text: '情绪如潮汐，自然地来，自然地去', duration: 3000 },
    { icon: '☁️', text: '此刻的感受，只是此刻的云彩', duration: 3000 }
  ],
  general: [
    { icon: '🌱', text: '感谢您的真诚分享', duration: 3000 },
    { icon: '💧', text: '每一句话语，都如清泉般珍贵', duration: 3000 },
    { icon: '🎋', text: '您的表达，让理解成为可能', duration: 3000 },
    { icon: '📖', text: '每个故事，都是独一无二的诗篇', duration: 3000 }
  ]
}

// 获取随机的安抚话术
export function getRandomComfortMessage(category = 'general') {
  const messages = comfortMessages[category] || comfortMessages.general
  return messages[Math.floor(Math.random() * messages.length)]
}

// 获取适合问题类型的安抚话术
export function getComfortMessageByQuestionType(questionType) {
  return getRandomComfortMessage(questionType)
}

// 获取积极鼓励语
export function getEncouragementMessage(progress) {
  const encouragements = [
    { threshold: 0, icon: '🌱', text: '分享刚开始，慢慢来，不着急' },
    { threshold: 0.2, icon: '🌿', text: '您分享得很用心，请继续' },
    { threshold: 0.4, icon: '🌸', text: '过半了，您做得很好' },
    { threshold: 0.6, icon: '🌳', text: '快完成了，感谢您的真诚' },
    { threshold: 0.8, icon: '🎋', text: '所有分享已完成，感谢您的信任' }
  ]
  
  // 找到第一个进度大于等于当前进度的鼓励语
  for (let i = encouragements.length - 1; i >= 0; i--) {
    if (progress >= encouragements[i].threshold) {
      return encouragements[i]
    }
  }
  
  return encouragements[0]
}

// 获取诗句
export function getPoemLine(index) {
  const poems = [
    '静听心声，自在表达',
    '如竹虚心，自然生长',
    '此时此刻，唯有倾听',
    '心语如诗，缓缓流淌',
    '分享完成，静待花开'
  ]
  return poems[index] || poems[0]
}

// 获取心率状态诗意描述
export function getHeartStatusPoetic() {
  const statuses = [
    { icon: '🌊', text: '心律平和', description: '如宁静的湖面' },
    { icon: '🌿', text: '心律平稳', description: '如林间微风' },
    { icon: '🌸', text: '心律舒缓', description: '如花瓣轻落' },
    { icon: '☁️', text: '心律安宁', description: '如云般舒展' }
  ]
  return statuses[Math.floor(Math.random() * statuses.length)]
}

// 获取时刻诗句
export function getMomentPoem() {
  const poems = [
    { icon: '🎋', line1: '此刻静好', line2: '心语如涓涓细流' },
    { icon: '🍂', line1: '一叶知秋', line2: '一语见心' },
    { icon: '🌅', line1: '晨光微熹', line2: '心境渐明' },
    { icon: '🌌', line1: '静夜思语', line2: '星河入梦' }
  ]
  return poems[Math.floor(Math.random() * poems.length)]
}