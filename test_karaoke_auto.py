#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
自动测试卡拉OK生成功能
"""

import sys
import os
import json

# 添加src路径
sys.path.insert(0, '/subsai/src')

from subsai import SubsAI, Tools
from subsai.karaoke_generator import create_karaoke_subtitles

def test_karaoke_generation():
    """测试卡拉OK生成"""
    print("=" * 60)
    print("🎤 开始自动测试卡拉OK生成功能")
    print("=" * 60)

    # 测试视频
    test_video = "/tmp/test_video.mp4"

    # 检查视频是否存在
    if not os.path.exists(test_video):
        print(f"❌ 测试视频不存在: {test_video}")
        return False

    print(f"\n📹 测试视频: {test_video}")
    video_size = os.path.getsize(test_video) / 1024 / 1024
    print(f"   视频大小: {video_size:.2f} MB")

    try:
        # 1. 创建模型配置
        print("\n1️⃣ 创建Whisper模型...")
        model_config = {
            'model_type': 'tiny',
            'compute_type': 'int8'
        }

        subs_ai = SubsAI()
        model = subs_ai.create_model('openai/whisper', model_config)
        print("   ✅ 模型创建成功")

        # 2. 转录生成字幕
        print("\n2️⃣ 转录视频生成字幕...")
        subs = subs_ai.transcribe(test_video, model)
        print(f"   ✅ 生成了 {len(subs)} 个字幕事件")

        # 打印前3个字幕
        print("\n   前3个字幕内容:")
        for i, sub in enumerate(subs[:3]):
            print(f"   [{i+1}] {sub.start}ms - {sub.end}ms: {sub.text}")

        # 3. 生成卡拉OK字幕
        print("\n3️⃣ 生成卡拉OK字幕...")
        karaoke_subs = create_karaoke_subtitles(
            subs=subs,
            style_name='classic',
            words_per_line=10
        )

        if karaoke_subs is None or len(karaoke_subs) == 0:
            print("   ❌ 卡拉OK字幕生成失败")
            return False

        print(f"   ✅ 生成了 {len(karaoke_subs)} 个卡拉OK字幕事件")

        # 保存ASS字幕文件
        ass_file = "/tmp/test_karaoke.ass"
        karaoke_subs.save(ass_file)
        print(f"   💾 保存ASS文件: {ass_file}")

        # 检查ASS文件内容
        if os.path.exists(ass_file):
            with open(ass_file, 'r', encoding='utf-8') as f:
                ass_content = f.read()
                if '\\k' in ass_content:
                    print("   ✅ ASS文件包含卡拉OK标签 (\\k)")
                else:
                    print("   ⚠️ ASS文件不包含卡拉OK标签")

        # 4. 烧录卡拉OK字幕到视频
        print("\n4️⃣ 烧录卡拉OK字幕到视频...")
        tools = Tools()

        output_video = tools.burn_karaoke_subtitles(
            subs=karaoke_subs,
            media_file=test_video,
            output_filename="test_karaoke_output",
            video_codec='libx264',
            crf=23
        )

        print(f"   ✅ 卡拉OK视频生成成功!")
        print(f"   📁 输出文件: {output_video}")

        # 检查输出文件
        if os.path.exists(output_video):
            output_size = os.path.getsize(output_video) / 1024 / 1024
            print(f"   📦 输出大小: {output_size:.2f} MB")

            # 使用ffprobe检查视频信息
            import subprocess
            try:
                result = subprocess.run(
                    ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', output_video],
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    streams_info = json.loads(result.stdout)
                    print("\n   📊 输出视频流信息:")
                    for stream in streams_info.get('streams', []):
                        codec_type = stream.get('codec_type')
                        codec_name = stream.get('codec_name')
                        print(f"      - {codec_type}: {codec_name}")

                    # 检查是否有字幕流
                    subtitle_streams = [s for s in streams_info.get('streams', []) if s.get('codec_type') == 'subtitle']
                    if subtitle_streams:
                        print(f"   ⚠️ 视频包含 {len(subtitle_streams)} 个字幕流（应该是硬字幕，不应该有字幕流）")
                    else:
                        print(f"   ✅ 视频没有字幕流（字幕已烧录为硬字幕）")

            except Exception as e:
                print(f"   ⚠️ 无法检查视频信息: {e}")
        else:
            print(f"   ❌ 输出文件不存在")
            return False

        print("\n" + "=" * 60)
        print("🎉 卡拉OK生成测试成功!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_karaoke_generation()
    sys.exit(0 if success else 1)
