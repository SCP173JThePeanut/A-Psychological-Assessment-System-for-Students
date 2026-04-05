// 多模态数据采集与处理工具 (真实设备版)
// 注意：特征提取(13,21,9维)通常应由后端复杂模型完成。此处提供数据采集和格式封装。

/**
 * 生成唯一会话ID，用于关联一次完整的测试过程
 * @returns {string} 会话ID
 */
export const generateSessionId = () => {
  return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
};

/**
 * 格式化数据包供API调用
 * @param {Array} faceFeatures - 13维面部特征数组（可由后端从视频帧提取）
 * @param {Array} audioFeatures - 21维音频特征数组（可由后端从音频流提取）
 * @param {Array} hrFeatures - 9维心率特征数组
 * @returns {Object} 符合后端约定的数据包对象
 */
export const formatDataPacket = (faceFeatures = [], audioFeatures = [], hrFeatures = []) => {
  // 如果前端无法提取特征，这里可发送原始数据或预留空数组，由后端处理。
  // 以下返回模拟特征向量，实际项目应替换为真实提取逻辑或删除。
  const defaultFaceFeatures = Array(13).fill(0).map(() => parseFloat((Math.random() * 2 - 1).toFixed(4)));
  const defaultAudioFeatures = Array(21).fill(0).map(() => parseFloat((Math.random() * 2 - 1).toFixed(4)));
  const defaultHrFeatures = Array(9).fill(0).map(() => parseFloat((Math.random() * 2 - 1).toFixed(4)));

  return {
    face_features: faceFeatures.length === 13 ? faceFeatures : defaultFaceFeatures,
    audio_features: audioFeatures.length === 21 ? audioFeatures : defaultAudioFeatures,
    hr_features: hrFeatures.length === 9 ? hrFeatures : defaultHrFeatures,
    timestamp: new Date().toISOString(),
  };
};

/**
 * 验证特征数据格式是否符合与后端约定的规范
 * @param {Object} features 特征包对象
 * @returns {Boolean} 是否验证通过
 */
export const validateFeatures = (features) => {
  const spec = { face_features: 13, audio_features: 21, hr_features: 9 };
  for (const [key, requiredLength] of Object.entries(spec)) {
    if (!features[key] || !Array.isArray(features[key]) || features[key].length !== requiredLength) {
      console.error(`${key} 格式错误！要求长度为 ${requiredLength} 的数组，当前长度：${features[key]?.length || 0}`);
      return false;
    }
    if (!features[key].every(item => typeof item === 'number' && !isNaN(item))) {
      console.error(`${key} 必须全部为有效数字！`);
      return false;
    }
  }
  return true;
};

// ============================================================================
// 音频录制与处理类
// ============================================================================
export class AudioRecorder {
  constructor() {
    this.mediaRecorder = null;
    this.stream = null;
    this.audioChunks = [];
    this.isRecording = false;
    this.audioContext = null;
    this.analyser = null;
    this.dataArray = null;
  }

  /**
   * 请求麦克风权限并获取音频流
   * @returns {Promise<MediaStream>} 音频流对象
   */
  async startMicrophone() {
    try {
      // 注意：getUserMedia 需要在安全上下文（HTTPS 或 localhost）中运行
      this.stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,         // 单声道通常足够用于语音分析
          sampleRate: 16000,       // 常见语音采样率
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });
      console.log('✅ 麦克风访问成功，音频流已获取。');
      this._setupAudioAnalysis(); // 初始化音频分析（用于可视化）
      return this.stream;
    } catch (err) {
      console.error('❌ 无法访问麦克风:', err.name, err.message);
      throw new Error(`麦克风访问被拒绝或不可用: ${err.message}`);
    }
  }

  /**
   * 初始化 Web Audio API 用于实时频率分析（可视化）
   * @private
   */
  _setupAudioAnalysis() {
    if (!this.stream) return;
    try {
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const source = this.audioContext.createMediaStreamSource(this.stream);
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 256;
      const bufferLength = this.analyser.frequencyBinCount;
      this.dataArray = new Uint8Array(bufferLength);
      source.connect(this.analyser);
    } catch (e) {
      console.warn('Web Audio API 初始化失败，将不影响录音，仅影响可视化:', e);
    }
  }

  /**
   * 获取当前音频频率数据，用于绘制波形
   * @returns {Uint8Array} 频率数据数组
   */
  getAudioFrequencyData() {
    if (this.analyser && this.dataArray) {
      this.analyser.getByteFrequencyData(this.dataArray);
      return this.dataArray;
    }
    return new Uint8Array(0);
  }

  /**
   * 开始录制音频
   * @param {Function} onDataAvailable - 数据可用的回调函数，可用于实时上传
   */
  startRecording(onDataAvailable = null) {
    if (!this.stream) {
      throw new Error('请先调用 startMicrophone 获取音频流。');
    }
    // 设置录制格式，'audio/webm' 是广泛支持的格式
    const options = { mimeType: 'audio/webm; codecs=opus' };
    this.mediaRecorder = new MediaRecorder(this.stream, options);
    this.audioChunks = [];
    this.isRecording = true;

    this.mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        this.audioChunks.push(event.data);
        // 如果提供了回调，可以传递数据块（用于实时上传或分析）
        if (onDataAvailable && typeof onDataAvailable === 'function') {
          onDataAvailable(event.data);
        }
      }
    };

    this.mediaRecorder.onstop = () => {
      console.log('⏹️ 音频录制已停止。');
      this.isRecording = false;
    };

    this.mediaRecorder.start(1000); // 每隔 1000ms 触发一次 ondataavailable
    console.log('🎤 音频录制已开始。');
  }

  /**
   * 停止录制
   * @returns {Blob} 录制完成的完整音频 Blob 对象
   */
  stopRecording() {
    if (this.mediaRecorder && this.isRecording) {
      return new Promise((resolve) => {
        this.mediaRecorder.onstop = () => {
          const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
          console.log(`📦 音频录制完成，Blob 大小: ${(audioBlob.size / 1024).toFixed(2)} KB`);
          this.isRecording = false;
          this._cleanup();
          resolve(audioBlob);
        };
        this.mediaRecorder.stop();
      });
    }
    this._cleanup();
    return Promise.resolve(null);
  }

  /**
   * 清理音频资源
   * @private
   */
  _cleanup() {
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }
    if (this.audioContext && this.audioContext.state !== 'closed') {
      this.audioContext.close();
    }
    this.audioChunks = [];
  }
}

// ============================================================================
// 视频捕获类
// ============================================================================
export class VideoCapture {
  constructor(videoElement) {
    this.videoElement = videoElement;
    this.stream = null;
    this.captureInterval = null;
    this.onFrameCallback = null; // 用于处理每一帧的回调函数
  }

  /**
   * 请求摄像头权限并开始视频流
   * @param {Object} constraints - 自定义视频约束
   * @returns {Promise<MediaStream>} 视频流对象
   */
  async startCamera(constraints = {}) {
    const defaultConstraints = {
      video: {
        width: { ideal: 640 },
        height: { ideal: 480 },
        facingMode: 'user', // 前置摄像头
        frameRate: { ideal: 15 } // 适当帧率
      },
      audio: false
    };
    const finalConstraints = { ...defaultConstraints.video, ...constraints.video };

    try {
      this.stream = await navigator.mediaDevices.getUserMedia({ video: finalConstraints });
      if (this.videoElement) {
        this.videoElement.srcObject = this.stream;
        // 等待视频元数据加载
        await new Promise((resolve) => {
          this.videoElement.onloadedmetadata = () => {
            this.videoElement.play().then(resolve).catch(console.error);
          };
        });
      }
      console.log('✅ 摄像头访问成功，视频流已开始。');
      return this.stream;
    } catch (err) {
      console.error('❌ 无法访问摄像头:', err.name, err.message);
      throw new Error(`摄像头访问被拒绝或不可用: ${err.message}`);
    }
  }

  /**
   * 开始定期捕获视频帧（用于分析或上传）
   * @param {number} intervalMs - 捕获间隔（毫秒）
   * @param {Function} callback - 帧数据回调函数
   */
  startFrameCapture(intervalMs = 1000, callback) {
    this.onFrameCallback = callback;
    this.captureInterval = setInterval(() => {
      if (this.videoElement && this.videoElement.readyState >= this.videoElement.HAVE_METADATA) {
        const frameData = this.captureFrame();
        if (frameData && this.onFrameCallback) {
          this.onFrameCallback(frameData);
        }
      }
    }, intervalMs);
    console.log(`📸 开始定时捕获视频帧，间隔: ${intervalMs}ms`);
  }

  /**
   * 捕获单帧并转换为Base64（JPEG格式）
   * @returns {string} Base64编码的图片数据
   */
  captureFrame() {
    if (!this.videoElement || this.videoElement.videoWidth === 0) {
      return null;
    }
    const canvas = document.createElement('canvas');
    canvas.width = this.videoElement.videoWidth;
    canvas.height = this.videoElement.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(this.videoElement, 0, 0, canvas.width, canvas.height);
    // 转换为DataURL (Base64)，质量0.8以平衡大小和清晰度
    return canvas.toDataURL('image/jpeg', 0.8);
  }

  /**
   * 停止捕获帧
   */
  stopFrameCapture() {
    if (this.captureInterval) {
      clearInterval(this.captureInterval);
      this.captureInterval = null;
      console.log('⏹️ 已停止定时捕获视频帧。');
    }
  }

  /**
   * 停止摄像头并清理所有资源
   */
  stopCamera() {
    this.stopFrameCapture();
    if (this.stream) {
      this.stream.getTracks().forEach(track => {
        track.stop();
        console.log(`🛑 已停止轨道: ${track.kind}`);
      });
      this.stream = null;
    }
    if (this.videoElement) {
      this.videoElement.srcObject = null;
    }
    console.log('📷 摄像头已完全关闭。');
  }
}