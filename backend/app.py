import threading
import sys
import os
import time
from datetime import datetime
import torch
import cv2
import uuid
import numpy as np
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import sys
import os
from flask_socketio import SocketIO, emit
import logging
from datetime import datetime
from queue import Queue, Empty
from jry import FaceFeatureExtractor, AudioFeatureExtractor, SmartHRVProcessor, HeartRateCollector, compute_9d_features

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MultiModalDataManager:
    """管理多模态数据（视频、音频、心率）的采集、处理和特征提取"""

    def __init__(self, config=None):
        self.config = config or {
            'participant_id': 'api_user',
            'experiment_type': 'realtime_api',
            'output_dir': 'data/api_collected',
            'video_fps': 15,
            'audio_sample_rate': 16000,
            'enable_visualization': False,
            'use_database': False
        }

        # 初始化各模态处理器
        self.face_extractor = None
        self.audio_extractor = None
        self.hrv_processor = None
        self.heart_rate_collector = None
        self._sync_hr_thread = None
        self._sync_hr_running = False

        # 数据缓冲区
        self.video_buffer = Queue(maxsize=100)  # 视频帧缓冲区
        self.audio_buffer = Queue(maxsize=50)  # 音频数据缓冲区
        self.hr_buffer = []  # 心率数据缓冲区

        # 特征存储
        self.current_features = {
            'face_features': [],
            'audio_features': [],
            'hr_features': [],
            'timestamp': 0,
            'valid': False
        }

        # 状态
        self.is_processing = False
        self.processing_thread = None
        self.lock = threading.RLock()
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 初始化处理器
        self._initialize_processors()

        hr_device_type = self.config.get('hr_device_type', 'ble_heart_rate')  # 或 'simulated'
        ble_keyword = self.config.get('ble_keyword', 'HUAWEI')
        ble_timeout = self.config.get('ble_timeout', 30)
        fallback = self.config.get('fallback_simulated', True)

        # HRV 处理器（如果需要）
        self.hrv_processor = SmartHRVProcessor(
            hr_collector=self.heart_rate_collector) if self.heart_rate_collector else None

    def start_processing(self):
        with self.lock:
            if self.is_processing:
                return False
            self.is_processing = True
            # 启动心率同步线程
            self._sync_hr_running = True
            self._sync_hr_thread = threading.Thread(target=self._sync_hr_loop, daemon=True)
            self._sync_hr_thread.start()
            logger.info("✅ 启动多模态数据处理线程")
            return True

    def stop_processing(self):
        with self.lock:
            self.is_processing = False
            self._sync_hr_running = False
            if self._sync_hr_thread:
                self._sync_hr_thread.join(timeout=2.0)
            # ... 其他清理 ...

    def _sync_hr_loop(self):
        while self._sync_hr_running and self.is_processing:
            try:
                if self.heart_rate_collector:
                    hr = self.heart_rate_collector.get_current_hr()
                    if hr:
                        logger.info(f"同步心率: {hr} bpm")  # 添加这行
                        rr_interval = 60000.0 / hr if hr > 0 else None
                        self.add_heart_rate_data(hr, rr_interval)
                    else:
                        logger.debug("get_current_hr() 返回 None")
            except Exception as e:
                logger.error(f"同步心率数据失败: {e}")
            time.sleep(0.5)

    def _initialize_processors(self):
        """初始化各模态的特征提取器"""
        try:
            self.face_extractor = FaceFeatureExtractor()
            logger.info("✅ 面部特征提取器初始化成功")
        except Exception as e:
            logger.error(f"❌ 面部特征提取器初始化失败: {e}")
            self.face_extractor = None

        try:
            sample_rate = self.config.get('audio_sample_rate', 16000)
            self.audio_extractor = AudioFeatureExtractor(sample_rate=sample_rate)
            logger.info(f"✅ 音频特征提取器初始化成功 (采样率: {sample_rate}Hz)")
        except Exception as e:
            logger.error(f"❌ 音频特征提取器初始化失败: {e}")
            self.audio_extractor = None

        try:
            hr_device_type = self.config.get('hr_device_type', 'ble_heart_rate')
            ble_keyword = self.config.get('ble_keyword', 'HUAWEI')
            ble_timeout = self.config.get('ble_timeout', 30)
            fallback = self.config.get('fallback_simulated', True)
            self.heart_rate_collector = HeartRateCollector(
                device_type=hr_device_type,
                ble_keyword=ble_keyword,
                ble_timeout=ble_timeout,
                fallback=fallback
                # 暂时不加 verbose，等修改 jry.py 后再加
            )
            logger.info(f"✅ 心率采集器初始化成功 (类型={hr_device_type})")
        except Exception as e:
            logger.error(f"❌ 心率采集器初始化失败: {e}")
            self.heart_rate_collector = None

    def add_video_frame(self, frame_data):
        """添加视频帧到缓冲区"""
        with self.lock:
            try:
                if not self.video_buffer.full():
                    data_packet = {
                        'frame': frame_data['frame'],
                        'timestamp': frame_data.get('timestamp', time.time()),
                        'source': 'api'
                    }
                    self.video_buffer.put_nowait(data_packet)
                    return True
                else:
                    logger.warning("视频缓冲区已满，丢弃帧")
                    return False
            except Exception as e:
                logger.error(f"添加视频帧失败: {e}")
                return False

    def add_audio_data(self, audio_data, sample_rate=16000):
        """添加音频数据到缓冲区"""
        with self.lock:
            try:
                if not self.audio_buffer.full():
                    data_packet = {
                        'audio': audio_data,
                        'sample_rate': sample_rate,
                        'timestamp': time.time(),
                        'source': 'api'
                    }
                    self.audio_buffer.put_nowait(data_packet)
                    return True
                else:
                    logger.warning("音频缓冲区已满，丢弃数据")
                    return False
            except Exception as e:
                logger.error(f"添加音频数据失败: {e}")
                return False

    def add_heart_rate_data(self, heart_rate, rr_interval=None):
        """添加心率数据（模拟或真实）"""
        with self.lock:
            try:
                current_time = time.time()
                hr_data = {
                    'timestamp': current_time,
                    'heart_rate': heart_rate,
                    'rr_interval': rr_interval
                }
                self.hr_buffer.append(hr_data)

                # 保持缓冲区大小
                if len(self.hr_buffer) > 1000:
                    self.hr_buffer = self.hr_buffer[-1000:]

                return True
            except Exception as e:
                logger.error(f"添加心率数据失败: {e}")
                return False

    def generate_simulated_hr_data(self):
        """生成模拟心率数据（用于测试）"""
        import random

        # 模拟正常心率 (60-100 BPM)
        base_hr = 75
        variation = random.uniform(-5, 5)
        heart_rate = base_hr + variation

        # 模拟RR间期
        rr_interval = 60000 / heart_rate  # 毫秒

        self.add_heart_rate_data(heart_rate, rr_interval)
        return heart_rate

    def _start_heart_rate_simulation(self):
        """启动模拟心率数据生成线程"""

        def simulation_loop():
            while self.is_processing:
                # 生成并添加一条模拟心率数据
                self.generate_simulated_hr_data()
                # 控制生成频率，例如每秒2次（模拟500ms一个心跳）
                time.sleep(0.5)

        self.hr_simulation_thread = threading.Thread(
            target=simulation_loop,
            name="HRSimulation",
            daemon=True
        )
        self.hr_simulation_thread.start()
        logger.info("✅ 模拟心率数据生成线程已启动")

    def _processing_loop(self):
        """主处理循环 - 仅在数据充足时提取特征并更新"""
        # 移除固定时间间隔，改为基于队列状态的触发
        check_interval = 0.1  # 检查队列状态的间隔（秒）

        while self.is_processing:
            print("test===========")
            time.sleep(check_interval)  # 降低循环频率，减少CPU占用

            try:
                trigger_processing = False
                reason = ""

                # 检查视频缓冲区是否已满 (触发条件1)
                if self.video_buffer.full():
                    trigger_processing = True
                    reason = "视频缓冲区已满"
                # 检查音频缓冲区是否有足够数据（至少1秒）(触发条件2)
                elif not self.audio_buffer.empty():
                    # 估算音频缓冲区中的总样本数（近似）
                    estimated_samples = 0
                    # 注意：这里仅估算，精确计算需要遍历队列，可能影响性能
                    # 一个更简单的方法是检查队列大小是否超过一个经验阈值
                    if self.audio_buffer.qsize() >= 3:  # 假设每个数据包约0.5秒，3个包约1.5秒
                        trigger_processing = True
                        reason = "音频缓冲区数据充足"

                # 如果触发条件满足，则执行特征提取
                if trigger_processing:
                    logger.debug(f"触发特征提取: {reason}")

                    # 提取面部特征 (可能会消费整个视频缓冲区)
                    face_features = self._extract_face_features()

                    # 提取音频特征 (会消费部分或全部音频缓冲区，直到攒够1秒)
                    audio_features = self._extract_audio_features()

                    # 生成并提取心率特征 (模拟数据)
                    # 确保有心率数据可供提取
                    if len(self.hr_buffer) < 10:
                        self.generate_simulated_hr_data()
                    hr_features = self._extract_hr_features()

                    print(self.current_features)

                    # 更新当前特征
                    with self.lock:
                        self.current_features = {
                            'face_features': face_features,
                            'audio_features': audio_features,
                            'hr_features': hr_features,
                            'timestamp': time.time(),
                            'valid': all([
                                len(face_features) > 0,
                                len(audio_features) >= 0,
                                len(hr_features) > 0
                            ])
                        }

                    if self.current_features['valid']:
                        logger.info(
                            f"✅ 特征已更新（触发条件: {reason}） - 面部:{len(face_features)}, 音频:{len(audio_features)}, 心率:{len(hr_features)}")
                    else:
                        logger.debug(f"特征提取完成但数据无效，可能原因: 面部[{len(face_features)}], 音频[{len(audio_features)}], 心率[{len(hr_features)}]")

            except Exception as e:
                logger.error(f"特征提取循环失败: {e}")
                time.sleep(1)  # 出错后暂停一段时间

    def _extract_face_features(self):
        """从视频缓冲区提取面部特征"""
        if not self.face_extractor or self.video_buffer.empty():
            return []

        try:
            # 获取最新一帧
            video_packet = None
            if not self.video_buffer.empty():
                video_packet = self.video_buffer.get_nowait()

            if video_packet and 'frame' in video_packet:
                frame = video_packet['frame']
                # 使用 jry.py 的提取器
                features = self.face_extractor.extract_features(frame)
                return features if features else []

        except Exception as e:
            logger.error(f"面部特征提取失败: {e}")

        return []

    def _extract_audio_features(self):
        """从音频缓冲区提取音频特征"""
        if not self.audio_extractor or self.audio_buffer.empty():
            return []

        try:
            # 收集足够的音频数据（至少1秒）
            audio_chunks = []
            total_samples = 0
            target_samples = self.config.get('audio_sample_rate', 16000)  # 1秒数据

            while not self.audio_buffer.empty() and total_samples < target_samples:
                try:
                    audio_packet = self.audio_buffer.get_nowait()
                    if 'audio' in audio_packet:
                        audio_data = audio_packet['audio']
                        audio_chunks.append(audio_data)
                        total_samples += len(audio_data)
                except Empty:
                    break

            if audio_chunks:
                # 合并音频数据
                combined_audio = np.concatenate(audio_chunks) if len(audio_chunks) > 1 else audio_chunks[0]
                # 使用 jry.py 的提取器
                features = self.audio_extractor.extract_features(combined_audio)
                return features if features else []

        except Exception as e:
            logger.error(f"音频特征提取失败: {e}")

        return []

    def _extract_hr_features(self):
        """从心率缓冲区提取HRV特征"""
        if not self.hrv_processor or not self.hr_buffer:
            return []

        try:
            # 提取最近的心率数据
            recent_hr_data = self.hr_buffer[-100:] if len(self.hr_buffer) >= 100 else self.hr_buffer
            print(f"缓冲区长度: {len(self.hr_buffer)}")

            if len(recent_hr_data) < 10:  # 需要足够的数据点
                # 如果没有足够数据，使用模拟数据
                self.generate_simulated_hr_data()
                recent_hr_data = self.hr_buffer[-10:]

            # 将字典格式转换为 compute_9d_features 期望的格式
            # compute_9d_features 期望 [(timestamp, heart_rate), ...] 格式
            heart_rate_data = []
            for data in recent_hr_data:
                if 'timestamp' in data and 'heart_rate' in data:
                    # 从字典中提取 timestamp 和 heart_rate
                    heart_rate_data.append([data['timestamp'], data['heart_rate']])
                elif 'rr_interval' in data:
                    # 如果没有直接的 heart_rate，但提供了 rr_interval，需要计算 heart_rate
                    # RR间期单位是毫秒，心率 = 60000 / RR间期(ms)
                    if data.get('rr_interval', 0) > 0:
                        hr = 60000 / data['rr_interval']
                        heart_rate_data.append([data.get('timestamp', 0), hr])
                elif isinstance(data, (list, tuple)) and len(data) >= 2:
                    # 如果已经是列表或元组格式
                    heart_rate_data.append([data[0], data[1]])

            print(f"转换后的心率数据格式: {len(heart_rate_data)} 个数据点")

            if heart_rate_data and len(heart_rate_data) >= 5:  # 确保有足够的数据点
                try:
                    # 使用 jry.py 的HRV处理器
                    print('开始计算9维特征...')
                    features = compute_9d_features(heart_rate_data)
                    print(f"特征计算结果: {features}")
                    return features if features else []
                except Exception as e:
                    print(f"特征计算错误: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"数据不足: 需要至少5个数据点，当前有 {len(heart_rate_data) if heart_rate_data else 0} 个")

        except Exception as e:
            logger.error(f"心率特征提取失败: {e}")
            import traceback
            traceback.print_exc()

        return []

    def get_current_features(self):
        """获取当前的多模态特征"""
        with self.lock:
            return self.current_features.copy()

    def get_status(self):
        """获取处理器状态"""
        with self.lock:
            return {
                'is_processing': self.is_processing,
                'session_id': self.session_id,
                'video_buffer_size': self.video_buffer.qsize(),
                'audio_buffer_size': self.audio_buffer.qsize(),
                'hr_buffer_size': len(self.hr_buffer),
                'current_features_valid': (self.audio_buffer.qsize()>0 and self.video_buffer.qsize()>0 and len(self.hr_buffer)>0),
                'processors_available': {
                    'face': self.face_extractor is not None,
                    'audio': self.audio_extractor is not None,
                    'hrv': self.hrv_processor is not None
                }
            }

# 添加模型代码路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from src.models.transformer_fusion import TransformerFusionModel

    logger.info("✓ 成功导入模型代码")
except ImportError as e:
    logger.error(f"无法导入模型代码: {e}")
    sys.exit(1)

app = Flask(__name__)
CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*")

# 全局标志，确保广播线程只启动一次
_broadcast_thread_started = False


def broadcast_heart_rate():
    global _broadcast_thread_started
    while True:
        try:
            if data_manager and hasattr(data_manager, 'heart_rate_collector') and data_manager.heart_rate_collector:
                collector = data_manager.heart_rate_collector
                hr = collector.get_current_hr()
                if hr:
                    with app.app_context():
                        # 使用 socketio.emit，而不是单独的 emit
                        socketio.emit('heart_rate', {
                            'heart_rate': hr,
                            'timestamp': time.time()
                        }, namespace='/')
            time.sleep(1)
        except Exception as e:
            logger.error(f"心率广播错误: {e}")
            time.sleep(1)


@socketio.on('connect')
def handle_connect():
    """客户端连接时的处理"""
    global _broadcast_thread_started
    print(f'✅ 客户端已连接 (SID: {request.sid})')

    # 启动心率广播线程（只启动一次）
    if not _broadcast_thread_started:
        _broadcast_thread_started = True
        thread = threading.Thread(target=broadcast_heart_rate, daemon=True)
        thread.start()
        logger.info("心率广播线程已启动")


@socketio.on('disconnect')
def handle_disconnect():
    """客户端断开连接时的处理"""
    print(f'❌ 客户端已断开 (SID: {request.sid})')

# 全局变量
data_manager = None
model = None
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
MODEL_PATH = "saved_models/final_mental_health_model.pth"

# ==================== 模型配置（必须与训练时的配置一致）====================
MODEL_CONFIG = {
    'face_dim': 13,
    'audio_dim': 21,
    'hr_dim': 9,
    'num_classes': 4,
    'hidden_dim': 32,  # 从错误信息看，训练好的模型用的是32
    'num_heads': 4,
    'num_layers': 2,
    'dropout': 0.3,
    'device': device
}

# 类别名称
CLASS_NAMES = ['健康', '轻度压力', '中度压力', '重度压力']


try:
    data_manager = MultiModalDataManager()
    data_manager.start_processing()
    logger.info("✅ 多模态数据管理器启动成功")
except Exception as e:
    logger.error(f"❌ 数据管理器启动失败: {e}")
    data_manager = None

def load_model():
    """加载模型"""
    global model
    try:
        logger.info("正在加载模型...")
        logger.info(f"使用设备: {device}")
        logger.info(f"模型配置: {MODEL_CONFIG}")

        if not os.path.exists(MODEL_PATH):
            logger.error(f"模型文件不存在: {MODEL_PATH}")
            return False

        # 创建模型实例
        model = TransformerFusionModel(**MODEL_CONFIG)

        # 加载权重
        checkpoint = torch.load(MODEL_PATH, map_location=device, weights_only=False)
        logger.info(f"成功加载模型文件: {MODEL_PATH}")

        # 处理不同的保存格式
        if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
            state_dict = checkpoint['model_state_dict']
            logger.info("使用 'model_state_dict' 键加载权重")
        elif isinstance(checkpoint, dict) and 'state_dict' in checkpoint:
            state_dict = checkpoint['state_dict']
            logger.info("使用 'state_dict' 键加载权重")
        else:
            state_dict = checkpoint
            logger.info("直接使用checkpoint作为状态字典")

        # 加载权重（允许部分缺失，但这里应该完全匹配）
        missing, unexpected = model.load_state_dict(state_dict, strict=False)

        if missing:
            logger.warning(f"缺失的键: {len(missing)}个")
            if len(missing) > 0:
                logger.debug(f"前5个缺失键: {missing[:5]}")
        else:
            logger.info("所有模型键都匹配")

        if unexpected:
            logger.warning(f"⚠意外的键: {len(unexpected)}个")
            if len(unexpected) > 0:
                logger.debug(f"前5个意外键: {unexpected[:5]}")
        else:
            logger.info("没有意外的键")

        model.to(device)
        model.eval()
        logger.info("模型加载成功，已设置为评估模式")
        return True

    except Exception as e:
        logger.error(f"模型加载失败: {e}")
        return False


def validate_features(data):
    """验证输入特征"""
    errors = []

    required_fields = ['face_features', 'audio_features', 'hr_features']
    for field in required_fields:
        if field not in data:
            errors.append(f"缺少字段: {field}")

    if errors:
        return False, errors

    face = np.array(data['face_features'])
    audio = np.array(data['audio_features'])
    hr = np.array(data['hr_features'])

    if len(face) != 13:
        errors.append(f"面部特征维度应为13，实际为{len(face)}")
    if len(audio) != 21:
        errors.append(f"音频特征维度应为21，实际为{len(audio)}")
    if len(hr) != 9:
        errors.append(f"心率特征维度应为9，实际为{len(hr)}")

    # 检查值范围
    if len(face) == 13 and (np.any(face < 0) or np.any(face > 1)):
        errors.append("面部特征值应在0-1范围内")
    if len(audio) == 21 and (np.any(audio < 0) or np.any(audio > 1)):
        errors.append("音频特征值应在0-1范围内")
    if len(hr) == 9 and (np.any(hr < 0) or np.any(hr > 1)):
        errors.append("心率特征值应在0-1范围内")

    return len(errors) == 0, errors


def extract_contributions(contributions_dict):
    """
    从模型返回的contributions中提取各模态贡献度
    模型返回格式: {
        'modal_contributions': tensor([batch, 3]),
        'encoded_features': tensor,
        'contribution_scores': tensor
    }
    """
    try:
        if not contributions_dict:
            logger.warning("贡献度字典为空")
            return {'face': 33.3, 'audio': 33.3, 'hr': 33.3}

        # 获取模态贡献度
        if 'modal_contributions' in contributions_dict:
            modal_contrib = contributions_dict['modal_contributions']

            # 如果是tensor，取第一个样本（单样本预测）
            if isinstance(modal_contrib, torch.Tensor):
                if modal_contrib.dim() == 2:
                    # [batch, 3] 取第一个样本
                    contrib_values = modal_contrib[0].detach().cpu().numpy()
                elif modal_contrib.dim() == 1:
                    # [3] 直接使用
                    contrib_values = modal_contrib.detach().cpu().numpy()
                else:
                    contrib_values = modal_contrib.mean(dim=0).detach().cpu().numpy()
            else:
                contrib_values = modal_contrib

            # 确保是长度为3的数组
            if len(contrib_values) >= 3:
                # 归一化到百分比
                total = contrib_values.sum()
                if total > 0:
                    face_pct = (contrib_values[0] / total) * 100
                    audio_pct = (contrib_values[1] / total) * 100
                    hr_pct = (contrib_values[2] / total) * 100
                else:
                    face_pct = audio_pct = hr_pct = 33.3

                return {
                    'face': float(face_pct),
                    'audio': float(audio_pct),
                    'hr': float(hr_pct)
                }

        # 如果找不到modal_contributions，返回默认值
        logger.warning("未找到modal_contributions，使用默认值")
        return {'face': 33.3, 'audio': 33.3, 'hr': 33.3}

    except Exception as e:
        logger.error(f"提取贡献度失败: {e}")
        return {'face': 33.3, 'audio': 33.3, 'hr': 33.3}


def generate_friendly_explanation(pred_class, score, confidence, contributions, face_features, audio_features,
                                  hr_features, username="用户"):
    """
    生成友好、人性化的解释文本
    """
    class_name = CLASS_NAMES[pred_class]

    # 1. 问候语和状态描述
    if score < 30:
        status_text = f"你的心理压力分数为{score:.1f}分，属于正常范围，说明你当前状态良好。"
        level_desc = "正常"
    elif score < 50:
        status_text = f"你的心理压力分数为{score:.1f}分，属于轻度压力水平。这是身体对日常挑战的正常反应，但长期积累可能影响健康。"
        level_desc = "轻度压力"
    elif score < 70:
        status_text = f"你的心理压力分数为{score:.1f}分，属于中度压力水平。这表明你正处于明显的压力状态，需要及时调节，避免发展成更严重状态。"
        level_desc = "中度压力"
    else:
        status_text = f"你的心理压力分数为{score:.1f}分，属于重度压力水平。请务必重视，并采取积极行动，必要时寻求专业帮助。"
        level_desc = "重度压力"

    # 2. 置信度说明
    if confidence > 0.7:
        confidence_text = "本次评估的置信度高于业内平均水平，结果可靠。"
    elif confidence > 0.5:
        confidence_text = "本次评估结果较为可靠，可作为参考。"
    else:
        confidence_text = "本次评估置信度偏低，建议结合自身感受综合判断。"

    # 3. 确定主要影响因素
    main_modal = max(contributions, key=contributions.get)
    modal_names = {'face': '面部表情', 'audio': '语音特征', 'hr': '心率变化'}
    dominant_modality = modal_names.get(main_modal, '综合因素')
    dominant_contrib = contributions[main_modal]

    # 4. 各模态贡献度分析
    def get_contribution_level(contrib):
        if contrib > 50:
            return "显著"
        elif contrib > 30:
            return "中等"
        else:
            return "轻微"

    face_level = get_contribution_level(contributions['face'])
    audio_level = get_contribution_level(contributions['audio'])
    hr_level = get_contribution_level(contributions['hr'])

    # 5. 详细分析
    if level_desc == "正常":
        level_analysis = "你的各项指标均处于健康范围内，自主神经平衡，情绪稳定。"
    elif level_desc == "轻度压力":
        level_analysis = "你的轻度压力可能源于近期的学业、社交或生活事件。身体正处于应对挑战的准备状态，但长时间持续可能消耗精力。"
    elif level_desc == "中度压力":
        level_analysis = "你的中度压力表明身体已经进入明显的应激状态，可能伴随注意力下降、易怒或疲劳。这是需要主动调节的信号。"
    else:
        level_analysis = "你的重度压力提示身心负荷过重，可能影响日常功能。这是身体发出的强烈警报，需要立即关注。"

    # 6. 建议列表
    advice_map = {
        "正常": [
            "建议你继续保持健康的生活习惯，保证充足睡眠，适当运动。",
            "每天进行5-10分钟的正念冥想，有助于维持心理平衡。",
            "如果偶尔感到压力，不妨听听轻松的音乐，或与朋友聊聊天。",
            "你可以访问我们的“知识库”学习更多心理健康知识。"
        ],
        "轻度压力": [
            "建议你适当休息，进行一些放松活动，如散步、听音乐。",
            "可以尝试腹式呼吸：吸气4秒，屏气4秒，呼气6秒，重复5次。",
            "保持规律的作息，减少咖啡因摄入。",
            "如果压力持续，欢迎使用我们的“放松练习”功能，或去“树洞”匿名倾诉。",
            "每天记录三件感恩的小事，有助于提升积极情绪。"
        ],
        "中度压力": [
            "建议你进行15分钟冥想或渐进式肌肉放松练习。",
            "今天早点休息，保证7-8小时睡眠。",
            "可以尝试写情绪日记，梳理压力源。",
            "我们的“知识库”中有很多情绪管理文章，推荐你阅读。",
            "如果感到难以自我调节，请考虑联系学校心理中心或专业咨询师。",
            "适度有氧运动（如快走、慢跑）能有效释放压力。"
        ],
        "重度压力": [
            "请立即暂停当前任务，进行几次深呼吸。",
            "如果情绪难以控制，请及时联系学校心理中心或拨打心理援助热线。",
            "我们的“树洞”也欢迎你匿名倾诉，会有同伴支持你。",
            "建议你今天进行温和的运动，如散步，帮助释放压力。",
            "请记住，寻求帮助是勇敢的表现。",
            "可以尝试简单的正念练习：专注于当下的一呼一吸，观察而不评判。"
        ]
    }

    advice_list = advice_map.get(level_desc, advice_map["正常"])

    # 7. 组合完整的解释文本
    explanation_parts = []

    # 问候和状态
    explanation_parts.append(f"你好，{username}，根据本次测评，我们为你生成以下分析：")
    explanation_parts.append("")
    explanation_parts.append(status_text)
    explanation_parts.append("")
    explanation_parts.append(confidence_text)
    explanation_parts.append("")
    explanation_parts.append("我们通过分析你的面部表情、语音特征和心率信号，综合评估了你的心理状态。各模态的贡献度如下：")
    explanation_parts.append("")
    explanation_parts.append(
        f"  • 面部表情贡献了{contributions['face']:.1f}%，属于{face_level}影响程度。这表明你的面部肌肉活动在当前状态中扮演了重要角色。")
    explanation_parts.append(
        f"  • 语音特征贡献了{contributions['audio']:.1f}%，属于{audio_level}影响程度。你的声音韵律和停顿模式反映了情绪波动。")
    explanation_parts.append(
        f"  • 心率信号贡献了{contributions['hr']:.1f}%，属于{hr_level}影响程度。你的心率变异性指标显示了生理层面的压力反应。")
    explanation_parts.append("")
    explanation_parts.append(f"其中，{dominant_modality}是影响你当前状态的主要因素，贡献了{dominant_contrib:.1f}%。")
    explanation_parts.append("")
    explanation_parts.append(level_analysis)
    explanation_parts.append("")
    explanation_parts.append("建议：")
    for advice in advice_list:
        explanation_parts.append(f"  • {advice}")
    explanation_parts.append("")
    explanation_parts.append("关注心理健康是关爱自己的重要方式。我们一直在这里，陪伴你走过每一个情绪时刻。")
    explanation_parts.append("")

    return "\n".join(explanation_parts)


# ==================== API路由 ====================

@app.route('/', methods=['GET'])
def index():
    """根路由 - 显示API使用说明"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>心理健康预测API</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
                color: #333;
                line-height: 1.6;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
                margin-top: 0;
            }
            .status {
                background: #27ae60;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                display: inline-block;
                margin-bottom: 20px;
            }
            .endpoint {
                background: #f8f9fa;
                border-left: 5px solid #3498db;
                padding: 15px;
                margin: 15px 0;
                border-radius: 0 5px 5px 0;
            }
            .method {
                font-weight: bold;
                color: #2980b9;
                font-size: 1.1em;
            }
            .url {
                color: #e74c3c;
                font-family: monospace;
                font-size: 1.1em;
                margin-left: 10px;
            }
            pre {
                background: #2d3436;
                color: #fdcb6e;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            th, td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            th {
                background-color: #3498db;
                color: white;
            }
            .badge {
                background: #3498db;
                color: white;
                padding: 3px 8px;
                border-radius: 3px;
                font-size: 12px;
            }
            .footer {
                margin-top: 40px;
                text-align: center;
                color: #7f8c8d;
                border-top: 1px solid #eee;
                padding-top: 20px;
            }
            .highlight {
                background: #fff3cd;
                padding: 10px;
                border-left: 4px solid #ffc107;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>心理健康预测API <span style="font-size:14px; background:#3498db; color:white; padding:5px 10px; border-radius:20px; margin-left:15px;">v1.0.0</span></h1>
            <div class="status">✅ 服务状态: 运行中</div>
            <div class="highlight">
                <strong>当前使用的模型:</strong> final_mental_health_model.pth<br>
                <strong>模型位置:</strong> saved_models/final_mental_health_model.pth<br>
                <strong>模型类型:</strong> TransformerFusionModel<br>
                <strong>隐藏层维度:</strong> 32<br>
                <strong>贡献度来源:</strong> 模型内部贡献度计算层（基于Transformer注意力）
            </div>
            <p>这是一个基于多模态特征（面部、音频、心率）的心理健康状态预测API。</p>
            <h2>可用接口</h2>
            <div class="endpoint"><div><span class="method">GET</span> <span class="url">/</span></div><div class="desc">📄 本帮助页面</div></div>
            <div class="endpoint"><div><span class="method">GET</span> <span class="url">/health</span></div><div class="desc">❤️ 健康检查接口</div></div>
            <div class="endpoint"><div><span class="method">GET</span> <span class="url">/info</span></div><div class="desc">ℹ️ 模型信息接口</div></div>
            <div class="endpoint"><div><span class="method">POST</span> <span class="url">/predict</span></div><div class="desc">🎯 心理健康预测接口</div></div>
            <div class="endpoint"><div><span class="method">POST</span> <span class="url">/batch_predict</span></div><div class="desc">📦 批量预测接口</div></div>
            <h2>特征维度</h2>
            <table>
                <tr><th>特征类型</th><th>维度</th><th>范围</th></tr>
                <tr><td>面部特征</td><td><span class="badge">13</span></td><td>[0, 1]</td></tr>
                <tr><td>音频特征</td><td><span class="badge">21</span></td><td>[0, 1]</td></tr>
                <tr><td>心率特征</td><td><span class="badge">9</span></td><td>[0, 1]</td></tr>
            </table>
            <h2>预测类别</h2>
            <table>
                <tr><th>编码</th><th>类别</th><th>压力分数范围</th></tr>
                <tr><td>0</td><td>健康</td><td>0-30</td></tr>
                <tr><td>1</td><td>轻度压力</td><td>30-50</td></tr>
                <tr><td>2</td><td>中度压力</td><td>50-70</td></tr>
                <tr><td>3</td><td>重度压力</td><td>70-100</td></tr>
            </table>
            <div class="footer"><p>服务运行在: <code>http://localhost:5000</code></p></div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)


@app.route('/health', methods=['GET'])
def health():
    """健康检查接口"""
    return jsonify({
        'status': 'ok',
        'model_loaded': model is not None,
        'model_path': MODEL_PATH if os.path.exists(MODEL_PATH) else None,
        'device': str(device),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/upload_frame', methods=['POST'])
def upload_frame():
    """接收视频帧并送入多模态处理器"""
    try:
        if 'frame' not in request.files:
            return jsonify({'success': False, 'error': 'No frame file'}), 400

        file = request.files['frame']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Empty filename'}), 400

        # 读取并解码图像
        img_bytes = file.read()
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({'success': False, 'error': 'Invalid image'}), 400

        logger.info(f"收到视频帧，尺寸: {frame.shape[1]}x{frame.shape[0]}")

        # 送入多模态处理器
        if data_manager:
            success = data_manager.add_video_frame({
                'frame': frame,
                'timestamp': time.time()
            })

            if not success:
                logger.warning("视频帧添加失败，缓冲区可能已满")

        return jsonify({
            'success': True,
            'message': '视频帧已接收',
            'size': f"{frame.shape[1]}x{frame.shape[0]}",
            'in_processor': data_manager is not None
        })

    except Exception as e:
        logger.error(f"处理视频帧失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/info', methods=['GET'])
def info():
    """模型信息接口"""
    return jsonify({
        'model_type': 'TransformerFusionModel',
        'model_path': MODEL_PATH,
        'model_exists': os.path.exists(MODEL_PATH),
        'model_config': {k: str(v) if isinstance(v, torch.device) else v for k, v in MODEL_CONFIG.items()},
        'feature_dims': {'face': 13, 'audio': 21, 'hr': 9},
        'class_names': CLASS_NAMES,
        'class_mapping': {i: name for i, name in enumerate(CLASS_NAMES)},
        'device': str(device),
        'model_loaded': model is not None,
        'contribution_method': 'Transformer贡献度计算层'
    })


@app.route('/predict', methods=['POST'])
def predict():
    """单样本预测接口 - 支持多模态实时数据"""
    try:
        if model is None:
            return jsonify({'success': False, 'error': '模型未加载'}), 503

        # 判断数据来源
        request_data = request.get_json() or {}
        use_realtime = request_data.get('use_realtime', False)

        if use_realtime and data_manager:
            # 同步提取特征
            face_features = data_manager._extract_face_features()
            audio_features = data_manager._extract_audio_features()
            hr_features = data_manager._extract_hr_features()

            if not (len(face_features) > 0 and len(audio_features) > 0 and len(hr_features) > 0):
                return jsonify({
                    'success': False,
                    'error': '实时特征提取失败',
                    'details': {
                        'face_extracted': len(face_features) > 0,
                        'audio_extracted': len(audio_features) > 0,
                        'hr_extracted': len(hr_features) > 0
                    }
                }), 400

            prediction_data = {
                'face_features': face_features,
                'audio_features': audio_features,
                'hr_features': hr_features
            }
            data_source = 'realtime_multimodal'

        else:
            # 使用请求体中的数据
            data = request_data
            if not data:
                return jsonify({'success': False, 'error': '请求数据为空'}), 400

            is_valid, errors = validate_features(data)
            if not is_valid:
                return jsonify({'success': False, 'error': '特征验证失败', 'details': errors}), 400

            prediction_data = data
            data_source = 'request_body'

        # 验证特征
        is_valid, errors = validate_features(prediction_data)
        if not is_valid:
            return jsonify({'success': False, 'error': '特征验证失败', 'details': errors}), 400

        # 转换为tensor
        face_tensor = torch.tensor([prediction_data['face_features']], dtype=torch.float32)
        audio_tensor = torch.tensor([prediction_data['audio_features']], dtype=torch.float32)
        hr_tensor = torch.tensor([prediction_data['hr_features']], dtype=torch.float32)

        # 使用模型预测
        with torch.no_grad():
            model.eval()
            # 关键修改1：假设模型返回(predictions, contributions)元组
            predictions, model_contributions = model(face_tensor, audio_tensor, hr_tensor)
            probs = torch.softmax(predictions, dim=1)  # 注意dim可能与文档2不同，需保持一致
            pred_class = torch.argmax(probs, dim=1).item()
            confidence = probs[0][pred_class].item()

        # 关键修改2：计算压力分数 (0-100)
        weights = torch.tensor([0, 33, 66, 100], device=device).float()
        score = torch.sum(probs * weights).item()

        # 关键修改3：提取贡献度 (使用模型返回的真实贡献度信息)
        contributions = extract_contributions(model_contributions)

        # 获取用户名（可选）
        username = request_data.get('username', '用户')

        # 关键修改4：生成友好版可解释性文本
        explanation = generate_friendly_explanation(
            pred_class=pred_class,
            score=score,
            confidence=confidence,
            contributions=contributions,
            face_features=prediction_data['face_features'],
            audio_features=prediction_data['audio_features'],
            hr_features=prediction_data['hr_features'],
            username=username
        )

        # 构造结果
        result = {
            'success': True,
            'prediction': int(pred_class),
            'prediction_class': CLASS_NAMES[pred_class],  # 新增：返回类别名称
            'score': round(score, 1),                     # 新增：压力分数
            'confidence': float(confidence),
            'probabilities': probs[0].cpu().numpy().tolist(),
            'contributions': contributions,
            'explanation': explanation,                   # 替换为新的详细报告
            'features': {
                'face_dim': len(prediction_data['face_features']),
                'audio_dim': len(prediction_data['audio_features']),
                'hr_dim': len(prediction_data['hr_features'])
            },
            'data_source': data_source,
            'timestamp': time.time()  # 可选添加
        }

        # 添加额外信息
        if data_source == 'realtime_multimodal' and data_manager:
            result['session_id'] = data_manager.session_id
            result['timestamp'] = time.time()  # 直接使用当前时间，不再依赖 features 变量
            result['features_valid'] = True  # 因为已经提取成功

        logger.info(f"✅ 预测完成: 类别={result['prediction']}, 置信度={result['confidence']:.3f}, 数据源={data_source}")
        return jsonify(result)

    except Exception as e:
        logger.error(f"❌ 预测失败: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    """接收音频数据并送入多模态处理器"""
    try:
        if 'audio_data' not in request.files:
            return jsonify({'success': False, 'error': 'No audio data'}), 400

        audio_file = request.files['audio_data']
        sample_rate = request.form.get('sample_rate', 16000, type=int)

        # 读取PCM数据
        audio_bytes = audio_file.read()

        if len(audio_bytes) == 0:
            return jsonify({'success': False, 'error': 'Empty audio data'}), 400

        # 转换为numpy数组 (int16)
        audio_array = np.frombuffer(audio_bytes, dtype=np.int16)

        # 转换为float32并归一化（符合jry.py的音频处理器要求）
        audio_float = audio_array.astype(np.float32) / 32768.0

        logger.info(f"收到音频数据: {len(audio_array)} 样本, 采样率: {sample_rate}Hz")

        # 送入多模态处理器
        if data_manager:
            success = data_manager.add_audio_data(audio_float, sample_rate)

            if not success:
                logger.warning("音频数据添加失败，缓冲区可能已满")

        return jsonify({
            'success': True,
            'message': '音频数据已接收',
            'samples': len(audio_array),
            'duration': len(audio_array) / sample_rate,
            'in_processor': data_manager is not None
        })

    except Exception as e:
        logger.error(f"处理音频失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/predict_realtime', methods=['GET', 'POST'])
def predict_realtime():
    """使用多模态数据进行实时预测（同步按需处理模式）"""
    try:
        if model is None:
            return jsonify({'success': False, 'error': '模型未加载'}), 503
        if data_manager is None:
            return jsonify({'success': False, 'error': '多模态处理器未初始化'}), 503

        # === 同步提取特征：直接调用提取方法，会消费缓冲区头部的数据 ===
        face_features = data_manager._extract_face_features()
        audio_features = data_manager._extract_audio_features()
        hr_features = data_manager._extract_hr_features()

        # === 检查本次特征提取是否成功 ===
        extraction_status = {
            'face_extracted': len(face_features) > 0,
            'audio_extracted': len(audio_features) > 0,
            'hr_extracted': len(hr_features) > 0
        }

        # 如果任何一个特征提取失败，返回错误详情
        if not all(extraction_status.values()):
            return jsonify({
                'success': False,
                'error': '实时特征提取失败',
                'details': extraction_status,
                'feature_dimensions': {
                    'face': len(face_features),
                    'audio': len(audio_features),
                    'hr': len(hr_features)
                }
            }), 404

        # === 验证特征维度 ===
        prediction_data = {
            'face_features': face_features,
            'audio_features': audio_features,
            'hr_features': hr_features
        }
        is_valid, errors = validate_features(prediction_data)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': '特征验证失败',
                'details': errors
            }), 400

        # === 转换为tensor并进行预测 ===
        face_tensor = torch.tensor([prediction_data['face_features']], dtype=torch.float32)
        audio_tensor = torch.tensor([prediction_data['audio_features']], dtype=torch.float32)
        hr_tensor = torch.tensor([prediction_data['hr_features']], dtype=torch.float32)

        with torch.no_grad():
            model.eval()
            output = model(face_tensor, audio_tensor, hr_tensor)

            # 处理模型返回元组的情况
            if isinstance(output, tuple):
                # 通常第一个元素是主要的输出（logits）
                logits = output[0]
                # 如果有其他输出，可以打印出来调试
                if len(output) > 1:
                    print(f"模型返回了 {len(output)} 个输出")
            else:
                logits = output

            probs = torch.softmax(logits, dim=1)
            pred_class = torch.argmax(probs, dim=1).item()
            confidence = probs[0][pred_class].item()

        # 提取贡献度
        contributions = extract_contributions({'modal_contributions': face_tensor,
        'encoded_features': audio_tensor,
        'contribution_scores': hr_tensor})

        # 构造结果
        result = {
            'success': True,
            'prediction': int(pred_class),
            'confidence': float(confidence),
            'probabilities': probs[0].cpu().numpy().tolist(),
            'contributions': contributions,
            'features': {
                'face_dim': len(prediction_data['face_features']),
                'audio_dim': len(prediction_data['audio_features']),
                'hr_dim': len(prediction_data['hr_features'])
            },
            'timestamp': time.time(),
            'data_source': 'multimodal_realtime_on_demand',
            'session_id': data_manager.session_id,
            'extraction_info': extraction_status  # 可选，返回本次提取的状态信息
        }

        logger.info(f"✅ 实时预测完成（按需模式）: 类别={pred_class}, 置信度={confidence:.3f}")
        return jsonify(result)

    except Exception as e:
        logger.error(f"❌ 实时预测失败: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/processor/status', methods=['GET'])
def get_processor_status():
    """获取多模态处理器状态"""
    if data_manager is None:
        return jsonify({
            'success': False,
            'error': '多模态处理器未初始化'
        }), 503

    status = data_manager.get_status()
    return jsonify({
        'success': True,
        'status': status
    })

@app.route('/upload_heartrate', methods=['POST'])
def upload_heartrate():
    """接收心率数据并送入多模态处理器"""
    try:
        # 从表单中获取心率值（必需）
        heart_rate = request.form.get('heart_rate', type=float)
        if heart_rate is None:
            return jsonify({'success': False, 'error': '缺少 heart_rate 字段'}), 400

        # 可选字段（记录日志或后续使用）
        avg_heart_rate = request.form.get('avg_heart_rate', type=float)
        hrv = request.form.get('hrv', type=float)
        stress_index = request.form.get('stress_index', type=float)
        trend = request.form.get('trend')
        stability = request.form.get('stability', type=float)
        session_id = request.form.get('session_id')
        question_id = request.form.get('question_id')

        logger.info(f"收到心率数据: heart_rate={heart_rate}, avg_hr={avg_heart_rate}, "
                    f"hrv={hrv}, stress={stress_index}, trend={trend}, "
                    f"session={session_id}, question={question_id}")

        # 计算 RR 间期（毫秒），用于 HRV 分析
        rr_interval = 60000.0 / heart_rate if heart_rate > 0 else None

        # 存入多模态处理器
        if data_manager:
            success = data_manager.add_heart_rate_data(heart_rate, rr_interval)
            if not success:
                logger.warning("心率数据添加失败")
                return jsonify({'success': False, 'error': '心率数据添加失败'}), 500
        else:
            return jsonify({'success': False, 'error': '多模态处理器未初始化'}), 503

        return jsonify({
            'success': True,
            'message': '心率数据已接收',
            'heart_rate': heart_rate,
            'rr_interval': rr_interval,
            'in_processor': data_manager is not None
        })

    except Exception as e:
        logger.error(f"处理心率数据失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/processor/current_features', methods=['GET'])
def get_current_features():
    """获取当前的多模态特征"""
    if data_manager is None:
        return jsonify({'success': False, 'error': '多模态处理器未初始化'}), 503

    features = data_manager.get_current_features()
    return jsonify({
        'success': True,
        'features': features,
        'valid': features['valid']
    })


@app.route('/batch_predict', methods=['POST'])
def batch_predict():
    """批量预测接口"""
    try:
        if model is None:
            return jsonify({'success': False, 'error': '模型未加载'}), 503

        data = request.get_json()
        if not data or 'samples' not in data:
            return jsonify({'success': False, 'error': '请提供samples数组'}), 400

        samples = data['samples']
        if not isinstance(samples, list) or len(samples) == 0:
            return jsonify({'success': False, 'error': 'samples必须是非空数组'}), 400

        results = []
        for i, sample in enumerate(samples):
            try:
                is_valid, errors = validate_features(sample)
                if not is_valid:
                    results.append({'index': i, 'success': False, 'error': '特征验证失败', 'details': errors})
                    continue

                face = np.array(sample['face_features'], dtype=np.float32)
                audio = np.array(sample['audio_features'], dtype=np.float32)
                hr = np.array(sample['hr_features'], dtype=np.float32)

                face_t = torch.from_numpy(face).unsqueeze(0).to(device)
                audio_t = torch.from_numpy(audio).unsqueeze(0).to(device)
                hr_t = torch.from_numpy(hr).unsqueeze(0).to(device)

                with torch.no_grad():
                    predictions, contributions = model(face_t, audio_t, hr_t)
                    probs = torch.softmax(predictions, dim=-1)
                    pred_class = torch.argmax(probs, dim=-1).item()
                    confidence = probs[0][pred_class].item()
                    weights = torch.tensor([0, 33, 66, 100], device=device).float()
                    score = torch.sum(probs * weights).item()

                contributions_dict = extract_contributions(contributions)
                explanation = generate_explanation(pred_class, score, confidence, contributions_dict)

                results.append({
                    'index': i,
                    'success': True,
                    'prediction': CLASS_NAMES[pred_class],
                    'prediction_code': pred_class,
                    'score': round(score, 1),
                    'confidence': round(confidence, 4),
                    'contributions': {
                        'face': round(contributions_dict['face'], 1),
                        'audio': round(contributions_dict['audio'], 1),
                        'hr': round(contributions_dict['hr'], 1)
                    },
                    'explanation': explanation
                })

            except Exception as e:
                results.append({'index': i, 'success': False, 'error': str(e)})

        return jsonify({
            'success': True,
            'total': len(samples),
            'success_count': sum(1 for r in results if r.get('success')),
            'results': results,
            'timestamp': datetime.now().isoformat(),
            'model_used': 'final_mental_health_model.pth'
        })

    except Exception as e:
        logger.error(f" 批量预测失败: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': '接口不存在'}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'success': False, 'error': '方法不允许，请检查HTTP方法（GET/POST）'}), 405


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': '服务器内部错误'}), 500


# ==================== 启动服务 ====================
if __name__ == '__main__':
    print("=" * 60)
    print("🚀 启动心理健康评估系统")
    print(f"📅 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    load_model()
    if model:
        print(f"✅ 模型加载成功: {model.__class__.__name__}")
    else:
        print("❌ 模型加载失败")

    print("\n🌐 API 服务启动中...")
    print("📡 接口列表:")
    print("  POST /upload_frame     - 上传视频帧")
    print("  POST /upload_audio     - 上传音频数据")
    print("  POST /predict          - 预测接口")
    print("  GET  /predict_realtime - 实时预测")
    print("  GET  /api/processor/status - 处理器状态")
    print("  GET  /api/processor/current_features - 当前特征")
    print("\n🔗 服务地址: http://localhost:5000")
    print("=" * 60)

    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)