#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
调试卡拉OK标签显示问题
"""

from pysubs2 import SSAFile, SSAEvent
from subsai.karaoke_generator import create_karaoke_subtitles

def debug_karaoke_tags():
    """调试卡拉OK标签在ASS文件中的表现"""

    print("=" * 60)
    print("调试卡拉OK标签问题")
    print("=" * 60)

    # 创建简单测试字幕
    test_subs = SSAFile()
    test_subs.append(SSAEvent(start=0, end=3000, text="Hello world"))

    # 生成卡拉OK字幕
    karaoke_subs = create_karaoke_subtitles(
        subs=test_subs,
        style_name="classic",
        words_per_line=5,
        fontsize=36
    )

    print(f"\n生成了 {len(karaoke_subs)} 个卡拉OK事件")

    # 检查事件内容
    for i, event in enumerate(karaoke_subs):
        print(f"\n事件 {i+1}:")
        print(f"  时间: {event.start}ms - {event.end}ms")
        print(f"  文本: {event.text}")
        print(f"  文本repr: {repr(event.text)}")
        print(f"  文本长度: {len(event.text)}")

    # 保存到文件
    output_file = "/tmp/debug_karaoke.ass"
    karaoke_subs.save(output_file)
    print(f"\n已保存到: {output_file}")

    # 读取文件内容检查
    print("\n" + "=" * 60)
    print("检查ASS文件内容:")
    print("=" * 60)

    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 查找Events部分
    events_section = content.split("[Events]")[-1]

    # 找到Dialogue行
    for line in events_section.split('\n'):
        if line.startswith('Dialogue:'):
            print(f"\n对话行:")
            print(f"  {line}")

            # 检查是否包含 \k 标签
            if '\\k' in line:
                print(f"  ✅ 包含 \\k 标签")
            elif 'k' in line and '\\' not in line:
                print(f"  ❌ 包含 k 但缺少反斜杠!")
                print(f"  问题：ASS标签没有反斜杠，���被当作普通文本显示")

            # 提取文本部分（最后一个逗号后的内容）
            text_part = line.split(',', 9)[-1] if ',' in line else line
            print(f"  文本部分: {text_part}")
            print(f"  文本repr: {repr(text_part)}")

    print("\n" + "=" * 60)
    print("诊断完成")
    print("=" * 60)

    return output_file

if __name__ == '__main__':
    debug_karaoke_tags()
