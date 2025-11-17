#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试ffmpeg字幕烧录功能
Test ffmpeg subtitle burning functionality
"""

import tempfile
import os
import pysubs2
import ffmpeg
from pathlib import Path

def test_ffmpeg_subtitle_merge():
    """测试ffmpeg字幕合并"""
    print("=== 测试ffmpeg字幕合并功能 ===\n")

    # 1. 创建测试字幕文件
    print("1. 创建测试SRT字幕文件...")
    test_srt = "/tmp/test_merge.srt"
    subs = pysubs2.SSAFile()
    subs.append(pysubs2.SSAEvent(start=0, end=2000, text="Test subtitle line 1"))
    subs.append(pysubs2.SSAEvent(start=2000, end=4000, text="Test subtitle line 2"))
    subs.append(pysubs2.SSAEvent(start=4000, end=6000, text="Test subtitle line 3"))
    subs.save(test_srt)

    if os.path.exists(test_srt):
        size = os.path.getsize(test_srt)
        print(f"   ✅ SRT文件已创��: {test_srt} ({size} 字节)\n")
        with open(test_srt, 'r') as f:
            print(f"   内容预览:\n{f.read()}\n")
    else:
        print(f"   ❌ SRT文件创建失败\n")
        return

    # 2. 检查测试视频是否存在
    print("2. 检查测试视频...")
    test_video_paths = [
        "/subsai/assets/video/test1.webm",
        "/subsai/assets/video/test0.webm",
        "/tmp/test_video.mp4"
    ]

    test_video = None
    for path in test_video_paths:
        if os.path.exists(path):
            test_video = path
            print(f"   ✅ 找到测试视频: {test_video}\n")
            break

    if not test_video:
        print("   ⚠️ 未找到测试视频，跳过ffmpeg测试")
        print("   提示: 如果要完整测试，请提供测试视频文件\n")
        return

    # 3. 测试ffmpeg命令
    print("3. 测试ffmpeg字幕合并命令...")
    output_video = "/tmp/test_output_with_subs.mp4"

    try:
        # 构建ffmpeg命令（软字幕）
        input_video = ffmpeg.input(test_video)
        input_subs = ffmpeg.input(test_srt)

        output = ffmpeg.output(
            input_video['v'],
            input_video['a'],
            input_subs['s'],
            output_video,
            vcodec='copy',
            acodec='copy',
            scodec='mov_text',
            **{'metadata:s:s:0': 'title=Test'}
        )

        output = ffmpeg.overwrite_output(output)

        # 打印命令
        cmd = ffmpeg.compile(output)
        print(f"   ffmpeg命令: {' '.join(cmd)}\n")

        # 执行ffmpeg
        print("   执行ffmpeg...")
        stdout, stderr = ffmpeg.run(output, capture_stdout=True, capture_stderr=True)

        if os.path.exists(output_video):
            size = os.path.getsize(output_video)
            print(f"   ✅ 输出视频已创建: {output_video} ({size} 字节)")

            # 检查字幕流
            probe = ffmpeg.probe(output_video)
            print(f"\n   视频信息:")
            for stream in probe['streams']:
                print(f"     - {stream['codec_type']}: {stream.get('codec_name', 'unknown')}")
                if stream['codec_type'] == 'subtitle':
                    print(f"       标题: {stream.get('tags', {}).get('title', 'N/A')}")

            print(f"\n   ✅ ffmpeg字幕合并测试成功！\n")
        else:
            print(f"   ❌ 输出视频未创建\n")

    except ffmpeg.Error as e:
        print(f"   ❌ ffmpeg执行失败:")
        print(f"   错误信息: {e.stderr.decode('utf-8', errors='ignore')}\n")
    except Exception as e:
        print(f"   ❌ 测试失败: {e}\n")

    # 清理
    print("4. 清理测试文件...")
    for path in [test_srt, output_video]:
        if os.path.exists(path):
            os.unlink(path)
            print(f"   🗑️ 删除: {path}")

    print("\n=== 测试完成 ===")

if __name__ == '__main__':
    test_ffmpeg_subtitle_merge()
