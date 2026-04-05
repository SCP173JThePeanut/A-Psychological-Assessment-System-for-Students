// src/utils/pdfExport.js
import { jsPDF } from 'jspdf'

/**
 * 最小化PDF导出 - 不依赖任何API
 */
export const simpleExportPDF = (content, fileName = 'report') => {
  try {
    const pdf = new jsPDF()
    
    // 添加一些基本内容
    pdf.setFontSize(16)
    pdf.text('心理评估报告', 20, 20)
    
    pdf.setFontSize(12)
    pdf.text(`生成时间: ${new Date().toLocaleString()}`, 20, 30)
    
    // 如果是文本内容，可以这样添加
    if (typeof content === 'string') {
      const lines = pdf.splitTextToSize(content, 170)
      pdf.text(lines, 20, 45)
    }
    
    pdf.save(`${fileName}_${Date.now()}.pdf`)
    return true
  } catch (error) {
    console.error('PDF生成失败:', error)
    alert('PDF导出失败，请重试')
    return false
  }
}

export default simpleExportPDF