#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
完整的卡拉OK端到端测试 - 生成视频并截图验证
"""

import sys
import os
import subprocess
sys.path.insert(0, '/subsai/src')

from pysubs2 import SSAFile, SSAEvent
from subsai.karaoke_generator import KaraokeGenerator
from subsai.main import SubsAI

def create_test_video():
    """创建测试视频"""
    print("\n1. 创建测试视频...")

    # 创建480x832的竖屏视频
    width, height = 480, 832
    fps = 30
    duration = 6  # 6秒

    video_path = "/tmp/test_karaoke_input.mp4"

    # 使用系统ffmpeg创建纯色视频
    cmd = [
        '/usr/bin/ffmpeg', '-y',  # 使用系统ffmpeg
        '-f', 'lavfi',
        '-i', f'color=c=blue:s={width}x{height}:r={fps}:d={duration}',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        video_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"   ✅ 测试视频已创建: {video_path}")
        return video_path
    else:
        print(f"   ❌ 创建视频失败: {result.stderr}")
        return None

def create_test_subtitles_with_timestamps():
    """创建带词级时间戳的测试字幕"""
    print("\n2. 创建带词级时间戳的测试字幕...")

    test_subs = SSAFile()

    # 模拟whisper-timestamped的输出格式 (带词级标记)
    # 第一句: "Hello world this" (0-2秒)
    test_subs.append(SSAEvent(
        start=0,
        end=2000,
        text="{\\i1}Hello{\\i0} {\\i1}world{\\i0} {\\i1}this{\\i0}"
    ))

    # 第二句: "is a test" (2-4秒)
    test_subs.append(SSAEvent(
        start=2000,
        end=4000,
        text="{\\i1}is{\\i0} {\\i1}a{\\i0} {\\i1}test{\\i0}"
    ))

    # 第三句: "karaoke video" (4-6秒)
    test_subs.append(SSAEvent(
        start=4000,
        end=6000,
        text="{\\i1}karaoke{\\i0} {\\i1}video{\\i0}"
    ))

    print(f"   ✅ 创建了 {len(test_subs)} 个字幕事件")
    return test_subs

def test_karaoke_generation():
    """测试卡拉OK生成"""
    print("\n3. 生成卡拉OK字幕...")

    # 创建生成器
    generator = KaraokeGenerator(
        style_name="classic",
        words_per_line=5,
        fontsize=36
    )

    print(f"   - 样式: {generator.style.name}")
    print(f"   - 样式key: {generator.style.style_key}")
    print(f"   - 字体大小: {generator.style.get_fontsize()}")

    # 测试标签格式
    tag = generator.style.get_karaoke_tags(50)
    print(f"   - 卡拉OK标签示例: {tag}")

    # 创建测试字幕
    test_subs = create_test_subtitles_with_timestamps()

    # 生成卡拉OK
    karaoke_subs = generator.generate(test_subs)

    print(f"\n   生成结果:")
    print(f"   - 事件数量: {len(karaoke_subs)}")
    print(f"   - 样式数量: {len(karaoke_subs.styles)}")

    for style_name, style_obj in karaoke_subs.styles.items():
        print(f"   - 样式名称: {style_name}")
        print(f"     字体大小: {style_obj.fontsize}")
        print(f"     主色: {style_obj.primarycolor}")
        print(f"     次色 (高亮): {style_obj.secondarycolor}")

    # 显示前2个事件
    print(f"\n   卡拉OK事件内容:")
    for i, event in enumerate(karaoke_subs[:2]):
        print(f"   事件{i+1}: {event.text[:80]}...")
        if "{\\kf" in event.text:
            print(f"   ✅ 包含填充效果标签 (\\kf)")
        else:
            print(f"   ❌ 没有填充效果标签")

    # 保存ASS文件
    ass_path = "/tmp/test_karaoke_final.ass"
    karaoke_subs.save(ass_path)
    print(f"\n   ✅ ASS文件已保存: {ass_path}")

    # 显示ASS文件内容
    with open(ass_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        print("\n   ASS文件头部 (前30行):")
        for i, line in enumerate(lines[:30], 1):
            print(f"   {i:2d}: {line.rstrip()}")

    return ass_path

def burn_karaoke_to_video(video_path, ass_path):
    """将卡拉OK字幕烧录到视频"""
    print("\n4. 烧录卡拉OK字幕到视频...")

    output_path = "/tmp/test_karaoke_output_final.mp4"

    cmd = [
        '/usr/bin/ffmpeg', '-y',  # 使用系统ffmpeg
        '-i', video_path,
        '-vf', f"ass={ass_path}",
        '-c:v', 'libx264',
        '-crf', '23',
        '-preset', 'medium',
        '-c:a', 'copy',
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"   ✅ 卡拉OK视频已生成: {output_path}")
        return output_path
    else:
        print(f"   ❌ 烧录失败: {result.stderr}")
        return None

def extract_screenshots(video_path):
    """提取多个时间点的截图"""
    print("\n5. 提取截图验证效果...")

    timestamps = [0.5, 1.5, 3.0, 5.0]  # 在不同时间点提取
    screenshots = []

    for ts in timestamps:
        screenshot_path = f"/tmp/karaoke_screenshot_{ts}s.png"

        cmd = [
            '/usr/bin/ffmpeg', '-y',  # 使用系统ffmpeg
            '-i', video_path,
            '-ss', str(ts),
            '-vframes', '1',
            screenshot_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            screenshots.append(screenshot_path)
            print(f"   ✅ 截图已保存: {screenshot_path} (t={ts}s)")
        else:
            print(f"   ❌ 截图失败: {result.stderr}")

    return screenshots

def main():
    print("=" * 60)
    print("卡拉OK端到端测试 - 最终验证")
    print("=" * 60)

    # 1. 创建测试视频
    video_path = create_test_video()
    if not video_path:
        return

    # 2. 生成卡拉OK字幕
    ass_path = test_karaoke_generation()
    if not ass_path:
        return

    # 3. 烧录到视频
    output_path = burn_karaoke_to_video(video_path, ass_path)
    if not output_path:
        return

    # 4. 提取截图
    screenshots = extract_screenshots(output_path)

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print(f"\n生成的文件:")
    print(f"  - 输入视频: {video_path}")
    print(f"  - ASS字幕: {ass_path}")
    print(f"  - 输出视频: {output_path}")
    print(f"  - 截图: /tmp/karaoke_screenshot_*.png")
    print(f"\n请复制截图到Windows查看效果！")
    print(f"\n在Windows中运行:")
    print(f"  docker cp subsai-webui:/tmp/karaoke_screenshot_1.5s.png .")

if __name__ == '__main__':
    main()
