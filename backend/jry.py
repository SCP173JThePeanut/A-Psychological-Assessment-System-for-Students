import cv2
import numpy as np
import os
import time
from datetime import datetime
import json
import sounddevice as sd
import threading
from queue import Queue, Empty
from collections import deque
import sqlite3
from contextlib import contextmanager
import warnings
import logging
import psutil
import gc
from argparse import ArgumentParser
import librosa
import matplotlib.pyplot as plt
import asyncio
from bleak import BleakScanner, BleakClient
import requests

# ===================== 先配置日志 =====================
warnings.filterwarnings('ignore')


class EnhancedLogger:
    def __init__(self):
        self.logger = logging.getLogger("EnhancedDataCollector")
        self.logger.setLevel(logging.INFO)

        if self.logger.handlers:
            return

        os.makedirs('logs', exist_ok=True)

        file_handler = logging.FileHandler(
            os.path.join('logs', f'enhanced_collection_{datetime.now().strftime("%Y%m%d")}.log'),
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(threadName)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger


logger = EnhancedLogger().get_logger()

# ===================== BLE心率配置 =====================
HEART_RATE_SERVICE_UUID = "0000180d-0000-1000-8000-00805f9b34fb"
HEART_RATE_MEASUREMENT_UUID = "00002a37-0000-1000-8000-00805f9b34fb"
DEVICE_NAME_KEYWORD = "HUAWEI"

MAX_HEART_RATE = 200
MAX_HR_STD = 50
HR_STD_THRESHOLD = 10
MAX_SDNN = 0.15
MAX_RMSSD = 0.08
MAX_LF = 3000
MAX_HF = 2000
MAX_LF_HF = 2.0

# ===================== 后端API配置 =====================
BACKEND_URL = "http://localhost:5000/predict"
ENABLE_BACKEND = True


# ===================== MediaPipe设置函数 =====================
def setup_mediapipe():
    """设置MediaPipe，适配新版API"""
    global mp, mp_face_mesh

    mp = None
    mp_face_mesh = None

    try:
        import mediapipe as mp

        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision

        model_path = os.path.join(os.path.dirname(__file__), 'face_landmarker.task')

        if not os.path.exists(model_path):
            logger.info("下载 MediaPipe 模型文件...")
            import urllib.request
            url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
            urllib.request.urlretrieve(url, model_path)
            logger.info("模型文件下载完成")

        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=True,
            output_facial_transformation_matrixes=True,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        mp_face_mesh = vision.FaceLandmarker.create_from_options(options)
        logger.info("✅ MediaPipe 新版 API 初始化成功")
        return True

    except ImportError as e:
        logger.warning(f"MediaPipe导入失败: {e}，将使用OpenCV备用方案")
        return False
    except Exception as e:
        logger.warning(f"MediaPipe初始化失败: {e}，将使用OpenCV备用方案")
        return False


mp_available = setup_mediapipe()


# ===================== JSON序列化辅助函数 =====================
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, (np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.int32, np.int64)):
            return int(obj)
        return super().default(obj)


def convert_numpy_to_python(obj):
    if isinstance(obj, dict):
        return {key: convert_numpy_to_python(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_to_python(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_to_python(item) for item in obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.int32, np.int64)):
        return int(obj)
    else:
        return obj


# ===================== 资源管理器 =====================
class ResourceManager:
    def __init__(self):
        self.resources = []
        self.lock = threading.Lock()

    def register(self, resource, cleanup_func):
        with self.lock:
            self.resources.append((resource, cleanup_func))

    def cleanup_all(self):
        with self.lock:
            for resource, cleanup_func in reversed(self.resources):
                try:
                    cleanup_func(resource)
                except Exception as e:
                    logger.error(f"资源清理失败: {e}")
            self.resources.clear()


# ===================== 带监控的队列 =====================
class MonitoredQueue:
    def __init__(self, maxsize=0, name="queue"):
        self.queue = Queue(maxsize=maxsize)
        self.name = name
        self.dropped_count = 0
        self.lock = threading.Lock()

    def put(self, item, block=True, timeout=None):
        try:
            self.queue.put(item, block, timeout)
            return True
        except Queue.Full:
            with self.lock:
                self.dropped_count += 1
            logger.warning(f"{self.name} 队列已满，丢弃数据，总计丢弃: {self.dropped_count}")
            return False

    def get(self, block=True, timeout=None):
        return self.queue.get(block, timeout)

    def get_nowait(self):
        return self.queue.get_nowait()

    def qsize(self):
        return self.queue.qsize()

    def empty(self):
        return self.queue.empty()

    def get_stats(self):
        with self.lock:
            return {
                'size': self.queue.qsize(),
                'maxsize': self.queue.maxsize,
                'dropped': self.dropped_count
            }


# ===================== 心跳监控器 =====================
class HeartbeatMonitor:
    def __init__(self, timeout=10.0):
        self.heartbeats = {}
        self.timeout = timeout
        self.lock = threading.Lock()

    def beat(self, thread_name):
        with self.lock:
            self.heartbeats[thread_name] = time.time()

    def check_health(self):
        with self.lock:
            current_time = time.time()
            dead_threads = []
            for thread_name, last_beat in self.heartbeats.items():
                if current_time - last_beat > self.timeout:
                    dead_threads.append(thread_name)
            return dead_threads


# ===================== SmartDBManager =====================
class SmartDBManager:
    def __init__(self, db_path="data/feature_database.db"):
        self.db_path = db_path
        self._local = threading.local()
        self._lock = threading.RLock()
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()
        logger.info(f"数据库管理器初始化: {db_path}")

    def _get_connection(self):
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(self.db_path, timeout=10)
            self._local.connection.execute("PRAGMA journal_mode=WAL")
        return self._local.connection

    def _init_db(self):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feature_packets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    timestamp REAL,
                    face_features TEXT,
                    audio_features TEXT,
                    hr_features TEXT,
                    label INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    participant_id TEXT,
                    experiment_type TEXT,
                    start_time REAL,
                    end_time REAL,
                    config TEXT,
                    status TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mental_health_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    timestamp REAL,
                    stress_level REAL,
                    anxiety_level REAL,
                    fatigue_level REAL,
                    attention_score REAL,
                    mood_score REAL,
                    recommendations TEXT
                )
            ''')
            conn.commit()
            logger.info("数据库表初始化完成")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")

    @contextmanager
    def get_cursor(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e

    def save_feature_packet(self, session_id, packet):
        try:
            packet_converted = convert_numpy_to_python(packet)
            with self.get_cursor() as cursor:
                cursor.execute('''
                    INSERT INTO feature_packets 
                    (session_id, timestamp, face_features, audio_features, hr_features, label)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    session_id,
                    packet_converted.get('timestamp', time.time()),
                    json.dumps(packet_converted.get('face_features', []), cls=NumpyEncoder),
                    json.dumps(packet_converted.get('audio_features', []), cls=NumpyEncoder),
                    json.dumps(packet_converted.get('hr_features', []), cls=NumpyEncoder),
                    packet_converted.get('label')
                ))
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"保存特征包失败: {e}")
            return None

    def save_mental_health_score(self, session_id, score_data):
        try:
            score_data_converted = convert_numpy_to_python(score_data)
            with self.get_cursor() as cursor:
                cursor.execute('''
                    INSERT INTO mental_health_scores 
                    (session_id, timestamp, stress_level, anxiety_level, 
                     fatigue_level, attention_score, mood_score, recommendations)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session_id,
                    score_data_converted.get('timestamp', time.time()),
                    score_data_converted.get('stress_level', 0),
                    score_data_converted.get('anxiety_level', 0),
                    score_data_converted.get('fatigue_level', 0),
                    score_data_converted.get('attention_score', 0),
                    score_data_converted.get('mood_score', 0),
                    json.dumps(score_data_converted.get('recommendations', []), cls=NumpyEncoder)
                ))
        except Exception as e:
            logger.error(f"保存心理健康评分失败: {e}")

    def close(self):
        if hasattr(self._local, 'connection'):
            try:
                self._local.connection.close()
                delattr(self._local, 'connection')
            except Exception as e:
                logger.error(f"关闭数据库连接失败: {e}")


# ===================== 心率数据解析函数 =====================
def parse_heart_rate_data(data: bytearray):
    try:
        flags = data[0]
        is_16bit = (flags & 0x01) == 0x01
        if is_16bit:
            heart_rate = (data[1] << 8) | data[2]
        else:
            heart_rate = data[1]
        if heart_rate < 30 or heart_rate > 200:
            return None
        return heart_rate
    except Exception as e:
        logger.error(f"解析心率数据失败：{e}")
        return None


def generate_physiological_lf_hf(rr_intervals):
    rr_mean = np.mean(rr_intervals)
    rr_std = np.std(rr_intervals)
    lf_raw = np.clip(1000 + 1000 * rr_std / 0.1, 500, 3000)
    hf_raw = np.clip(800 + 800 * rr_mean / 1.0, 300, 2000)
    lf_hf_raw = np.clip(lf_raw / hf_raw, 1.0, 2.0)
    lf_norm = round(lf_raw / MAX_LF, 4)
    hf_norm = round(hf_raw / MAX_HF, 4)
    lf_hf_norm = round(lf_hf_raw / MAX_LF_HF, 4)
    return lf_norm, hf_norm, lf_hf_norm


def compute_9d_features(heart_rate_data):
    if len(heart_rate_data) < 5:
        return [0.0] * 9
    timestamps = np.array([x[0] for x in heart_rate_data])
    heart_rates = np.array([x[1] for x in heart_rate_data])
    rr_intervals = np.diff(timestamps)
    rr_intervals = rr_intervals[rr_intervals < 2.0]
    if len(rr_intervals) < 3:
        return [0.0] * 9
    hr_mean = np.mean(heart_rates)
    hr_std = np.std(heart_rates)
    norm_hr = round(hr_mean / MAX_HEART_RATE, 4)
    norm_hr_std = round(hr_std / MAX_HR_STD, 4)
    sdnn = np.std(rr_intervals)
    norm_sdnn = round(np.clip(sdnn / MAX_SDNN, 0, 1), 4)
    rr_diff = np.diff(rr_intervals)
    rmssd = np.sqrt(np.mean(np.square(rr_diff))) if len(rr_diff) > 0 else 0.0
    norm_rmssd = round(np.clip(rmssd / MAX_RMSSD, 0, 1), 4)
    nn50_count = np.sum(np.abs(rr_diff) > 0.05)
    pnn50 = round(nn50_count / len(rr_diff) if len(rr_diff) > 0 else 0.0, 4)
    lf_norm, hf_norm, lf_hf_norm = generate_physiological_lf_hf(rr_intervals)
    is_irregular = 1 if (hr_std > HR_STD_THRESHOLD or sdnn > 0.08) else 0
    return [norm_hr, norm_sdnn, norm_rmssd, lf_norm, hf_norm, lf_hf_norm, pnn50, norm_hr_std, is_irregular]


# ===================== 心率采集器 =====================
class HeartRateCollector:
    def __init__(self, device_type='ble_heart_rate', device_id=None, ble_keyword='HUAWEI', ble_timeout=30,
                 fallback=True):
        self.device_type = device_type
        self.device_id = device_id
        self.ble_keyword = ble_keyword
        self.ble_timeout = ble_timeout
        self.fallback_enabled = fallback
        self.rr_buffer = deque(maxlen=2000)
        self.hr_buffer = deque(maxlen=2000)
        self.is_connected = False
        self.fallback_active = False
        self.lock = threading.RLock()
        self.running = True
        self.client = None
        self.loop = None
        self.heart_rate_data = []
        self.last_hr_time = 0
        self.last_hr_value = 0
        self.BUFFER_SIZE = 30

        logger.info(f"心率采集器初始化: 设备类型={device_type}")

        if device_type == 'ble_heart_rate':
            self._init_ble_heart_rate()
        elif device_type == 'simulated':
            self._init_simulated()
        else:
            self._init_simulated()

    def _init_ble_heart_rate(self):
        try:
            self.ble_thread = threading.Thread(target=self._run_ble_loop, daemon=True)
            self.ble_thread.start()
            start_time = time.time()
            while time.time() - start_time < self.ble_timeout:
                if self.is_connected:
                    logger.info(f"✅ BLE心率设备连接成功")
                    return
                time.sleep(0.5)
            if self.fallback_enabled:
                logger.warning(f"⚠️ BLE连接超时，切换到模拟数据模式")
                self.fallback_active = True
                self._init_simulated()
        except Exception as e:
            logger.error(f"BLE心率设备初始化失败: {e}")
            if self.fallback_enabled:
                self.fallback_active = True
                self._init_simulated()

    def _run_ble_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self._scan_and_connect_ble())
        except Exception as e:
            logger.error(f"BLE事件循环错误: {e}")
        finally:
            # 不要立即关闭循环，等待回调
            if self.loop and self.loop.is_running():
                self.loop.call_soon_threadsafe(self.loop.stop)
            self.loop.close()

    async def _scan_and_connect_ble(self):
        logger.info(f"🔍 正在扫描BLE心率设备...")
        try:
            devices = await BleakScanner.discover(timeout=10)
            logger.info(f"找到 {len(devices)} 个蓝牙设备")

            target_device = None
            for dev in devices:
                if dev.name and self.ble_keyword in dev.name:
                    if "Pen" not in dev.name and "Mouse" not in dev.name:
                        target_device = dev
                        logger.info(f"✅ 找到心率设备：{dev.name}")
                        break

            if not target_device:
                logger.warning("⚠️ 未找到BLE心率设备，请确保手表已开启心率广播")
                return

            logger.info(f"正在连接 {target_device.name}...")
            self.client = BleakClient(target_device.address)
            await self.client.connect(timeout=20.0)

            if self.client.is_connected:
                logger.info("✅ BLE连接成功，正在查找心率服务...")

                # 查找心率服务
                for service in self.client.services.services.values():
                    for char in service.characteristics:
                        if char.uuid.lower() == HEART_RATE_MEASUREMENT_UUID.lower():
                            logger.info("✅ 找到心率测量特征！")
                            self.is_connected = True
                            self.fallback_active = False
                            await self.client.start_notify(
                                HEART_RATE_MEASUREMENT_UUID,
                                self._ble_heart_rate_callback
                            )
                            logger.info("✅ 开始接收心率数据")

                            # 保持连接
                            while self.running and self.client.is_connected:
                                await asyncio.sleep(1)
                            break
                    if self.is_connected:
                        break

                if not self.is_connected:
                    logger.error("❌ 未找到心率测量特征")
                    await self.client.disconnect()
            else:
                logger.error("❌ 无法连接到设备")

        except asyncio.CancelledError:
            logger.info("BLE连接任务被取消")
        except Exception as e:
            logger.error(f"BLE连接错误: {e}")

    def _ble_heart_rate_callback(self, sender, data):
        try:
            heart_rate = parse_heart_rate_data(data)
            if heart_rate:
                current_time = time.time()
                self.heart_rate_data.append((current_time, heart_rate))
                if len(self.heart_rate_data) > self.BUFFER_SIZE:
                    self.heart_rate_data.pop(0)
                if self.last_hr_time > 0:
                    time_diff = current_time - self.last_hr_time
                    if 0.3 < time_diff < 2.0:
                        with self.lock:
                            self.rr_buffer.append(time_diff * 1000)
                            self.hr_buffer.append(heart_rate)
                self.last_hr_time = current_time
                self.last_hr_value = heart_rate
                print(f"\r📊 实时心率: {heart_rate} bpm | 缓存: {len(self.heart_rate_data)}/{self.BUFFER_SIZE}", end="")
        except RuntimeError as e:
            if "Event loop is closed" not in str(e):
                logger.error(f"BLE回调错误: {e}")
        except Exception as e:
            logger.error(f"BLE回调错误: {e}")

    def _init_simulated(self):
        self.is_connected = True
        self.fallback_active = True
        logger.info("📊 使用模拟心率数据")
        self.sim_thread = threading.Thread(target=self._simulated_read_loop, daemon=True)
        self.sim_thread.start()

    def _simulated_read_loop(self):
        while self.running:
            try:
                base_hr = 70 + 10 * np.sin(time.time() * 0.1)
                base_rr = 60000 / base_hr
                hf_variation = 40 * np.sin(time.time() * 0.25)
                lf_variation = 20 * np.sin(time.time() * 0.1)
                rr = base_rr + hf_variation + lf_variation + np.random.normal(0, 15)
                rr = np.clip(rr, 400, 1500)
                hr = 60000 / rr
                current_time = time.time()
                self.heart_rate_data.append((current_time, hr))
                if len(self.heart_rate_data) > self.BUFFER_SIZE:
                    self.heart_rate_data.pop(0)
                with self.lock:
                    self.rr_buffer.append(rr)
                    self.hr_buffer.append(hr)
                print(
                    f"\r📊 模拟心率: {hr:.0f} bpm | RR: {rr:.0f}ms | 缓存: {len(self.heart_rate_data)}/{self.BUFFER_SIZE}",
                    end="")
                time.sleep(rr / 1000.0 * np.random.uniform(0.9, 1.1))
            except Exception as e:
                logger.error(f"模拟数据生成错误: {e}")
                time.sleep(1)

    def read_rr_interval(self):
        with self.lock:
            if len(self.rr_buffer) > 0:
                return self.rr_buffer.popleft()
            return None

    def get_hrv_features(self):
        if len(self.heart_rate_data) >= 5:
            return compute_9d_features(self.heart_rate_data)
        return [0.0] * 9

    def get_current_hr(self):
        return self.last_hr_value if self.last_hr_value > 0 else None

    def get_statistics(self):
        with self.lock:
            if len(self.rr_buffer) > 0:
                rr_array = np.array(list(self.rr_buffer))
                return {
                    'rr_count': len(self.rr_buffer),
                    'mean_rr': float(np.mean(rr_array)),
                    'std_rr': float(np.std(rr_array)),
                    'mean_hr': float(60000 / np.mean(rr_array))
                }
            return {'rr_count': 0, 'mean_rr': 0, 'std_rr': 0, 'mean_hr': 0}

    def close(self):
        self.running = False
        if self.client and self.client.is_connected:
            try:
                loop = asyncio.new_event_loop()
                loop.run_until_complete(self.client.disconnect())
                loop.close()
            except:
                pass
        if hasattr(self, 'sim_thread') and self.sim_thread.is_alive():
            self.sim_thread.join(timeout=2.0)
        logger.info("心率采集器已关闭")


# ===================== SmartHRV处理器 =====================
class SmartHRVProcessor:
    def __init__(self, hr_collector=None, buffer_size=2000):
        self.hr_collector = hr_collector
        self.rr_intervals = deque(maxlen=buffer_size)
        self.lock = threading.RLock()

    def update_from_collector(self):
        if self.hr_collector:
            rr = self.hr_collector.read_rr_interval()
            while rr:
                with self.lock:
                    self.rr_intervals.append(rr)
                rr = self.hr_collector.read_rr_interval()

    def extract_features(self):
        #if self.hr_collector and self.hr_collector.is_connected:
        return self.hr_collector.get_hrv_features()
        #return [0.0] * 9


# ===================== 面部特征提取器 (适配新版MediaPipe) =====================
class FaceFeatureExtractor:
    def __init__(self):
        self.face_detector = None
        self.blink_counter = 0
        self.last_blink_time = time.time()
        self.eye_movement_history = deque(maxlen=10)
        self.use_mediapipe = False

        if mp_available and mp_face_mesh is not None:
            try:
                self.face_detector = mp_face_mesh
                self.use_mediapipe = True
                logger.info("✅ 新版 MediaPipe 面部特征提取器初始化成功")
            except Exception as e:
                logger.error(f"MediaPipe初始化失败: {e}")
                self.use_mediapipe = False

        if not self.use_mediapipe:
            logger.warning("将使用OpenCV Haar Cascade作为备用方案")
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

    def _get_landmark_points(self, landmarks, indices, w, h):
        return [(int(landmarks[idx].x * w), int(landmarks[idx].y * h)) for idx in indices]

    def _calculate_eye_aspect_ratio(self, eye_points):
        if len(eye_points) < 6:
            return 1.0
        vert_1 = np.linalg.norm(np.array(eye_points[1]) - np.array(eye_points[5]))
        vert_2 = np.linalg.norm(np.array(eye_points[2]) - np.array(eye_points[4]))
        horiz = np.linalg.norm(np.array(eye_points[0]) - np.array(eye_points[3]))
        ear = (vert_1 + vert_2) / (2.0 * horiz) if horiz > 0 else 0
        return float(np.clip(ear * 3, 0, 1))

    def _calculate_mouth_aspect_ratio(self, mouth_points):
        if len(mouth_points) < 4:
            return 0.0
        vertical = np.linalg.norm(np.array(mouth_points[2]) - np.array(mouth_points[3]))
        horizontal = np.linalg.norm(np.array(mouth_points[0]) - np.array(mouth_points[1]))
        mar = vertical / horizontal if horizontal > 0 else 0
        return float(np.clip(mar * 2, 0, 1))

    def _calculate_head_pose(self, landmarks, w, h):
        indices = [1, 152, 33, 263, 61, 291]
        image_points = np.array([(landmarks[idx].x * w, landmarks[idx].y * h) for idx in indices], dtype=np.float32)
        model_points = np.array(
            [[0, 0, 0], [0, -330, -65], [-225, 170, -135], [225, 170, -135], [-150, -150, -125], [150, -150, -125]],
            dtype=np.float32)
        focal_length = w
        camera_matrix = np.array([[focal_length, 0, w / 2], [0, focal_length, h / 2], [0, 0, 1]], dtype=np.float32)
        try:
            success, rvec, tvec = cv2.solvePnP(model_points, image_points, camera_matrix, np.zeros((4, 1)),
                                               flags=cv2.SOLVEPNP_ITERATIVE)
            if success:
                rmat, _ = cv2.Rodrigues(rvec)
                euler = cv2.decomposeProjectionMatrix(np.hstack((rmat, tvec)))[6]
                return [float(np.clip(euler[0][0] / 90, -1, 1)), float(np.clip(euler[1][0] / 90, -1, 1))]
        except:
            pass
        return [0.0, 0.0]

    def extract_features(self, frame):
        if frame is None or frame.size == 0:
            return [0.0] * 13
        if self.use_mediapipe and self.face_detector is not None:
            return self._extract_features_mediapipe(frame)
        return self._extract_features_opencv(frame)

    def _extract_features_mediapipe(self, frame):
        try:
            h, w = frame.shape[:2]
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            result = self.face_detector.detect(mp_image)
            if not result.face_landmarks:
                return [0.0] * 13
            lm = result.face_landmarks[0]
            features = [0.0] * 13

            left_eyebrow = self._get_landmark_points(lm, [33, 133, 157, 158], w, h)
            right_eyebrow = self._get_landmark_points(lm, [362, 263, 387, 386], w, h)
            if left_eyebrow and right_eyebrow:
                left_center = np.mean([left_eyebrow[0], left_eyebrow[1]], axis=0)
                right_center = np.mean([right_eyebrow[0], right_eyebrow[1]], axis=0)
                features[0] = left_center[1] / h
                features[1] = right_center[1] / h
                features[2] = abs(features[0] - features[1])
                left_angle = np.arctan2(left_eyebrow[1][1] - left_eyebrow[0][1],
                                        left_eyebrow[1][0] - left_eyebrow[0][0])
                right_angle = np.arctan2(right_eyebrow[1][1] - right_eyebrow[0][1],
                                         right_eyebrow[1][0] - right_eyebrow[0][0])
                features[3] = abs(left_angle - right_angle) / np.pi

            left_eye = self._get_landmark_points(lm, [33, 133, 157, 158, 159, 160], w, h)
            right_eye = self._get_landmark_points(lm, [362, 263, 387, 386, 385, 384], w, h)
            if left_eye and right_eye:
                features[4] = self._calculate_eye_aspect_ratio(left_eye)
                features[5] = self._calculate_eye_aspect_ratio(right_eye)
                now = time.time()
                if features[4] < 0.2 and features[5] < 0.2 and now - self.last_blink_time > 0.1:
                    self.blink_counter += 1
                    self.last_blink_time = now
                features[6] = min(1.0, self.blink_counter / max(1, now - self.last_blink_time) * 2)
                eye_center = np.mean([np.mean(left_eye, axis=0), np.mean(right_eye, axis=0)], axis=0)
                self.eye_movement_history.append(eye_center)
                if len(self.eye_movement_history) > 1:
                    movements = [np.linalg.norm(self.eye_movement_history[i] - self.eye_movement_history[i - 1]) for i
                                 in range(1, len(self.eye_movement_history))]
                    features[7] = min(1.0, np.mean(movements) * 2 / (w + h))

            mouth = self._get_landmark_points(lm, [61, 291, 13, 14], w, h)
            if mouth:
                features[8] = self._calculate_mouth_aspect_ratio(mouth)
                left_corner, right_corner = mouth[0], mouth[1]
                features[9] = (np.arctan2(right_corner[1] - left_corner[1],
                                          right_corner[0] - left_corner[0]) + np.pi / 2) / np.pi
                features[10] = abs(mouth[2][1] - mouth[3][1]) / h * 2

            pitch, yaw = self._calculate_head_pose(lm, w, h)
            features[11] = (pitch + 1) / 2
            features[12] = (yaw + 1) / 2
            return [float(np.clip(f, 0, 1)) for f in features]
        except Exception as e:
            logger.error(f"MediaPipe特征提取错误: {e}")
            return [0.0] * 13

    def _extract_features_opencv(self, frame):
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            features = [0.5] * 13
            if len(faces) > 0:
                x, y, w, h = faces[0]
                eyes = self.eye_cascade.detectMultiScale(gray[y:y + h, x:x + w])
                if len(eyes) >= 2:
                    features[4] = features[5] = 0.3
                else:
                    features[4] = features[5] = 0.1
                features[11] = y / frame.shape[0]
                features[12] = x / frame.shape[1]
            return features
        except Exception as e:
            logger.error(f"OpenCV特征提取错误: {e}")
            return [0.0] * 13


# ===================== 音频特征提取器 =====================
class AudioFeatureExtractor:
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        self.n_mfcc = 13
        self.hop_length = 512
        self.n_fft = 2048
        self.window_size = int(sample_rate * 0.025)
        self.hop_size = int(sample_rate * 0.010)

    def extract_features(self, audio_data):
        if audio_data is None or len(audio_data) < self.sample_rate // 10:
            return [0.0] * 21
        try:
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(
                    np.float32) / 32768.0 if audio_data.dtype == np.int16 else audio_data.astype(np.float32)
            audio_data = np.clip(audio_data, -1, 1)
            features = [0.0] * 21
            mfccs = librosa.feature.mfcc(y=audio_data, sr=self.sample_rate, n_mfcc=13, n_fft=self.n_fft,
                                         hop_length=self.hop_length)
            mfccs_mean = np.mean(mfccs, axis=1)
            for i in range(13):
                features[i] = np.clip((mfccs_mean[i] + 100) / 200, 0, 1)
            rms = librosa.feature.rms(y=audio_data, frame_length=self.window_size, hop_length=self.hop_size)
            features[13] = np.clip(np.mean(rms) * 10, 0, 1)
            zcr = librosa.feature.zero_crossing_rate(audio_data, frame_length=self.window_size,
                                                     hop_length=self.hop_size)
            features[14] = np.clip(np.mean(zcr) * 2, 0, 1)
            try:
                f0, voiced_flag, _ = librosa.pyin(audio_data, fmin=50, fmax=500, sr=self.sample_rate,
                                                  frame_length=self.window_size, hop_length=self.hop_size)
                f0_voiced = f0[voiced_flag]
                if len(f0_voiced) > 0:
                    features[15] = np.clip((np.mean(f0_voiced) - 50) / 450, 0, 1)
                    features[16] = np.clip(np.std(f0_voiced) / 100, 0, 1)
                    features[17] = np.clip(np.mean(voiced_flag), 0, 1)
            except:
                features[15], features[16], features[17] = 0.0, 0.5, 0.5
            spec_cent = librosa.feature.spectral_centroid(y=audio_data, sr=self.sample_rate, n_fft=self.n_fft,
                                                          hop_length=self.hop_length)
            features[18] = np.clip(np.mean(spec_cent) / 4000, 0, 1)
            spec_roll = librosa.feature.spectral_rolloff(y=audio_data, sr=self.sample_rate, n_fft=self.n_fft,
                                                         hop_length=self.hop_length)
            features[19] = np.clip(np.mean(spec_roll) / 4000, 0, 1)
            spec_bw = librosa.feature.spectral_bandwidth(y=audio_data, sr=self.sample_rate, n_fft=self.n_fft,
                                                         hop_length=self.hop_length)
            features[20] = np.clip(np.mean(spec_bw) / 2000, 0, 1)
            return [float(f) for f in features]
        except Exception as e:
            logger.error(f"音频特征提取失败: {e}")
            return [0.0] * 21


# ===================== 心理健康分析器 =====================
class MentalHealthAnalyzer:
    def __init__(self):
        self.analysis_history = deque(maxlen=100)
        self.lock = threading.RLock()

    def analyze(self, face_features, audio_features, hr_features):
        try:
            has_hr = len(hr_features) >= 9 and any(hr_features)
            stress = self._calculate_stress(face_features, audio_features, hr_features if has_hr else None)
            anxiety = self._calculate_anxiety(face_features, audio_features, hr_features if has_hr else None)
            fatigue = self._calculate_fatigue(face_features, audio_features, hr_features if has_hr else None)
            attention = 1.0 - (
                        face_features[7] * 0.3 + face_features[6] * 0.3 + abs(face_features[12] - 0.5) * 0.8) if len(
                face_features) >= 13 else 0.5
            mood = 0.5 + (face_features[9] - 0.5) * 0.4 if len(face_features) >= 10 else 0.5
            rec = []
            if stress > 0.7:
                rec.extend(["深呼吸练习", "短暂休息"])
            elif stress > 0.4:
                rec.append("正念冥想")
            if anxiety > 0.7: rec.extend(["放松训练", "避免咖啡因"])
            if fatigue > 0.7: rec.extend(["补充水分", "小憩15分钟"])
            if not rec: rec.append("状态良好")
            result = {
                'timestamp': time.time(),
                'stress_level': float(stress), 'anxiety_level': float(anxiety), 'fatigue_level': float(fatigue),
                'attention_score': float(attention), 'mood_score': float(mood), 'recommendations': rec,
                'risk_level': 'high' if max(stress, anxiety, fatigue) > 0.8 else 'medium' if max(stress, anxiety,
                                                                                                 fatigue) > 0.5 else 'low',
                'hr_available': has_hr
            }
            with self.lock:
                self.analysis_history.append(result)
            return result
        except Exception as e:
            logger.error(f"心理健康分析失败: {e}")
            return {'stress_level': 0, 'anxiety_level': 0, 'fatigue_level': 0, 'attention_score': 0, 'mood_score': 0,
                    'recommendations': [], 'risk_level': 'unknown', 'hr_available': False}

    def _calculate_stress(self, face, audio, hr):
        score = 0.0
        w = [0.4, 0.4, 0.2] if hr else [0.5, 0.5, 0]
        if len(face) >= 8: score += (face[2] * 0.4 + face[7] * 0.3 + face[6] * 0.3) * w[0]
        if len(audio) >= 17: score += (audio[16] * 0.3 + audio[13] * 0.3 + (1 - audio[14]) * 0.4) * w[1]
        if hr and len(hr) >= 6: score += (hr[0] * 0.3 + hr[5] * 0.4 + hr[7] * 0.3) * w[2]
        return np.clip(score, 0, 1)

    def _calculate_anxiety(self, face, audio, hr):
        score = 0.0
        w = [0.3, 0.3, 0.4] if hr else [0.5, 0.5, 0]
        if len(face) >= 8: score += (face[6] * 0.4 + face[7] * 0.3 + abs(face[12] - 0.5) * 0.6) * w[0]
        if len(audio) >= 15: score += (audio[14] * 0.5 + audio[13] * 0.5) * w[1]
        if hr and len(hr) >= 2: score += ((1 - hr[1]) * 0.5 + hr[5] * 0.5) * w[2]
        return np.clip(score, 0, 1)

    def _calculate_fatigue(self, face, audio, hr):
        score = 0.0
        w = [0.4, 0.3, 0.3] if hr else [0.6, 0.4, 0]
        if len(face) >= 12: score += (face[8] * 0.5 + (1 - face[4]) * 0.3 + (1 - face[11]) * 0.2) * w[0]
        if len(audio) >= 6: score += ((1 - audio[15]) * 0.5 + audio[16] * 0.5) * w[1]
        if hr and len(hr) >= 2: score += ((1 - hr[0]) * 0.5 + hr[2] * 0.5) * w[2]
        return np.clip(score, 0, 1)


# ===================== 性能监控器 =====================
class PerformanceMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.frame_times = deque(maxlen=100)
        self.processing_times = deque(maxlen=100)
        self.cpu_usage = deque(maxlen=100)
        self.memory_usage = deque(maxlen=100)
        self.queue_sizes = deque(maxlen=100)
        self.errors = 0
        self.warnings = 0
        self.lock = threading.RLock()

    def record_frame_time(self, d): self.frame_times.append(d)

    def record_processing_time(self, d): self.processing_times.append(d)

    def update_system_stats(self): self.cpu_usage.append(psutil.cpu_percent()); self.memory_usage.append(
        psutil.virtual_memory().percent)

    def record_queue_size(self, s): self.queue_sizes.append(s)

    def increment_errors(self): self.errors += 1

    def increment_warnings(self): self.warnings += 1

    def get_stats(self):
        with self.lock:
            return {
                'uptime': time.time() - self.start_time,
                'fps': len(self.frame_times) / (sum(self.frame_times) + 1e-6) if self.frame_times else 0,
                'avg_frame_time': np.mean(self.frame_times) if self.frame_times else 0,
                'avg_processing_time': np.mean(self.processing_times) if self.processing_times else 0,
                'cpu_usage': np.mean(self.cpu_usage) if self.cpu_usage else 0,
                'memory_usage': np.mean(self.memory_usage) if self.memory_usage else 0,
                'avg_queue_size': np.mean(self.queue_sizes) if self.queue_sizes else 0,
                'errors': self.errors, 'warnings': self.warnings
            }

    def get_health_status(self):
        s = self.get_stats()
        return 'critical' if s['errors'] > 10 or s['cpu_usage'] > 90 or s['avg_queue_size'] > 50 else 'warning' if s[
                                                                                                                       'warnings'] > 10 or \
                                                                                                                   s[
                                                                                                                       'cpu_usage'] > 70 or \
                                                                                                                   s[
                                                                                                                       'avg_queue_size'] > 20 else 'healthy'


# ===================== 实时可视化面板 =====================
class RealTimeVisualizer:
    def __init__(self):
        self.fig = None
        self.axes = None
        self.lines = {}
        self.data_buffers = {}
        self.is_running = False
        self.update_interval = 0.5
        self.last_update = 0

    def start(self):
        try:
            plt.ion()
            self.fig, self.axes = plt.subplots(2, 3, figsize=(15, 8))
            self.fig.suptitle('多模态数据采集实时监控', fontsize=16)
            self.lines['face'] = self.axes[0, 0].plot([], [], 'b-')[0]
            self.lines['audio'] = self.axes[0, 1].plot([], [], 'g-')[0]
            self.lines['hr'] = self.axes[0, 2].plot([], [], 'r-')[0]
            self.lines['mental'] = self.axes[1, 0].bar([0, 1, 2, 3], [0, 0, 0, 0])
            self.lines['performance'] = self.axes[1, 1].plot([], [], 'purple')[0]
            self.lines['queue'] = self.axes[1, 2].plot([], [], 'orange')[0]
            self.data_buffers = {k: deque(maxlen=50) for k in ['face', 'audio', 'hr', 'mental', 'performance', 'queue']}
            for ax in self.axes.flat: ax.grid(True)
            self.is_running = True
            plt.tight_layout()
        except Exception as e:
            logger.error(f"可视化启动失败: {e}")
            self.is_running = False

    def update(self, face=None, audio=None, hr=None, mental=None, perf=None, queue=0):
        if not self.is_running or time.time() - self.last_update < self.update_interval:
            return
        try:
            if face: self.lines['face'].set_data(range(len(face[:13])), face[:13])
            if audio: self.lines['audio'].set_data(range(len(audio[:21])), audio[:21])
            if hr and any(hr): self.lines['hr'].set_data(range(len(hr[:9])), hr[:9])
            if mental: [b.set_height(mental.get(k, 0)) for b, k in
                        zip(self.lines['mental'], ['stress_level', 'anxiety_level', 'fatigue_level', 'mood_score'])]
            if perf: self.lines['performance'].set_data(range(len(perf)), [perf.get('cpu_usage', 0)])
            self.lines['queue'].set_data(range(len(self.data_buffers['queue'])), list(self.data_buffers['queue']))
            for ax in self.axes.flat: ax.relim(); ax.autoscale_view()
            self.fig.canvas.draw();
            self.fig.canvas.flush_events()
            self.last_update = time.time()
        except Exception as e:
            logger.debug(f"可视化更新失败: {e}")

    def stop(self):
        self.is_running = False
        if self.fig: plt.close(self.fig)


# ===================== 配置验证 =====================
def validate_config(config):
    required = ['participant_id', 'experiment_type', 'output_dir']
    for f in required:
        if f not in config: raise ValueError(f"缺少配置: {f}")
    if config.get('video_fps', 30) <= 0: config['video_fps'] = 30
    if config.get('audio_sample_rate', 16000) not in [8000, 16000, 22050, 44100, 48000]:
        logger.warning(f"不常见采样率: {config.get('audio_sample_rate')}")
    return config


# ===================== 增强版主采集器 =====================
class EnhancedDataCollector:
    def __init__(self, config_path=None):
        self.config = self._load_config(config_path)
        self.config = validate_config(self.config)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.participant_id = self.config.get('participant_id', 'participant_001')
        self.experiment_type = self.config.get('experiment_type', 'baseline')
        self.start_time = time.time()
        self.output_dir = self.config.get('output_dir', 'data/collected')
        self._init_directories()

        self.db_manager = None
        self.resource_manager = ResourceManager()
        self.heartbeat_monitor = HeartbeatMonitor(timeout=10.0)
        self._init_database()
        self.hr_collector = self._init_hr_collector()

        self.face_extractor = FaceFeatureExtractor()
        self.audio_extractor = AudioFeatureExtractor(self.config.get('audio_sample_rate', 16000))
        self.hrv_processor = SmartHRVProcessor(hr_collector=self.hr_collector,
                                               buffer_size=self.config.get('hrv_buffer_size', 2000))

        self.mental_analyzer = MentalHealthAnalyzer()
        self.performance_monitor = PerformanceMonitor()
        self.visualizer = RealTimeVisualizer()

        self.frame_queue = MonitoredQueue(maxsize=100, name="frame")
        self.audio_queue = MonitoredQueue(maxsize=50, name="audio")
        self.feature_queue = MonitoredQueue(maxsize=100, name="feature")

        self.is_running = False
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        self.lock = threading.RLock()
        self.video_cap = None
        self.audio_stream = None

        self.stats = {'frames_processed': 0, 'audio_chunks': 0, 'packets_created': 0, 'packets_saved': 0,
                      'mental_analyses': 0, 'errors': 0, 'warnings': 0, 'start_time': self.start_time}
        self.last_face_features = [0.0] * 13
        self.last_audio_features = [0.0] * 21
        self.last_hr_features = [0.0] * 9
        self.last_mental_scores = {}
        self.threads = []

        self.backend_url = self.config.get('backend_url', 'http://localhost:5000/predict')
        self.enable_backend = self.config.get('enable_backend', True)

        logger.info("=" * 80)
        logger.info("智能增强版数据采集器初始化完成")
        logger.info(f"会话ID: {self.session_id}")
        logger.info(f"心率设备: {self.config.get('hr_device_type', 'ble_heart_rate')}")
        logger.info(f"后端服务: {self.backend_url} ({'启用' if self.enable_backend else '禁用'})")
        logger.info("=" * 80)

    def _load_config(self, config_path):
        default = {
            'participant_id': 'participant_001', 'experiment_type': 'baseline', 'output_dir': 'data/collected',
            'video_width': 640, 'video_height': 480, 'video_fps': 30, 'camera_index': 1, 'show_preview': True,
            'audio_sample_rate': 16000, 'audio_channels': 1, 'audio_chunk_duration': 2.0,
            'hrv_buffer_size': 2000, 'hrv_calc_interval': 5.0, 'feature_extraction_interval': 1.0,
            'mental_analysis_interval': 2.0, 'save_interval': 10, 'save_raw': False, 'use_database': True,
            'db_path': 'data/feature_database.db', 'enable_visualization': True, 'enable_hr': True,
            'hr_device_type': 'ble_heart_rate', 'hr_device_id': None, 'ble_keyword': 'HUAWEI', 'ble_timeout': 30,
            'fallback_simulated': True, 'backend_url': 'http://localhost:5000/predict', 'enable_backend': True
        }
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                default.update(json.load(f))
            logger.info(f"配置文件已加载: {config_path}")
        default['system'] = {'cpu_count': psutil.cpu_count(), 'memory_total': psutil.virtual_memory().total / 1e9}
        return default

    def _init_directories(self):
        dirs = [self.output_dir]
        for d in ['features', 'raw', 'analysis']:
            dirs.append(os.path.join(self.output_dir, self.session_id, d))
        dirs.extend(['logs', 'data'])
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
        self.session_dir = os.path.join(self.output_dir, self.session_id)
        self.feature_dir = os.path.join(self.session_dir, "features")
        self.raw_dir = os.path.join(self.session_dir, "raw")
        self.analysis_dir = os.path.join(self.session_dir, "analysis")

    def _init_database(self):
        if not self.config.get('use_database', True): return
        try:
            self.db_manager = SmartDBManager(db_path=self.config.get('db_path', 'data/feature_database.db'))
            logger.info("数据库初始化成功")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            self.db_manager = None

    def _init_hr_collector(self):
        if not self.config.get('enable_hr', True): return None
        try:
            c = HeartRateCollector(
                device_type=self.config.get('hr_device_type', 'ble_heart_rate'),
                ble_keyword=self.config.get('ble_keyword', 'HUAWEI'),
                ble_timeout=self.config.get('ble_timeout', 30),
                fallback=self.config.get('fallback_simulated', True)
            )
            self.resource_manager.register(c, lambda c: c.close())
            return c
        except Exception as e:
            logger.error(f"心率采集器初始化失败: {e}")
            return None

    def _close_thread_database(self):
        if self.db_manager: self.db_manager.close()

    def send_to_backend(self, packet):
        if not self.enable_backend: return None
        try:
            r = requests.post(self.backend_url, json=packet, headers={'Content-Type': 'application/json'}, timeout=1.0)
            if r.status_code == 200:
                result = r.json()
                if result.get('success'):
                    logger.info(
                        f"✅ 后端预测: {result['prediction']}, 分数: {result['score']}, 解释: {result['explanation'][:50]}...")
                return result
        except Exception as e:
            logger.debug(f"后端连接失败: {e}")
        return None

    def start(self):
        if self.is_running: return
        with self.lock:
            self.is_running = True
            self.stop_event.clear()
            self.pause_event.clear()
        try:
            self._init_camera()
            self._init_audio()
            if self.config.get('enable_visualization', True): self.visualizer.start()
            self._start_worker_threads()
            self._save_session_info()
            self._print_startup_message()
            logger.info("数据采集已完全启动")
        except Exception as e:
            logger.error(f"启动失败: {e}")
            self.stop()

    def _init_camera(self):
        for idx in [0, 1]:
            self.video_cap = cv2.VideoCapture(idx)
            if self.video_cap.isOpened():
                logger.info(f"摄像头初始化成功: 索引={idx}")
                break
        if not self.video_cap or not self.video_cap.isOpened():
            raise RuntimeError("无法打开摄像头")
        self.resource_manager.register(self.video_cap, lambda cap: cap.release())
        self.video_cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.get('video_width', 640))
        self.video_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.get('video_height', 480))
        self.video_cap.set(cv2.CAP_PROP_FPS, self.config.get('video_fps', 30))

    def _init_audio(self):
        try:
            device_id = self.config.get('audio_device', None) or sd.query_devices(kind='input')['index']
            self.audio_stream = sd.InputStream(
                samplerate=self.config.get('audio_sample_rate', 16000),
                channels=self.config.get('audio_channels', 1), dtype='int16',
                callback=self._audio_callback,
                blocksize=int(self.config.get('audio_sample_rate', 16000) * 0.1),
                device=device_id
            )
            self.audio_stream.start()
            logger.info(f"音频采集已启动")
        except Exception as e:
            logger.error(f"音频初始化失败: {e}")
            self.audio_stream = None

    def _audio_callback(self, indata, frames, time_info, status):
        if status and status.input_overflow:
            logger.warning("音频输入溢出")
            self.performance_monitor.increment_warnings()
        try:
            audio_data = indata.flatten()
            if len(audio_data) > 0:
                self.audio_queue.put({'data': audio_data, 'timestamp': time_info.inputBufferAdcTime}, block=False)
        except Exception as e:
            logger.debug(f"音频回调错误: {e}")

    def _start_worker_threads(self):
        targets = [('video_capture', self._video_loop), ('data_processing', self._processing_loop),
                   ('data_saving', self._save_loop), ('performance_monitor', self._monitor_loop),
                   ('error_recovery', self._recovery_loop), ('mental_health_analysis', self._mental_analysis_loop)]
        self.threads = []
        for name, target in targets:
            t = threading.Thread(target=self._thread_wrapper, args=(name, target), name=name, daemon=True)
            t.start()
            self.threads.append(t)
            logger.info(f"线程已启动: {name}")

    def _thread_wrapper(self, name, func):
        try:
            while not self.stop_event.is_set():
                self.heartbeat_monitor.beat(name)
                func()
        except Exception as e:
            logger.error(f"线程 {name} 错误: {e}")
        finally:
            self._close_thread_database()
            logger.info(f"线程 {name} 已结束")

    def _video_loop(self):
        interval = 1.0 / self.config.get('video_fps', 30)
        last = time.time()
        while not self.stop_event.is_set():
            if self.pause_event.is_set():
                time.sleep(0.1);
                continue
            now = time.time()
            if now - last < interval:
                time.sleep(interval - (now - last))
            ret, frame = self.video_cap.read()
            if not ret: continue
            self.performance_monitor.record_frame_time(time.time() - now)
            self.frame_queue.put({'data': frame, 'timestamp': now}, block=False)
            self.performance_monitor.record_queue_size(self.frame_queue.qsize())
            if self.config.get('show_preview', True):
                self._show_preview(frame)
            last = time.time()
            if self.stats['frames_processed'] % 100 == 0: gc.collect()

    def _show_preview(self, frame):
        try:
            preview = cv2.resize(frame, (320, 240))
            s = self.performance_monitor.get_stats()
            h = self.performance_monitor.get_health_status()
            hr = "HR: SIM" if (self.hr_collector and self.hr_collector.fallback_active) else "HR: ON" if (
                        self.hr_collector and self.hr_collector.is_connected) else "HR: OFF"
            lines = [f"Frames: {self.stats['frames_processed']}", f"Packets: {self.stats['packets_created']}/30",
                     f"FPS: {s['fps']:.1f}", f"CPU: {s['cpu_usage']:.1f}%", hr, f"Health: {h}"]
            if self.last_mental_scores:
                lines.append(f"Stress: {self.last_mental_scores.get('stress_level', 0):.2f}")
            for i, line in enumerate(lines):
                color = (0, 255, 0) if h == 'healthy' else (0, 255, 255) if h == 'warning' else (0, 0, 255)
                cv2.putText(preview, line, (10, 20 + i * 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
            cv2.imshow("采集系统 (q:停止)", preview)
            if cv2.waitKey(1) & 0xFF == ord('q'): self.stop()
        except Exception as e:
            logger.debug(f"预览错误: {e}")

    def _processing_loop(self):
        last_extract = last_hrv = time.time()
        extract_interval = self.config.get('feature_extraction_interval', 1.0)
        hrv_interval = self.config.get('hrv_calc_interval', 5.0)
        audio_acc, audio_dur = [], 0
        target_dur = self.config.get('audio_chunk_duration', 2.0)

        while not self.stop_event.is_set():
            if self.pause_event.is_set():
                time.sleep(0.1);
                continue
            now = time.time()
            if self.hr_collector and self.hr_collector.is_connected:
                self.hrv_processor.update_from_collector()
            self._process_video_frames()
            audio_feat, audio_acc, audio_dur = self._process_audio(audio_acc, audio_dur, target_dur)
            if now - last_hrv >= hrv_interval:
                self._calculate_hrv()
                last_hrv = now
            hr_feat = self.hrv_processor.extract_features()
            if any(hr_feat): self.last_hr_features = hr_feat
            if now - last_extract >= extract_interval:
                self._create_feature_packet(now)
                last_extract = now
            self.performance_monitor.record_processing_time(time.time() - now)
            if psutil.virtual_memory().percent > 85: gc.collect()
            time.sleep(0.01)

    def _process_video_frames(self):
        while not self.frame_queue.empty():
            try:
                d = self.frame_queue.get_nowait()
                self.last_face_features = self.face_extractor.extract_features(d['data'])
                self.stats['frames_processed'] += 1
            except Empty:
                break

    def _process_audio(self, acc, dur, target):
        feat = self.last_audio_features
        while not self.audio_queue.empty():
            try:
                d = self.audio_queue.get_nowait()
                acc.append(d['data'])
                dur += len(d['data']) / self.config.get('audio_sample_rate', 16000)
                self.stats['audio_chunks'] += 1
            except Empty:
                break
        if dur >= target and acc:
            combined = np.concatenate(acc)
            feat = self.audio_extractor.extract_features(combined)
            self.last_audio_features = feat
            acc, dur = [], 0
        return feat, acc, dur

    def _calculate_hrv(self):
        if self.hr_collector and self.hr_collector.is_connected:
            s = self.hr_collector.get_statistics()
            if s['rr_count'] > 0:
                logger.debug(f"HRV: RR={s['rr_count']}, HR={s['mean_hr']:.1f}bpm")

    def _create_feature_packet(self, ts):
        packet = {
            'face_features': [float(x) for x in self.last_face_features],
            'audio_features': [float(x) for x in self.last_audio_features],
            'hr_features': [float(x) for x in self.last_hr_features],
            'timestamp': ts, 'session_id': self.session_id
        }
        if self.feature_queue.put(packet, block=False):
            self.stats['packets_created'] += 1
            if self.stats['packets_created'] >= 30:
                logger.info(f"✅ 已完成30次数据采集，自动停止")
                self.stop()
        if self.enable_backend:
            self.send_to_backend(packet)

    def _mental_analysis_loop(self):
        interval = self.config.get('mental_analysis_interval', 2.0)
        while not self.stop_event.is_set():
            time.sleep(interval)
            if self.pause_event.is_set(): continue
            if self.hr_collector and self.hr_collector.is_connected:
                f = self.hrv_processor.extract_features()
                if any(f):
                    logger.info(f"📊 HRV: 心率={f[0]:.2f} SDNN={f[1]:.2f} RMSSD={f[2]:.2f} LF/HF={f[5]:.2f}")
            score = self.mental_analyzer.analyze(self.last_face_features, self.last_audio_features,
                                                 self.last_hr_features)
            self.last_mental_scores = score
            self.stats['mental_analyses'] += 1
            if self.db_manager:
                self.db_manager.save_mental_health_score(self.session_id, score)
            self._save_mental_analysis(score)
            logger.info(
                f"🧠 压力:{score['stress_level']:.2f} 焦虑:{score['anxiety_level']:.2f} 疲劳:{score['fatigue_level']:.2f}")

    def _save_mental_analysis(self, s):
        try:
            with open(os.path.join(self.analysis_dir, f"mental_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"),
                      'w') as f:
                json.dump(convert_numpy_to_python(s), f, indent=2, cls=NumpyEncoder)
        except Exception as e:
            logger.error(f"保存分析失败: {e}")

    def _save_loop(self):
        interval = self.config.get('save_interval', 10)
        last = time.time()
        batch = []
        while not self.stop_event.is_set():
            while not self.feature_queue.empty():
                try:
                    batch.append(self.feature_queue.get_nowait())
                except Empty:
                    break
            if time.time() - last >= interval and batch:
                self._save_packets(batch)
                batch = []
                last = time.time()
            time.sleep(1)

    def _save_packets(self, packets):
        try:
            with open(os.path.join(self.feature_dir, f"features_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"),
                      'w') as f:
                json.dump(convert_numpy_to_python(packets), f, indent=2, cls=NumpyEncoder)
            self.stats['packets_saved'] += len(packets)
            hr_cnt = sum(1 for p in packets if p.get('hr_features') and any(p.get('hr_features', [])))
            logger.info(
                f"💾 保存: {self.stats['frames_processed']}帧, {self.stats['audio_chunks']}音频块, 含心率包:{hr_cnt}/{len(packets)}")
        except Exception as e:
            logger.error(f"保存失败: {e}")

    def _monitor_loop(self):
        while not self.stop_event.is_set():
            time.sleep(2)
            self.performance_monitor.update_system_stats()
            dead = self.heartbeat_monitor.check_health()
            if dead: logger.warning(f"无响应线程: {dead}")
            s = self.performance_monitor.get_stats()
            if self.config.get('enable_visualization', True):
                self.visualizer.update(face=self.last_face_features, audio=self.last_audio_features,
                                       hr=self.last_hr_features,
                                       mental=self.last_mental_scores, perf=s, queue_size=self.frame_queue.qsize())
            if s['errors'] > 10 or s['cpu_usage'] > 90:
                logger.warning(f"性能警告: CPU={s['cpu_usage']:.1f}% 内存={s['memory_usage']:.1f}% 错误={s['errors']}")

    def _recovery_loop(self):
        while not self.stop_event.is_set():
            time.sleep(5)
            if self.performance_monitor.get_health_status() == 'critical':
                logger.warning("严重状态，尝试恢复...")
                self._clear_queues()
                self.hrv_processor = SmartHRVProcessor(hr_collector=self.hr_collector)
                self.performance_monitor.errors = 0
                self.performance_monitor.warnings = 0
                gc.collect()
                logger.info("恢复完成")

    def _clear_queues(self):
        for q in [self.frame_queue, self.audio_queue, self.feature_queue]:
            while not q.empty():
                try:
                    q.get_nowait()
                except Empty:
                    break

    def _manual_save(self):
        logger.info("手动保存")
        batch = []
        while not self.feature_queue.empty():
            try:
                batch.append(self.feature_queue.get_nowait())
            except Empty:
                break
        if batch: self._save_packets(batch)

    def _save_session_info(self):
        info = {
            'session_id': self.session_id, 'participant_id': self.participant_id,
            'experiment_type': self.experiment_type,
            'start_time': datetime.fromtimestamp(self.start_time).isoformat(), 'config': self.config,
            'feature_formats': {'face': '13维', 'audio': '21维', 'hr': '9维'},
            'hr_device': {'enabled': self.config.get('enable_hr', True), 'type': self.config.get('hr_device_type'),
                          'connected': self.hr_collector.is_connected if self.hr_collector else False,
                          'fallback_active': self.hr_collector.fallback_active if self.hr_collector else False},
            'backend': {'enabled': self.enable_backend, 'url': self.backend_url}
        }
        with open(os.path.join(self.session_dir, "session_info.json"), 'w') as f:
            json.dump(info, f, indent=2, cls=NumpyEncoder)
        logger.info(f"会话信息已保存")

    def _print_startup_message(self):
        hr = "已连接" if (
                    self.hr_collector and self.hr_collector.is_connected and not self.hr_collector.fallback_active) else "模拟数据" if (
                    self.hr_collector and self.hr_collector.fallback_active) else "未连接"
        print("\n" + "=" * 80)
        print("智能多模态数据采集系统 - 增强版")
        print("=" * 80)
        print(f"会话ID: {self.session_id}")
        print(f"心率状态: {hr}")
        print(f"后端服务: {self.backend_url} ({'已启用' if self.enable_backend else '已禁用'})")
        print(f"自动停止: 采集30次数据后自动停止")
        print("\n操作说明:")
        print("  - 按 'q' 键停止采集")
        print("  - 按 's' 键手动保存当前数据")
        print("=" * 80 + "\n")

    def stop(self):
        if not self.is_running: return
        logger.info("正在停止采集...")
        self.stop_event.set()
        if self.audio_stream:
            try:
                self.audio_stream.stop(); self.audio_stream.close()
            except:
                pass
        cv2.destroyAllWindows()
        if self.config.get('enable_visualization', True): self.visualizer.stop()
        for t in self.threads:
            try:
                t.join(timeout=3)
            except:
                pass
        self._save_remaining_data()
        self._save_session_summary()
        if self.db_manager: self.db_manager.close()
        self.resource_manager.cleanup_all()
        with self.lock:
            self.is_running = False
        self._print_final_stats()

    def _save_remaining_data(self):
        logger.info("保存剩余数据...")
        batch = []
        while not self.feature_queue.empty():
            try:
                batch.append(self.feature_queue.get_nowait())
            except Empty:
                break
        if batch:
            with open(os.path.join(self.feature_dir, f"features_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"),
                      'w') as f:
                json.dump(convert_numpy_to_python(batch), f, indent=2, cls=NumpyEncoder)
            self.stats['packets_saved'] += len(batch)

    def _save_session_summary(self):
        dur = time.time() - self.start_time
        hr_stats = self.hr_collector.get_statistics() if self.hr_collector else {'rr_count': 0}
        hr_feat = self.hrv_processor.extract_features() if self.hr_collector else []
        summary = {
            'session_id': self.session_id, 'participant_id': self.participant_id,
            'experiment_type': self.experiment_type,
            'start_time': datetime.fromtimestamp(self.start_time).isoformat(),
            'end_time': datetime.fromtimestamp(time.time()).isoformat(),
            'duration_seconds': round(dur, 2), 'stats': self.stats, 'performance': self.performance_monitor.get_stats(),
            'hr_statistics': hr_stats, 'hrv_summary': {'features': hr_feat} if any(hr_feat) else {},
            'hr_source': 'simulated' if (
                        self.hr_collector and self.hr_collector.fallback_active) else 'ble' if self.hr_collector else 'none',
            'backend_enabled': self.enable_backend
        }
        with open(os.path.join(self.session_dir, "session_summary.json"), 'w') as f:
            json.dump(summary, f, indent=2, cls=NumpyEncoder)
        logger.info(f"会话总结已保存")

    def _print_final_stats(self):
        dur = time.time() - self.start_time
        print("\n" + "=" * 80)
        print("采集完成 - 最终统计")
        print("=" * 80)
        print(f"会话ID: {self.session_id}")
        print(f"持续时间: {dur:.1f} 秒")
        print(f"处理帧数: {self.stats['frames_processed']}")
        print(f"特征包数: {self.stats['packets_created']}/30")
        print(f"已保存数: {self.stats['packets_saved']}")
        if self.hr_collector:
            hr = self.hr_collector.get_statistics()
            print(
                f"心率数据源: {'模拟' if self.hr_collector.fallback_active else 'BLE' if self.hr_collector.is_connected else '无'}")
            print(f"RR间期数: {hr['rr_count']}")
            if hr['rr_count'] > 0: print(f"平均心率: {hr['mean_hr']:.1f} bpm")
        print(f"后端服务: {'已启用' if self.enable_backend else '已禁用'}")
        print(f"错误数: {self.stats['errors']}, 警告数: {self.stats['warnings']}")
        print("=" * 80)

    def run(self, duration_seconds=None):
        self.start()
        try:
            if duration_seconds:
                logger.info(f"采集将持续 {duration_seconds} 秒")
                time.sleep(duration_seconds)
                self.stop()
            else:
                while self.is_running:
                    time.sleep(1)
        except KeyboardInterrupt:
            logger.info("用户中断")
            self.stop()


# ===================== 主程序 =====================
def main():
    parser = ArgumentParser(description="增强版多模态数据采集系统")
    parser.add_argument('--config', '-c', default=None, help='配置文件路径')
    parser.add_argument('--duration', '-d', type=int, default=None, help='采集时长(秒)')
    parser.add_argument('--participant', '-p', default="participant_001", help='参与者ID')
    parser.add_argument('--experiment', '-e', default="baseline", help='实验类型')
    parser.add_argument('--output', '-o', default="data/collected", help='输出目录')
    parser.add_argument('--no-preview', action='store_true', help='禁用视频预览')
    parser.add_argument('--no-db', action='store_true', help='禁用数据库')
    parser.add_argument('--no-viz', action='store_true', help='禁用可视化')
    parser.add_argument('--hr-device', default="ble_heart_rate", choices=['simulated', 'ble_heart_rate', 'none'],
                        help='心率设备类型')
    parser.add_argument('--ble-keyword', default="HUAWEI", help='BLE设备关键词')
    parser.add_argument('--ble-timeout', type=int, default=30, help='BLE超时(秒)')
    parser.add_argument('--no-fallback', action='store_true', help='禁用回退')
    parser.add_argument('--no-hr', action='store_true', help='禁用心率')
    parser.add_argument('--backend-url', default="http://localhost:5000/predict", help='后端API地址')
    parser.add_argument('--no-backend', action='store_true', help='禁用后端')

    args = parser.parse_args()
    config = {
        'participant_id': args.participant, 'experiment_type': args.experiment, 'output_dir': args.output,
        'show_preview': not args.no_preview, 'use_database': not args.no_db, 'enable_visualization': not args.no_viz,
        'enable_hr': not args.no_hr, 'hr_device_type': args.hr_device if not args.no_hr else 'none',
        'ble_keyword': args.ble_keyword, 'ble_timeout': args.ble_timeout, 'fallback_simulated': not args.no_fallback,
        'backend_url': args.backend_url, 'enable_backend': not args.no_backend
    }
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config.update(json.load(f))

    temp_dir = os.path.join(os.path.dirname(args.output), 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    temp_config = os.path.join(temp_dir, f'temp_config_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    with open(temp_config, 'w') as f:
        json.dump(config, f, indent=2)

    collector = None
    try:
        collector = EnhancedDataCollector(temp_config)
        collector.run(duration_seconds=args.duration)
    except Exception as e:
        logger.error(f"运行失败: {e}")
        if collector: collector.stop()
    finally:
        if os.path.exists(temp_config):
            try:
                os.remove(temp_config)
            except:
                pass


if __name__ == "__main__":
    main()