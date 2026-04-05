// src/utils/pdfExport.js
// 移除有问题的导入：import { request } from '../api/index'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'

// 使用模拟数据
const USE_MOCK = true

/**
 * 模拟数据 - 专业心理评估报告
 */
const mockReportData = {
  code: 200,
  message: '成功',
  data: {
    // 基础信息
    reportId: 'PSY-20240318-001',
    testDate: '2024-03-18 14:30:00',
    duration: 1800, // 测试时长（秒）
    
    // 综合评估
    prediction: '情绪总体平稳，但存在工作压力',
    confidence: 0.92,
    score: 72,
    level: '良好',
    
    // 贡献度分析
    contributions: {
      face: 45,  // 面部表情分析
      audio: 25, // 语音情感分析
      hr: 30     // 心率变异性
    },
    
    // 情绪分布
    emotionRatio: {
      calm: 50,   // 平静
      happy: 20,  // 愉悦
      anxiety: 15, // 焦虑
      tired: 15   // 疲惫
    },
    
    // 详细解释
    explanation: '评估显示您当前情绪状态总体平稳，基础心理韧性良好。在压力应对方面表现中等，可能由于近期工作/学业任务较重导致间歇性压力感升高。建议关注压力管理和自我调节。',
    
    // 维度得分
    dimensionScores: [
      { dimension: '情绪稳定性', score: 72, status: '良好', description: '情绪波动在正常范围内，恢复能力较好' },
      { dimension: '压力应对', score: 65, status: '中等', description: '面对压力时有一定的调节能力，但存在提升空间' },
      { dimension: '社交支持', score: 78, status: '良好', description: '拥有较好的社会支持网络，能有效获取情感支持' },
      { dimension: '自我认知', score: 68, status: '中等', description: '对自身状态有基本认知，建议增强自我觉察' },
      { dimension: '生活意义', score: 75, status: '中等', description: '对生活有一定目标感，建议进一步明确个人价值' },
      { dimension: '心理弹性', score: 60, status: '中等', description: '面对挫折的恢复能力处于平均水平' }
    ],
    
    // 压力源分析
    stressSources: [
      { name: '工作/学业', score: 78, level: '较高' },
      { name: '人际关系', score: 45, level: '较低' },
      { name: '家庭事务', score: 52, level: '中等' },
      { name: '经济状况', score: 60, level: '中等' },
      { name: '个人发展', score: 68, level: '中等' },
      { name: '健康状况', score: 55, level: '中等' }
    ],
    
    // 生理指标
    physiologicalMetrics: {
      avgHeartRate: 72,
      hrv: 45,
      sleepQuality: 7.2,
      activityLevel: 6500
    },
    
    // 评估时间线
    timeline: [
      { time: '09:00', score: 68, emotion: 'calm' },
      { time: '12:00', score: 75, emotion: 'happy' },
      { time: '15:00', score: 65, emotion: 'anxiety' },
      { time: '18:00', score: 70, emotion: 'calm' },
      { time: '21:00', score: 72, emotion: 'calm' }
    ],
    
    // 建议列表
    suggestions: [
      '建立规律的作息时间，保证7-8小时睡眠',
      '每天安排15-20分钟的正念冥想练习',
      '每周进行3次中等强度有氧运动',
      '学习压力管理技巧，如深呼吸、时间管理',
      '加强与亲友的社交联系，分享感受'
    ],
    
    // 风险评估
    riskAssessment: {
      depressionRisk: '低',
      anxietyRisk: '中',
      burnoutRisk: '低',
      overallRisk: '低'
    },
    
    // 下次评估建议
    nextAssessment: {
      suggestedDate: '2024-04-18',
      interval: 30, // 天数
      reason: '定期复查，监测压力水平变化'
    }
  }
}

/**
 * 获取报告详情
 * @param {string} reportId - 报告ID
 * @returns {Promise} 报告数据
 */
export const getReportDetail = async (reportId) => {
  // 模拟延迟
  await new Promise(resolve => setTimeout(resolve, 800))
  
  // 根据reportId返回不同数据
  const mockData = { ...mockReportData }
  mockData.data.reportId = reportId || mockData.data.reportId
  
  return mockData
}

/**
 * 提交评估数据
 * @param {Object} data - 评估数据
 * @returns {Promise} 提交结果
 */
export const submitAssessment = async (data) => {
  // 模拟延迟
  await new Promise(resolve => setTimeout(resolve, 1500))
  
  return {
    code: 200,
    message: '评估数据提交成功',
    data: {
      reportId: `PSY-${Date.now().toString().slice(-8)}`,
      estimatedTime: 1800, // 预计处理时间（秒）
      status: 'processing'
    }
  }
}

/**
 * 获取评估历史
 * @param {Object} params - 查询参数
 * @returns {Promise} 历史列表
 */
export const getAssessmentHistory = async (params = {}) => {
  await new Promise(resolve => setTimeout(resolve, 500))
  
  const history = Array.from({ length: 5 }, (_, i) => ({
    id: `PSY-${Date.now().toString().slice(-8)}-${i}`,
    date: new Date(Date.now() - i * 7 * 24 * 60 * 60 * 1000).toISOString(),
    score: 65 + Math.random() * 20,
    prediction: ['情绪稳定', '轻度压力', '状态良好', '需关注', '表现优秀'][i],
    duration: 1500 + Math.random() * 600
  }))
  
  return {
    code: 200,
    message: '成功',
    data: {
      list: history,
      total: 5,
      page: params.page || 1,
      pageSize: params.pageSize || 10
    }
  }
}

/**
 * 删除评估报告
 * @param {string} reportId - 报告ID
 * @returns {Promise} 删除结果
 */
export const deleteReport = async (reportId) => {
  await new Promise(resolve => setTimeout(resolve, 300))
  
  return {
    code: 200,
    message: '报告删除成功',
    data: { reportId }
  }
}

/**
 * 导出报告
 * @param {string} reportId - 报告ID
 * @param {string} format - 导出格式 (pdf, csv, json)
 * @returns {Promise} 导出结果
 */
export const exportReport = async (reportId, format = 'pdf') => {
  await new Promise(resolve => setTimeout(resolve, 1000))
  
  return {
    code: 200,
    message: '报告导出成功',
    data: {
      reportId,
      format,
      downloadUrl: `https://example.com/reports/${reportId}.${format}`,
      expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
    }
  }
}

/**
 * 获取统计数据
 * @returns {Promise} 统计数据
 */
export const getStatistics = async () => {
  await new Promise(resolve => setTimeout(resolve, 500))
  
  return {
    code: 200,
    message: '成功',
    data: {
      totalAssessments: 124,
      avgScore: 68.5,
      commonIssues: [
        { issue: '工作压力', percentage: 45 },
        { issue: '睡眠问题', percentage: 38 },
        { issue: '情绪波动', percentage: 32 },
        { issue: '社交焦虑', percentage: 25 }
      ],
      trend: {
        last7Days: [65, 68, 70, 67, 72, 69, 71],
        last30Days: Array.from({ length: 30 }, () => 65 + Math.random() * 10)
      }
    }
  }
}

/**
 * 核心新增：generatePdfReport 函数（适配 Report.vue 的导入）
 * @param {Object} reportData - 报告数据
 * @param {Object} userInfo - 用户信息
 * @param {string} fileName - PDF文件名
 * @returns {Promise} 导出结果
 */
export const generatePdfReport = async (reportData, userInfo, fileName = '心理评估报告') => {
  try {
    const getModalExplanation = (modal, data) => {
      const score = data.score || 50;                 // 原始分数 0-100（越高压力越小）
      const stressLevel = ((100 - score) / 100) * 5;  // 压力指数 0-5
      const contribution = data.contributions?.[modal] || 0;
      const hrv = data.physiologicalMetrics?.hrv || 45;

      switch (modal) {
        case 'face':
          if (stressLevel > 3.0) return '面部肌肉紧张，皱眉频率较高，显示明显压力反应。';
          if (stressLevel > 1.5) return '面部表情轻微紧绷，有一定紧张感。';
          return '面部表情自然放松，情绪稳定。';
        case 'audio':
          if (stressLevel > 3.0) return '语速较快，音调偏高，存在焦虑情绪特征。';
          if (stressLevel > 1.5) return '语速轻微加快，语调略有波动。';
          return '语速平稳，语调自然，情绪状态良好。';
        case 'hr':
          if (stressLevel > 3.0) return `心率变异性较低（${hrv}ms），交感神经活跃，应激水平高。`;
          if (stressLevel > 1.5) return `心率变异性中等（${hrv}ms），有一定生理压力。`;
          return `心率变异性良好（${hrv}ms），自主神经平衡。`;
        default:
          return '该模态对评估结果有重要贡献。';
      }
    };
    // 1. 动态创建PDF内容容器（临时DOM）
    const pdfContainer = document.createElement('div')
    pdfContainer.style.width = '210mm'
    pdfContainer.style.padding = '20mm'
    pdfContainer.style.backgroundColor = '#fff'
    pdfContainer.style.position = 'absolute'
    pdfContainer.style.top = '-9999px'
    pdfContainer.style.left = '-9999px'
    pdfContainer.style.fontFamily = 'SimSun, Microsoft YaHei, sans-serif'
    
    // 2. 拼接PDF内容（适配你的数据结构）
    pdfContainer.innerHTML = `
      <div style="text-align: center; margin-bottom: 20px;">
        <h1 style="font-size: 20px; margin: 0; color: #333;">专业心理评估报告</h1>
        <div style="font-size: 12px; color: #666; margin-top: 8px;">
          评估人：${userInfo.name || '保密用户'} | 评估时间：${userInfo.testDate || new Date().toLocaleString()}
        </div>
        <hr style="border: 1px solid #eee; margin: 10px 0;">
      </div>

      <!-- 综合评估 -->
      <div style="margin-bottom: 15px;">
        <h3 style="font-size: 16px; color: #333; margin: 0 0 8px 0;">一、综合评估</h3>
        <div style="font-size: 14px; line-height: 1.6;">
          <p style="margin: 4px 0;">评估结果：${reportData.prediction || '暂无'}</p>
          <p style="margin: 4px 0;">评估得分：${reportData.score || 0} 分（满分100）</p>
          <p style="margin: 4px 0;">置信度：${reportData.confidence ? (reportData.confidence * 100).toFixed(1) + '%' : '0%'}</p>
          <p style="margin: 4px 0;">状态等级：${reportData.level || '暂无'}</p>
        </div>
      </div>


      <!-- 详细解释 -->
      <div style="margin-bottom: 15px;">
        <h3 style="font-size: 16px; color: #333; margin: 0 0 8px 0;">二、评估解释</h3>
        <div style="font-size: 14px; line-height: 1.6; color: #444;">
          ${reportData.explanation || '暂无评估解释'}
        </div>
      </div>

      <!-- 三、多模态置信度分析（原各维度得分位置） -->
      <div style="margin-bottom: 15px;">
        <h3 style="font-size: 16px; color: #333; margin: 0 0 8px 0;">三、多模态置信度分析</h3>
        <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
          <thead>
            <tr style="background: #f5f5f5;">
              <th style="border: 1px solid #ddd; padding: 6px; text-align: left;">模态</th>
              <th style="border: 1px solid #ddd; padding: 6px; text-align: center;">置信度（贡献度）</th>
              <th style="border: 1px solid #ddd; padding: 6px; text-align: left;">动态说明</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style="border: 1px solid #ddd; padding: 6px;">面部表情</td>
              <td style="border: 1px solid #ddd; padding: 6px; text-align: center;">${reportData.contributions?.face || 0}%</td>
              <td style="border: 1px solid #ddd; padding: 6px;">${getModalExplanation('face', reportData)}</td>
            </tr>
            <tr>
              <td style="border: 1px solid #ddd; padding: 6px;">语音情感</td>
              <td style="border: 1px solid #ddd; padding: 6px; text-align: center;">${reportData.contributions?.audio || 0}%</td>
              <td style="border: 1px solid #ddd; padding: 6px;">${getModalExplanation('audio', reportData)}</td>
            </tr>
            <tr>
              <td style="border: 1px solid #ddd; padding: 6px;">心率指标</td>
              <td style="border: 1px solid #ddd; padding: 6px; text-align: center;">${reportData.contributions?.hr || 0}%</td>
              <td style="border: 1px solid #ddd; padding: 6px;">${getModalExplanation('hr', reportData)}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 建议列表 -->
      <div style="margin-bottom: 0; margin-top: 0;">
        <h3 style="font-size: 16px; color: #333; margin: 0 0 4px 0;">五、专业建议</h3>
        <ul style="font-size: 14px; line-height: 1.4; margin: 0; padding-left: 20px;">
          ${(reportData.suggestions?.slice(0, 4) || []).map(item => `<li style="margin: 4px 0;">${item}</li>`).join('')}
          ${(!reportData.suggestions || reportData.suggestions.length === 0) ? '<li>暂无专业建议</li>' : ''}
        </ul>
      </div>

      <!-- 风险评估 -->
      <div style="margin-bottom: 15px;">
        <h3 style="font-size: 16px; color: #333; margin: 0 0 8px 0;">五、风险评估</h3>
        <div style="font-size: 14px; line-height: 1.6;">
          <p style="margin: 4px 0;">抑郁风险：${reportData.riskAssessment?.depressionRisk || '暂无'}</p>
          <p style="margin: 4px 0;">焦虑风险：${reportData.riskAssessment?.anxietyRisk || '暂无'}</p>
          <p style="margin: 4px 0;">倦怠风险：${reportData.riskAssessment?.burnoutRisk || '暂无'}</p>
          <p style="margin: 4px 0;">总体风险：${reportData.riskAssessment?.overallRisk || '暂无'}</p>
        </div>
      </div>
    `;

    // 3. 添加临时容器到页面
    document.body.appendChild(pdfContainer);

    // 4. 转换为画布
    const canvas = await html2canvas(pdfContainer, {
      scale: 2,
      useCORS: true,
      logging: false,
      backgroundColor: '#ffffff'
    });

    // 5. 生成PDF
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    });
    const imgWidth = 210;
    const imgHeight = canvas.height * imgWidth / canvas.width;
    pdf.addImage(canvas, 'PNG', 0, 0, imgWidth, imgHeight);

    // 6. 保存PDF并清理
    pdf.save(`${fileName}_${Date.now()}.pdf`);
    document.body.removeChild(pdfContainer);

    return { success: true, message: 'PDF导出成功' };
  } catch (error) {
    console.error('PDF生成失败:', error);
    alert('PDF导出失败，请重试');
    throw new Error(`PDF导出失败：${error.message}`);
  }
}

// 导出所有函数
export default {
  getReportDetail,
  submitAssessment,
  getAssessmentHistory,
  deleteReport,
  exportReport,
  getStatistics,
  generatePdfReport
}