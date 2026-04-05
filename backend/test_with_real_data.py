import requests
import json
import os
import glob
from datetime import datetime
import sys


def find_latest_feature_file():
    """查找最新的特征文件"""
    data_dir = r"D:\pythoncode\DaChuang\data\collected"

    if not os.path.exists(data_dir):
        print(f"数据目录不存在: {data_dir}")
        return None

    sessions = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
    if not sessions:
        print("没有找到会话目录")
        return None

    sessions.sort(reverse=True)
    latest_session = sessions[0]
    session_path = os.path.join(data_dir, latest_session)

    features_dir = os.path.join(session_path, "features")
    if not os.path.exists(features_dir):
        print(f"特征目录不存在: {features_dir}")
        return None

    feature_files = glob.glob(os.path.join(features_dir, "features_*.json"))
    if not feature_files:
        print("没有找到特征文件")
        return None

    feature_files.sort(reverse=True)
    latest_file = feature_files[0]

    print(f"找到最新特征文件: {latest_file}")
    return latest_file


def load_features_from_file(file_path):
    """从文件加载特征数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not data:
            print("文件为空")
            return None

        # 取最新的数据包（最后一个，不是第一个）
        packet = data[-1] if len(data) > 1 else data[0]

        features = {
            "face_features": packet.get("face_features", [0.5] * 13),
            "audio_features": packet.get("audio_features", [0.5] * 21),
            "hr_features": packet.get("hr_features", [0.5] * 9)
        }

        # 显示特征统计
        print(f"\n特征统计:")
        print(f"  面部特征: {len(features['face_features'])}维, "
              f"范围: [{min(features['face_features']):.3f}, {max(features['face_features']):.3f}]")
        print(f"  音频特征: {len(features['audio_features'])}维, "
              f"范围: [{min(features['audio_features']):.3f}, {max(features['audio_features']):.3f}]")
        print(f"  心率特征: {len(features['hr_features'])}维, "
              f"范围: [{min(features['hr_features']):.3f}, {max(features['hr_features']):.3f}]")

        if "timestamp" in packet:
            dt = datetime.fromtimestamp(packet["timestamp"])
            print(f"  采集时间: {dt.strftime('%Y-%m-%d %H:%M:%S')}")

        return features, packet.get("timestamp", None)

    except Exception as e:
        print(f"加载特征文件失败: {e}")
        return None, None


def save_prediction_for_html(result, test_data, data_timestamp):
    """保存预测结果为HTML可读的JSON文件"""
    try:
        # 创建保存目录
        save_dir = "static/predictions"
        os.makedirs(save_dir, exist_ok=True)

        # 生成文件名（固定文件名，方便HTML读取）
        filename = "latest_prediction.json"
        filepath = os.path.join(save_dir, filename)

        # 格式化时间
        data_time_str = ""
        if data_timestamp:
            data_time = datetime.fromtimestamp(data_timestamp)
            data_time_str = data_time.strftime('%Y-%m-%d %H:%M:%S')

        # 保存结果
        output = {
            "success": True,
            "prediction": result.get("prediction"),
            "prediction_code": result.get("prediction_code"),
            "score": result.get("score"),
            "confidence": result.get("confidence"),
            "confidence_percent": round(result.get("confidence", 0) * 100, 1),
            "contributions": result.get("contributions"),
            "explanation": result.get("explanation"),
            "timestamp": result.get("timestamp"),
            "data_timestamp": data_time_str,
            "data_timestamp_raw": data_timestamp,
            "model_used": result.get("model_used"),
            "feature_summary": {
                "face_min": round(min(test_data.get("face_features", [0])), 3),
                "face_max": round(max(test_data.get("face_features", [0])), 3),
                "audio_min": round(min(test_data.get("audio_features", [0])), 3),
                "audio_max": round(max(test_data.get("audio_features", [0])), 3),
                "hr_min": round(min(test_data.get("hr_features", [0])), 3),
                "hr_max": round(max(test_data.get("hr_features", [0])), 3)
            }
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"\n✅ 预测结果已保存到: {filepath}")
        print(f"   可在浏览器中查看: file:///{os.path.abspath('test_display.html')}")

        return True

    except Exception as e:
        print(f"保存预测结果失败: {e}")
        return False


def test_predict_with_real_data():
    """使用真实采集的数据进行预测测试"""
    print("=" * 60)
    print("心理健康预测测试 - 使用真实采集数据")
    print("=" * 60)

    # 1. 检查API服务
    print("\n1. 检查API服务...")
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            print("✅ API服务正常运行")
        else:
            print(f"❌ API服务异常: {response.status_code}")
            return
    except:
        print("❌ 无法连接到API服务，请确保已运行 python app.py")
        return

    # 2. 查找并加载最新的特征数据
    print("\n2. 查找最新采集的特征数据...")
    feature_file = find_latest_feature_file()
    data_timestamp = None

    if not feature_file:
        print("⚠️ 没有找到采集数据，使用示例数据")
        test_data = {
            "face_features": [0.5] * 13,
            "audio_features": [0.5] * 21,
            "hr_features": [0.5] * 9
        }
        print("   使用示例数据（所有特征=0.5）")
    else:
        result = load_features_from_file(feature_file)
        if result:
            test_data, data_timestamp = result
        else:
            print("加载特征失败，使用示例数据")
            test_data = {
                "face_features": [0.5] * 13,
                "audio_features": [0.5] * 21,
                "hr_features": [0.5] * 9
            }

    # 3. 发送预测请求
    print("\n3. 发送预测请求...")
    try:
        response = requests.post(
            'http://localhost:5000/predict',
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        print(f"\n响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()

            # 在控制台显示结果
            print("\n" + "=" * 60)
            print("预测结果")
            print("=" * 60)
            print(f"心理状态: {result['prediction']}")
            print(f"压力分数: {result['score']} 分")
            print(f"置信度: {result['confidence'] * 100:.1f}%")
            print(f"\n各模态贡献度:")
            print(f"  面部表情: {result['contributions']['face']}%")
            print(f"  语音特征: {result['contributions']['audio']}%")
            print(f"  心率变化: {result['contributions']['hr']}%")
            print(f"\n解释: {result['explanation']}")
            print(f"\n预测时间: {result['timestamp']}")

            # 保存为HTML可读取的JSON文件
            save_prediction_for_html(result, test_data, data_timestamp)

            print("\n" + "=" * 60)
            print("✅ 完成！现在可以在HTML页面中查看结果")
            print("=" * 60)

        else:
            print(f"❌ 预测失败: {response.json()}")

    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except Exception as e:
        print(f"❌ 请求失败: {e}")


if __name__ == "__main__":
    test_predict_with_real_data()