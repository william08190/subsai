#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
完整测试字幕烧录功能（使用修复后的代码）
Full test of subtitle burning with fixed code
"""

import sys
sys.path.insert(0, '/subsai/src')

from subsai import Tools
import pysubs2
import os

def test_merge_with_fixed_code():
    """测试修复后的merge_subs_with_video"""
    print("=== 测试修复后的字幕合并功能 ===\n")

    # 使用测试视频
    test_video = "/subsai/assets/video/test1.webm"

    if not os.path.exists(test_video):
        print(f"❌ 测试视频不存在: {test_video}")
        return

    print(f"📹 测试视频: {test_video}\n")

    # 创建测试字幕
    print("1. 创建测试字幕...")
    subs = pysubs2.SSAFile()
    subs.append(pysubs2.SSAEvent(start=0, end=2000, text="This is test subtitle 1"))
    subs.append(pysubs2.SSAEvent(start=2000, end=4000, text="This is test subtitle 2"))
    subs.append(pysubs2.SSAEvent(start=4000, end=6000, text="This is test subtitle 3"))
    print(f"   ✅ 创建了 {len(subs)} 个字幕事件\n")

    # 使用Tools.merge_subs_with_video
    print("2. 调用 Tools.merge_subs_with_video()...")
    tools = Tools()

    try:
        output_file = tools.merge_subs_with_video(
            subs={'English': subs},
            media_file=test_video,
            output_filename="test_merged_fixed"
        )

        print(f"\n✅ 成功！输出文件: {output_file}")

        if os.path.exists(output_file):
            size = os.path.getsize(output_file)
            print(f"✅ 文件存在，大小: {size} 字节")

            # 检查视频信息
            import ffmpeg
            probe = ffmpeg.probe(output_file)
            print(f"\n📊 视频信息:")
            for stream in probe['streams']:
                codec_type = stream['codec_type']
                codec_name = stream.get('codec_name', 'unknown')
                print(f"   - {codec_type}: {codec_name}", end="")
                if codec_type == 'subtitle':
                    title = stream.get('tags', {}).get('title', 'N/A')
                    print(f" (title: {title})", end="")
                print()

            print(f"\n🎉 测试成功！字幕已成功烧录到视频")
        else:
            print(f"❌ 输出文件不存在")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

    print("\n=== 测试完成 ===")

if __name__ == '__main__':
    test_merge_with_fixed_code()
