// src/utils/pdfTemplate.js

/**
 * 生成专业心理测试报告HTML模板
 */
export const generateProfessionalReportHtml = (reportData, userInfo = {}) => {
  const { prediction, score, confidence, dimensionScores, emotionRatio, explanation, suggestions } = reportData;
  const { name = '保密用户', age = '', gender = '', testDate = new Date().toLocaleDateString('zh-CN') } = userInfo;
  
  // 获取分数对应的等级和颜色
  const getScoreLevel = (score) => {
    if (score >= 80) return { level: '优秀', color: '#4ECDC4', bgColor: 'rgba(78, 205, 196, 0.1)' };
    if (score >= 70) return { level: '良好', color: '#4ECDC4', bgColor: 'rgba(78, 205, 196, 0.1)' };
    if (score >= 60) return { level: '中等', color: '#FFD700', bgColor: 'rgba(255, 215, 0, 0.1)' };
    if (score >= 40) return { level: '需关注', color: '#FFA726', bgColor: 'rgba(255, 167, 38, 0.1)' };
    return { level: '需干预', color: '#FF6B6B', bgColor: 'rgba(255, 107, 107, 0.1)' };
  };

  const scoreLevel = getScoreLevel(score);

  return `
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>专业心理测试分析报告</title>
      <style>
        /* 使用内联样式确保PDF渲染正确 */
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
          font-family: 'Microsoft YaHei', 'PingFang SC', 'SimHei', sans-serif;
        }
        
        body {
          background: #f8fafc;
          color: #2c3e50;
          line-height: 1.6;
          padding: 20px;
          font-size: 12px;
        }
        
        .report-container {
          max-width: 210mm;
          margin: 0 auto;
          background: white;
          padding: 15mm;
          box-shadow: 0 4px 20px rgba(0,0,0,0.1);
          border-radius: 8px;
        }
        
        /* 水印背景 */
        .watermark-bg {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTEwMCAyMDBDNDQuNzcxNSA0Ni44NTcgNDYuODU3IDEwMCAyMDAgMTAwQzQ2Ljg1NyAxMDAgNDQuNzcxNSA0Ni44NTcgMTAwIDBIMjAwVjIwMEgxMDBaIiBmaWxsPSJyZ2JhKDc4LCAyMDUsIDE5NiwgMC4wNSkiLz48L3N2Zz4=');
          opacity: 0.1;
          pointer-events: none;
        }
        
        /* 头部样式 */
        .header {
          text-align: center;
          margin-bottom: 25px;
          position: relative;
          padding-bottom: 15px;
          border-bottom: 2px solid #4ECDC4;
        }
        
        .main-title {
          font-size: 28px;
          color: #2A6F79;
          margin-bottom: 8px;
          font-weight: bold;
          letter-spacing: 2px;
        }
        
        .subtitle {
          font-size: 16px;
          color: #546E7A;
          margin-bottom: 15px;
        }
        
        .report-info {
          display: flex;
          justify-content: space-between;
          background: #F8FAFC;
          padding: 10px 15px;
          border-radius: 6px;
          margin-top: 15px;
          font-size: 11px;
        }
        
        .info-item {
          display: flex;
          flex-direction: column;
        }
        
        .info-label {
          color: #78909C;
          margin-bottom: 3px;
        }
        
        .info-value {
          color: #2C3E50;
          font-weight: 500;
        }
        
        /* 核心数据卡片 */
        .score-card {
          background: linear-gradient(135deg, #4ECDC4, #2A6F79);
          color: white;
          padding: 20px;
          border-radius: 10px;
          margin: 20px 0;
          text-align: center;
          box-shadow: 0 6px 20px rgba(78, 205, 196, 0.3);
        }
        
        .score-number {
          font-size: 48px;
          font-weight: bold;
          margin: 10px 0;
          font-family: 'Arial', sans-serif;
        }
        
        .score-level {
          display: inline-block;
          background: rgba(255, 255, 255, 0.2);
          padding: 5px 15px;
          border-radius: 20px;
          font-size: 14px;
          margin-top: 10px;
        }
        
        /* 维度表格 */
        .dimension-table {
          width: 100%;
          border-collapse: collapse;
          margin: 20px 0;
          font-size: 11px;
        }
        
        .dimension-table th {
          background: #F8FAFC;
          padding: 12px 8px;
          text-align: left;
          font-weight: 600;
          color: #2A6F79;
          border-bottom: 2px solid #4ECDC4;
        }
        
        .dimension-table td {
          padding: 10px 8px;
          border-bottom: 1px solid #E8F4F3;
        }
        
        .progress-bar {
          width: 150px;
          height: 8px;
          background: #E8F4F3;
          border-radius: 4px;
          overflow: hidden;
          display: inline-block;
          vertical-align: middle;
          margin-right: 10px;
        }
        
        .progress-fill {
          height: 100%;
          border-radius: 4px;
        }
        
        .score-text {
          display: inline-block;
          width: 40px;
          text-align: right;
          font-weight: 600;
          font-family: 'Arial', sans-serif;
        }
        
        /* 图表容器 */
        .chart-container {
          margin: 25px 0;
          page-break-inside: avoid;
        }
        
        .chart-title {
          font-size: 14px;
          color: #2A6F79;
          margin-bottom: 15px;
          padding-left: 8px;
          border-left: 4px solid #4ECDC4;
          font-weight: 600;
        }
        
        /* 情绪分布图 */
        .emotion-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 15px;
          margin-top: 15px;
        }
        
        .emotion-item {
          text-align: center;
          padding: 15px;
          border-radius: 8px;
        }
        
        .emotion-color {
          width: 20px;
          height: 20px;
          border-radius: 50%;
          margin: 0 auto 10px;
        }
        
        .emotion-label {
          font-weight: 600;
          margin-bottom: 5px;
        }
        
        .emotion-value {
          font-size: 18px;
          font-weight: bold;
          font-family: 'Arial', sans-serif;
        }
        
        /* 建议部分 */
        .suggestions {
          background: #FFF9E6;
          border-left: 4px solid #FFA726;
          padding: 20px;
          margin: 25px 0;
          border-radius: 0 8px 8px 0;
        }
        
        .suggestion-title {
          color: #F57C00;
          font-size: 16px;
          margin-bottom: 15px;
          font-weight: 600;
        }
        
        .suggestion-list {
          list-style: none;
          padding-left: 20px;
        }
        
        .suggestion-list li {
          margin-bottom: 10px;
          position: relative;
          padding-left: 25px;
        }
        
        .suggestion-list li:before {
          content: '•';
          color: #4ECDC4;
          font-size: 20px;
          position: absolute;
          left: 0;
          top: -2px;
        }
        
        /* 分页控制 */
        @media print {
          body {
            padding: 0;
          }
          
          .report-container {
            box-shadow: none;
            padding: 0;
          }
          
          .page-break {
            page-break-before: always;
            margin-top: 30px;
          }
        }
        
        /* 脚注 */
        .footer {
          margin-top: 30px;
          padding-top: 15px;
          border-top: 1px solid #E8F4F3;
          text-align: center;
          color: #78909C;
          font-size: 10px;
        }
        
        /* 警告框 */
        .warning-box {
          background: #FFEBEE;
          border: 1px solid #FFCDD2;
          border-left: 4px solid #F44336;
          padding: 15px;
          margin: 20px 0;
          border-radius: 0 6px 6px 0;
          font-size: 11px;
        }
        
        .warning-title {
          color: #D32F2F;
          font-weight: 600;
          margin-bottom: 8px;
        }
      </style>
    </head>
    <body>
      <div class="watermark-bg"></div>
      <div class="report-container">
        <!-- 头部 -->
        <div class="header">
          <h1 class="main-title">专业心理测试分析报告</h1>
          <div class="subtitle">心境 · 守望 心理健康综合评估</div>
          <div class="report-info">
            <div class="info-item">
              <span class="info-label">姓名</span>
              <span class="info-value">${name}</span>
            </div>
            <div class="info-item">
              <span class="info-label">测试编号</span>
              <span class="info-value">PSY-${Date.now().toString().slice(-8)}</span>
            </div>
            <div class="info-item">
              <span class="info-label">测试日期</span>
              <span class="info-value">${testDate}</span>
            </div>
            <div class="info-item">
              <span class="info-label">评估版本</span>
              <span class="info-value">V2.0 (多模态评估)</span>
            </div>
          </div>
        </div>
        
        <!-- 综合评分 -->
        <div class="score-card">
          <div style="font-size: 14px; opacity: 0.9;">综合评估分数</div>
          <div class="score-number">${score}</div>
          <div style="margin-bottom: 10px;">总分 / 100</div>
          <div class="score-level">${scoreLevel.level}</div>
          <div style="margin-top: 15px; font-size: 11px; opacity: 0.9;">
            评估置信度：${(confidence * 100).toFixed(1)}%
          </div>
        </div>
        
        <!-- 维度得分明细 -->
        <div class="chart-container">
          <h3 class="chart-title">各维度得分明细</h3>
          <table class="dimension-table">
            <thead>
              <tr>
                <th>评估维度</th>
                <th>得分</th>
                <th>水平分析</th>
                <th>百分比</th>
              </tr>
            </thead>
            <tbody>
              ${dimensionScores.map(item => {
                const level = getScoreLevel(item.score);
                const percentage = Math.min(100, Math.max(0, item.score));
                return `
                <tr>
                  <td style="font-weight: 500;">${item.dimension}</td>
                  <td>
                    <div class="progress-bar">
                      <div class="progress-fill" style="width: ${percentage}%; background: ${level.color};"></div>
                    </div>
                    <span class="score-text">${item.score}分</span>
                  </td>
                  <td>
                    <span style="color: ${level.color}; font-weight: 500;">${level.level}</span>
                  </td>
                  <td style="text-align: center;">
                    <span style="font-family: 'Arial'; font-weight: 600;">${percentage}%</span>
                  </td>
                </tr>
                `;
              }).join('')}
            </tbody>
          </table>
        </div>
        
        <!-- 情绪状态分布 -->
        <div class="chart-container">
          <h3 class="chart-title">情绪状态分布</h3>
          <div class="emotion-grid">
            <div class="emotion-item" style="background: rgba(78, 205, 196, 0.1);">
              <div class="emotion-color" style="background: #4ECDC4;"></div>
              <div class="emotion-label">平静</div>
              <div class="emotion-value">${emotionRatio.calm || 0}%</div>
            </div>
            <div class="emotion-item" style="background: rgba(255, 215, 0, 0.1);">
              <div class="emotion-color" style="background: #FFD700;"></div>
              <div class="emotion-label">愉悦</div>
              <div class="emotion-value">${emotionRatio.happy || 0}%</div>
            </div>
            <div class="emotion-item" style="background: rgba(255, 107, 107, 0.1);">
              <div class="emotion-color" style="background: #FF6B6B;"></div>
              <div class="emotion-label">焦虑</div>
              <div class="emotion-value">${emotionRatio.anxiety || 0}%</div>
            </div>
            <div class="emotion-item" style="background: rgba(149, 165, 166, 0.1);">
              <div class="emotion-color" style="background: #95A5A6;"></div>
              <div class="emotion-label">疲惫</div>
              <div class="emotion-value">${emotionRatio.tired || 0}%</div>
            </div>
          </div>
        </div>
        
        <!-- 综合结论 -->
        <div class="chart-container">
          <h3 class="chart-title">综合评估结论</h3>
          <div style="
            background: #F8FAFC;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #2A6F79;
            margin: 15px 0;
          ">
            <p style="margin-bottom: 15px; font-size: 13px; line-height: 1.8;">
              ${explanation || '基于多维度数据分析，您的心理健康状况评估已完成。'}
            </p>
            <div style="
              display: flex;
              align-items: center;
              background: white;
              padding: 12px;
              border-radius: 6px;
              margin-top: 15px;
            ">
              <div style="
                width: 12px;
                height: 12px;
                background: ${scoreLevel.color};
                border-radius: 50%;
                margin-right: 10px;
              "></div>
              <span style="color: #2A6F79; font-weight: 500;">
                综合评定：<strong style="color: ${scoreLevel.color};">${scoreLevel.level}</strong>
                （得分：${score}/100）
              </span>
            </div>
          </div>
        </div>
        
        <!-- 因子分析说明 -->
        <div class="chart-container">
          <h3 class="chart-title">因子分析摘要</h3>
          <div style="
            background: linear-gradient(135deg, rgba(232, 244, 243, 0.5), rgba(255, 255, 255, 0.8));
            padding: 18px;
            border-radius: 8px;
            font-size: 12px;
            line-height: 1.7;
            border: 1px solid #E8F4F3;
          ">
            <p style="margin-bottom: 10px;">基于多模态数据（面部表情、语音特征、生理信号）的综合分析，本次评估主要关注以下关键因子：</p>
            <ul style="padding-left: 20px; margin: 10px 0;">
              <li style="margin-bottom: 6px;"><strong>情绪稳定性</strong>：反映情绪的波动程度和恢复能力</li>
              <li style="margin-bottom: 6px;"><strong>压力应对</strong>：评估面对压力时的调节和适应能力</li>
              <li style="margin-bottom: 6px;"><strong>社交支持感知</strong>：衡量对社会支持系统的感知和利用</li>
              <li style="margin-bottom: 6px;"><strong>自我认知清晰度</strong>：反映对自身状态和需求的觉察程度</li>
            </ul>
            <p>各因子得分已在维度明细中展示，综合加权计算得出总体评分。</p>
          </div>
        </div>
        
        <!-- 专业建议与指导 -->
        <div class="suggestions">
          <h3 class="suggestion-title">个性化建议与指导</h3>
          <ul class="suggestion-list">
            ${suggestions.map((suggestion, index) => `
              <li style="margin-bottom: 12px; font-size: 12px; line-height: 1.6;">
                <strong style="color: #2A6F79;">建议 ${index + 1}：</strong>
                ${suggestion}
              </li>
            `).join('')}
          </ul>
        </div>
        
        <!-- 根据分数提供专业建议 -->
        <div class="chart-container">
          <h3 class="chart-title">专业指导方案</h3>
          ${(() => {
            if (score >= 80) {
              return `
                <div style="background: rgba(78, 205, 196, 0.1); padding: 18px; border-radius: 8px; border-left: 4px solid #4ECDC4;">
                  <h4 style="color: #2A6F79; margin-bottom: 10px;">💪 优势维持方案</h4>
                  <p style="font-size: 12px; line-height: 1.7; margin-bottom: 12px;">
                    您的心理状态处于良好水平。建议继续保持当前的健康习惯，并探索潜能发展：
                  </p>
                  <ul style="padding-left: 20px; font-size: 11px; line-height: 1.6;">
                    <li>每周进行2-3次正念冥想练习，巩固情绪调节能力</li>
                    <li>建立情绪日记，记录积极体验和应对策略</li>
                    <li>参与志愿者活动或技能分享，增强社会联结</li>
                    <li>每季度进行一次心理状态回顾与目标设定</li>
                  </ul>
                </div>
              `;
            } else if (score >= 60) {
              return `
                <div style="background: rgba(255, 215, 0, 0.1); padding: 18px; border-radius: 8px; border-left: 4px solid #FFD700;">
                  <h4 style="color: #B8860B; margin-bottom: 10px;">🔄 平衡发展方案</h4>
                  <p style="font-size: 12px; line-height: 1.7; margin-bottom: 12px;">
                    您处于可调节的心理适应期。建议关注压力管理，建立更系统的自我照顾习惯：
                  </p>
                  <ul style="padding-left: 20px; font-size: 11px; line-height: 1.6;">
                    <li>建立规律的睡眠周期，保证每天7-8小时睡眠</li>
                    <li>学习压力管理技巧（如4-7-8呼吸法、渐进式肌肉放松）</li>
                    <li>设定合理的工作/生活边界，避免过度消耗</li>
                    <li>每月进行一次心理状态自我评估</li>
                  </ul>
                </div>
              `;
            } else if (score >= 40) {
              return `
                <div style="background: rgba(255, 167, 38, 0.1); padding: 18px; border-radius: 8px; border-left: 4px solid #FFA726;">
                  <h4 style="color: #D2691E; margin-bottom: 10px;">🎯 重点关注方案</h4>
                  <p style="font-size: 12px; line-height: 1.7; margin-bottom: 12px;">
                    您的评估显示需要更多关注。建议采取主动措施进行心理调适：
                  </p>
                  <ul style="padding-left: 20px; font-size: 11px; line-height: 1.6;">
                    <li>优先确保基本自我照顾（饮食、睡眠、适度运动）</li>
                    <li>主动与信任的亲友沟通，建立支持网络</li>
                    <li>考虑预约专业心理咨询进行1-2次评估性访谈</li>
                    <li>减少非必要的压力源，重新评估优先事项</li>
                  </ul>
                </div>
              `;
            } else {
              return `
                <div style="background: rgba(255, 107, 107, 0.1); padding: 18px; border-radius: 8px; border-left: 4px solid #FF6B6B;">
                  <h4 style="color: #8B0000; margin-bottom: 10px;">🆘 专业支持方案</h4>
                  <p style="font-size: 12px; line-height: 1.7; margin-bottom: 12px;">
                    评估表明您当前可能需要专业支持。以下建议供您参考：
                  </p>
                  <ul style="padding-left: 20px; font-size: 11px; line-height: 1.6;">
                    <li><strong>建议联系心理卫生专业人员</strong>进行详细评估</li>
                    <li>告知信任的家人或朋友您当前的状况</li>
                    <li>暂时调整工作/学习强度，优先关注心理健康</li>
                    <li>记录情绪变化模式，为专业咨询提供参考</li>
                  </ul>
                </div>
              `;
            }
          })()}
        </div>
        
        <!-- 重要提示 -->
        <div class="warning-box">
          <div class="warning-title">重要说明与免责声明</div>
          <p style="font-size: 11px; line-height: 1.6; margin-bottom: 8px;">
            1. 本报告基于多模态数据分析生成，仅供参考和自我觉察使用，不能替代专业医疗诊断。
          </p>
          <p style="font-size: 11px; line-height: 1.6; margin-bottom: 8px;">
            2. 心理状态具有动态变化性，建议定期（如每1-3个月）进行复评。
          </p>
          <p style="font-size: 11px; line-height: 1.6;">
            3. 如需专业帮助，请联系：心理咨询热线 12355 或 当地精神卫生中心。
          </p>
        </div>
        
        <!-- 脚注 -->
        <div class="footer">
          <p>报告生成时间：${new Date().toLocaleString('zh-CN')}</p>
          <p>© 2026 心境 · 守望 心理健康评估系统 | 本报告最终解释权归评估系统所有</p>
          <p style="margin-top: 5px; font-size: 9px; color: #B0BEC5;">
            保密声明：本报告内容仅限本人查阅，建议妥善保管。
          </p>
        </div>
      </div>
    </body>
    </html>
  `;
};