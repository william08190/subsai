#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成测试视频和字幕
"""

import cv2
import numpy as np
from pathlib import Path

# 创建test_data目录
test_data_dir = Path('test_data')
test_data_dir.mkdir(exist_ok=True)

# 视频参数
width, height = 1280, 720  # 720p分辨率
fps = 30
duration = 15  # 15秒
total_frames = fps * duration

# 创建视频写入器
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
output_file = str(test_data_dir / 'test_video.mp4')
video_writer = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

print("🎬 正在生成测试视频...")

for frame_num in range(total_frames):
    # 创建彩色渐变背景
    frame = np.zeros((height, width, 3), dtype=np.uint8)

    # 时间相关的颜色变化
    t = frame_num / total_frames
    r = int(128 + 127 * np.sin(2 * np.pi * t))
    g = int(128 + 127 * np.sin(2 * np.pi * t + 2 * np.pi / 3))
    b = int(128 + 127 * np.sin(2 * np.pi * t + 4 * np.pi / 3))

    frame[:, :] = (b, g, r)

    # 添加一些图案
    cv2.rectangle(frame, (100, 100), (width-100, height-100), (255, 255, 255), 3)
    cv2.putText(frame, f'Test Frame {frame_num}', (width//2-150, height//2),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # 添加时间显示
    time_str = f'{frame_num/fps:.2f}s / {duration}s'
    cv2.putText(frame, time_str, (width//2-100, height-100),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    video_writer.write(frame)

    if (frame_num + 1) % 30 == 0:
        print(f"  进度: {(frame_num + 1) / total_frames * 100:.1f}%")

video_writer.release()

print(f"✅ 测试视频已生成: {output_file}")
print(f"   分辨率: {width}x{height} (720p)")
print(f"   时长: {duration}秒")
print(f"   帧率: {fps} fps")

# 验证文件
import os
file_size = os.path.getsize(output_file) / (1024*1024)
print(f"   文件大小: {file_size:.2f} MB")
