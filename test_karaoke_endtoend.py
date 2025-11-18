#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
端到端卡拉OK测试 - 生成视频并验证
"""

import os
import subprocess
from pysubs2 import SSAFile, SSAEvent
from subsai import Tools
from subsai.karaoke_generator import create_karaoke_subtitles

def test_full_karaoke_pipeline():
    """完整测试卡拉OK生成和烧录流程"""

    print("=" * 70)
    print("🎬 端到端卡拉OK测试")
    print("=" * 70)

    # 1. 创建测试字幕
    print("\n[步骤1] 创建测试字幕...")
    test_subs = SSAFile()
    test_subs.append(SSAEvent(start=0, end=2000, text="Hello world this is"))
    test_subs.append(SSAEvent(start=2000, end=4000, text="a karaoke test video"))
    test_subs.append(SSAEvent(start=4000, end=6000, text="checking tag display"))
    print(f"✅ 创建了 {len(test_subs)} 个字幕事件")

    # 2. 生成卡拉OK字幕
    print("\n[步骤2] 生成卡拉OK字幕...")
    karaoke_subs = create_karaoke_subtitles(
        subs=test_subs,
        style_name='classic',
        words_per_line=3,
        fontsize=36
    )
    print(f"✅ 生成了 {len(karaoke_subs)} 个卡拉OK事件")

    # 打印卡拉OK事件内容
    print("\n卡拉OK事件内容:")
    for i, event in enumerate(karaoke_subs):
        text_preview = event.text[:60] + "..." if len(event.text) > 60 else event.text
        print(f"  事件{i+1}: {text_preview}")
        # 检查是否包含 \k 标签
        if '\\k' in event.text:
            print(f"    ✅ 包含卡拉OK标签")
        else:
            print(f"    ❌ 缺少卡拉OK标签")

    # 3. 创建测试视频（3秒彩色条纹）
    print("\n[步骤3] 创建测试视频...")
    test_video = "/tmp/test_karaoke_input.mp4"

    ffmpeg_create_cmd = [
        '/usr/bin/ffmpeg',
        '-f', 'lavfi',
        '-i', 'testsrc=duration=6:size=480x832:rate=30',
        '-c:v', 'libx264',
        '-t', '6',
        '-y',
        test_video
    ]

    result = subprocess.run(ffmpeg_create_cmd, capture_output=True)
    if result.returncode == 0:
        print(f"✅ 测试视频已创建: {test_video}")
        print(f"   文件大小: {os.path.getsize(test_video)} 字节")
    else:
        print(f"❌ 创建测试视频失败")
        print(result.stderr.decode('utf-8', errors='ignore'))
        return False

    # 4. 烧录卡拉OK字幕
    print("\n[步骤4] 烧录卡拉OK字幕到视频...")
    tools = Tools()

    try:
        output_file = tools.burn_karaoke_subtitles(
            subs=karaoke_subs,
            media_file=test_video,
            output_filename='test_karaoke_output'
        )
        print(f"✅ 卡拉OK视频已生成: {output_file}")

        if os.path.exists(output_file):
            print(f"   文件大小: {os.path.getsize(output_file)} 字节")
        else:
            print(f"❌ 输出文件不存在!")
            return False

    except Exception as e:
        print(f"❌ 烧录失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 5. 提取视频截图
    print("\n[步骤5] 提取视频截图进行验证...")
    screenshot_file = "/tmp/karaoke_screenshot.png"

    # 提取第2秒的截图（应该显示第一行字幕）
    ffmpeg_screenshot_cmd = [
        '/usr/bin/ffmpeg',
        '-i', output_file,
        '-ss', '00:00:01.0',  # 第1秒
        '-vframes', '1',
        '-y',
        screenshot_file
    ]

    result = subprocess.run(ffmpeg_screenshot_cmd, capture_output=True)
    if result.returncode == 0:
        print(f"✅ 截图已保存: {screenshot_file}")
        print(f"   文件大小: {os.path.getsize(screenshot_file)} 字节")
    else:
        print(f"❌ 提取截图失败")
        return False

    # 6. 使用 OCR 检测截图中的文本（如果可用）
    print("\n[步骤6] 检查截图...")
    print("⚠️  请手动检查截图文件:")
    print(f"   {screenshot_file}")
    print("\n预期结果:")
    print("   ✅ 应该显示: 'Hello world this'")
    print("   ❌ 不应显示: 'k', 数字标签")

    # 7. 检查ASS文件内容
    print("\n[步骤7] 验证ASS字幕文件...")
    ass_file = "/tmp/verify_karaoke.ass"
    karaoke_subs.save(ass_file)

    with open(ass_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查 Dialogue 行
    dialogue_lines = [line for line in content.split('\n') if line.startswith('Dialogue:')]
    print(f"\n找到 {len(dialogue_lines)} 行对话:")
    for i, line in enumerate(dialogue_lines[:3], 1):
        # 提取文本部分
        parts = line.split(',', 9)
        if len(parts) >= 10:
            text = parts[9]
            print(f"\n对话 {i}:")
            print(f"  完整行: {line}")
            print(f"  文本部分: {text}")

            # 检查标签格式
            if '\\k' in text:
                print(f"  ✅ 包含正确的 \\k 标签")
            elif 'k' in text and '\\' not in text:
                print(f"  ❌ 警告: 包含 k 但缺少反斜杠!")

    print("\n" + "=" * 70)
    print("测试完成！")
    print("=" * 70)
    print("\n📂 生成的文件:")
    print(f"   测试视频: {test_video}")
    print(f"   卡拉OK视频: {output_file}")
    print(f"   截图: {screenshot_file}")
    print(f"   ASS文件: {ass_file}")

    print("\n📋 下一步验证:")
    print("   1. 在容器外查看截图:")
    print(f"      docker cp subsai-webui:{screenshot_file} .")
    print("   2. 播放视频检查:")
    print(f"      docker cp subsai-webui:{output_file} .")

    return True

if __name__ == '__main__':
    import sys
    success = test_full_karaoke_pipeline()
    sys.exit(0 if success else 1)
