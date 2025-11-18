#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试视频宽高比裁剪功能

验证内容：
1. 原始尺寸（无裁剪）
2. 16:9 横屏裁剪
3. 9:16 竖屏裁剪
4. 1:1 正方形裁剪
5. 4:3 传统电视裁剪
"""

import sys
import os
import subprocess
from pathlib import Path

sys.path.insert(0, '/subsai/src')

from pysubs2 import SSAFile, SSAEvent
from subsai.karaoke_generator import create_karaoke_subtitles
from subsai import Tools

def create_test_video(output_path: str, width: int, height: int, duration: int = 6):
    """创建测试视频"""
    print(f"  📹 创建测试视频 {width}x{height} ({duration}秒)...")

    # 使用系统ffmpeg，兼容旧版本
    cmd = [
        '/usr/bin/ffmpeg', '-y',
        '-f', 'lavfi',
        '-i', f'color=c=blue:s={width}x{height}:d={duration}',
        '-f', 'lavfi',
        '-i', f'anullsrc=r=44100:cl=stereo',  # 不使用duration参数，用-t代替
        '-t', str(duration),  # 使用-t指定输出时长
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-shortest',
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        print(f"  ❌ 创建视频失败: {result.stderr.decode('utf-8', errors='ignore')}")
        return False

    if os.path.exists(output_path):
        print(f"  ✅ 测试视频创建成功: {output_path}")
        return True
    else:
        print(f"  ❌ 视频文件不存在")
        return False

def get_video_dimensions(video_path: str):
    """获取视频尺寸"""
    cmd = [
        '/usr/bin/ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height',
        '-of', 'csv=s=x:p=0',
        video_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        dims = result.stdout.strip().split('x')
        return int(dims[0]), int(dims[1])
    return None, None

def test_aspect_ratio_cropping():
    """测试宽高比裁剪功能"""
    print("=" * 70)
    print("测试视频宽高比裁剪功能")
    print("=" * 70)

    # 创建测试目录
    test_dir = Path("/tmp/karaoke_aspect_ratio_test")
    test_dir.mkdir(exist_ok=True)
    print(f"\n📁 测试目录: {test_dir}")

    # 1. 创建测试视频（1920x1080, 16:9）
    print("\n1️⃣  准备测试视频...")
    test_video_path = test_dir / "test_video_1920x1080.mp4"

    if not create_test_video(str(test_video_path), 1920, 1080, 6):
        print("❌ 无法创建测试视频，测试终止")
        return False

    # 验证原始尺寸
    orig_w, orig_h = get_video_dimensions(str(test_video_path))
    print(f"  📺 原始视频尺寸: {orig_w}x{orig_h} (宽高比: {orig_w/orig_h:.3f})")

    # 2. 创建测试字幕
    print("\n2️⃣  创建测试字幕...")
    test_subs = SSAFile()
    test_subs.append(SSAEvent(start=0, end=2000, text="Hello world this is"))
    test_subs.append(SSAEvent(start=2000, end=4000, text="a karaoke test video"))
    test_subs.append(SSAEvent(start=4000, end=6000, text="with aspect ratio cropping"))

    karaoke_subs = create_karaoke_subtitles(
        subs=test_subs,
        style_name='classic',
        words_per_line=5
    )
    print(f"  ✅ 生成了 {len(karaoke_subs)} 个卡拉OK字幕事件")

    # 3. 测试各种宽高比
    test_cases = [
        ("原���尺寸 (无裁剪)", None, 1920, 1080),
        ("16:9 横屏", "16:9", 1920, 1080),  # 应该无裁剪
        ("9:16 竖屏", "9:16", 608, 1080),   # 裁剪宽度
        ("4:3 传统电视", "4:3", 1440, 1080),  # 裁剪宽度
        ("1:1 正方形", "1:1", 1080, 1080),  # 裁剪宽度
    ]

    tools = Tools()
    results = []

    print("\n3️⃣  测试���种宽高比裁剪...")
    for idx, (name, aspect_ratio, expected_w, expected_h) in enumerate(test_cases, 1):
        print(f"\n  [{idx}/{len(test_cases)}] 测试: {name}")
        print(f"      目标宽高比: {aspect_ratio or '原始'}")
        print(f"      预期输出尺寸: {expected_w}x{expected_h}")

        # 生成输出文件名
        output_name = f"test_output_{aspect_ratio.replace(':', '_') if aspect_ratio else 'original'}"

        try:
            # 调用烧录函数
            output_path = tools.burn_karaoke_subtitles(
                subs=karaoke_subs,
                media_file=str(test_video_path),
                output_filename=output_name,
                aspect_ratio=aspect_ratio
            )

            # 验证输出
            if os.path.exists(output_path):
                actual_w, actual_h = get_video_dimensions(output_path)

                # 检查尺寸是否正确（允许±2像素误差，因为需要偶数尺寸）
                w_match = abs(actual_w - expected_w) <= 2
                h_match = abs(actual_h - expected_h) <= 2

                if w_match and h_match:
                    print(f"      ✅ 成功！实际尺寸: {actual_w}x{actual_h}")
                    results.append((name, True, f"{actual_w}x{actual_h}"))
                else:
                    print(f"      ❌ 失败！实际尺寸: {actual_w}x{actual_h}, 预期: {expected_w}x{expected_h}")
                    results.append((name, False, f"{actual_w}x{actual_h} (预期: {expected_w}x{expected_h})"))
            else:
                print(f"      ❌ 输出文件不存在")
                results.append((name, False, "文件不存在"))

        except Exception as e:
            print(f"      ❌ 异常: {str(e)}")
            results.append((name, False, str(e)))

    # 4. 汇总结果
    print("\n" + "=" * 70)
    print("测试结果汇总")
    print("=" * 70)

    success_count = sum(1 for _, success, _ in results if success)
    total_count = len(results)

    for name, success, details in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {status} - {name}: {details}")

    print(f"\n📊 总计: {success_count}/{total_count} 测试通过")

    if success_count == total_count:
        print("🎉 所有测试通过！")
        return True
    else:
        print("⚠️  部分测试失败，请检查日志")
        return False

if __name__ == '__main__':
    success = test_aspect_ratio_cropping()
    sys.exit(0 if success else 1)
