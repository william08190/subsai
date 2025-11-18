#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
最终卡拉OK测试 - 不使用sys.path修改
"""

from subsai import SubsAI, Tools
from subsai.karaoke_generator import create_karaoke_subtitles
import os

def final_test():
    print("🎤 最终卡拉OK生成测试\\n")

    # 测试视频
    test_video = "/tmp/test_video.mp4"
    print(f"📹 测试视频: {test_video}")

    # 1. 创建模型并转录
    print("\\n1️⃣ 转录中...")
    subs_ai = SubsAI()
    model = subs_ai.create_model('openai/whisper', {'model_type': 'tiny'})
    subs = subs_ai.transcribe(test_video, model)
    print(f"   ✅ 生成 {len(subs)} 个字幕")

    # 2. 生成卡拉OK字幕
    print("\\n2️⃣ 生成卡拉OK字幕...")
    karaoke_subs = create_karaoke_subtitles(subs, style_name='classic', words_per_line=10)
    print(f"   ✅ 生成 {len(karaoke_subs)} 个卡拉OK事件")

    # 调试：检查styles
    print(f"\\n   🔍 Styles: {list(karaoke_subs.styles.keys())}")
    for key, val in karaoke_subs.styles.items():
        print(f"      {key}: {type(val)}")

    # 3. 烧录到视频
    print("\\n3️⃣ 烧录卡拉OK字幕到视频...")
    tools = Tools()
    output = tools.burn_karaoke_subtitles(
        subs=karaoke_subs,
        media_file=test_video,
        output_filename="final_test_karaoke"
    )

    print(f"\\n✅ 成功！输出: {output}")
    if os.path.exists(output):
        size = os.path.getsize(output) / 1024 / 1024
        print(f"   文件大小: {size:.2f} MB")

if __name__ == '__main__':
    try:
        final_test()
    except Exception as e:
        print(f"\\n❌ 失败: {e}")
        import traceback
        traceback.print_exc()
