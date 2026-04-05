#!/usr/bin/env python3
"""
摄像头测试工具
用法：
    python test_camera.py            # 测试索引 0
    python test_camera.py --index 1  # 测试索引 1
    python test_camera.py --list      # 列出可用摄像头索引
    python test_camera.py --all       # 依次测试索引 0~9
"""

import cv2
import argparse
import time
import sys


def list_cameras(max_index=10):
    """尝试打开 0~max_index 摄像头，返回可用的索引列表"""
    available = []
    for i in range(max_index):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                available.append(i)
                print(f"✓ 索引 {i}: 可用 (分辨率 {frame.shape[1]}x{frame.shape[0]})")
            else:
                print(f"✗ 索引 {i}: 可打开但无法读取图像")
            cap.release()
        else:
            print(f"✗ 索引 {i}: 无法打开")
    return available


def test_single_camera(index, duration=30, show_fps=True):
    """测试单个摄像头，显示实时画面"""
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        print(f"❌ 无法打开摄像头索引 {index}")
        return False

    # 获取摄像头属性
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    backend = cap.getBackendName() if hasattr(cv2.VideoCapture, 'getBackendName') else "Unknown"

    print(f"✅ 成功打开摄像头索引 {index}")
    print(f"   分辨率: {width}x{height}")
    print(f"   标称帧率: {fps} FPS")
    print(f"   后端: {backend}")
    print("按 'q' 或 'ESC' 退出预览\n")

    frame_count = 0
    start_time = time.time()
    last_fps_update = start_time
    fps_display = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ 无法读取帧，可能摄像头已断开")
            break

        frame_count += 1
        now = time.time()
        if now - last_fps_update >= 1.0:
            fps_display = frame_count / (now - start_time)
            last_fps_update = now

        # 显示信息
        if show_fps:
            cv2.putText(frame, f"FPS: {fps_display:.1f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Index: {index}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow(f"Camera Test (Index {index})", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:  # q or ESC
            break

        if duration > 0 and (now - start_time) > duration:
            print(f"测试时长 {duration} 秒结束")
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"共处理 {frame_count} 帧，平均 FPS: {frame_count / (time.time() - start_time):.1f}")
    return True


def main():
    parser = argparse.ArgumentParser(description="摄像头测试工具")
    parser.add_argument('--index', '-i', type=int, default=None,
                        help="指定要测试的摄像头索引")
    parser.add_argument('--list', '-l', action='store_true',
                        help="列出所有可用摄像头索引")
    parser.add_argument('--all', '-a', action='store_true',
                        help="依次测试所有可用摄像头（索引0~9）")
    parser.add_argument('--duration', '-d', type=int, default=30,
                        help="测试持续时间（秒），0表示无限直到按q")
    parser.add_argument('--no-fps', action='store_true',
                        help="不显示帧率信息")

    args = parser.parse_args()

    if args.list:
        list_cameras(max_index=10)
        return

    if args.all:
        available = list_cameras(max_index=10)
        if not available:
            print("未找到任何可用摄像头")
            return
        for idx in available:
            print(f"\n--- 测试摄像头索引 {idx} ---")
            test_single_camera(idx, duration=args.duration, show_fps=not args.no_fps)
        return

    if args.index is not None:
        test_single_camera(args.index, duration=args.duration, show_fps=not args.no_fps)
        return

    # 默认：测试索引 0
    print("未指定参数，默认测试摄像头索引 0\n")
    test_single_camera(0, duration=args.duration, show_fps=not args.no_fps)


if __name__ == "__main__":
    main()