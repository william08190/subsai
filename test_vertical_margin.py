#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试字幕垂直位置自定义功能

验证内容：
1. vertical_margin参数是否正确传递
2. 不同的vertical_margin值是否正确应用到ASS样式中
3. 默认值和自定义值是否都能正常工作
"""

import sys
sys.path.insert(0, '/subsai/src')

from pysubs2 import SSAFile, SSAEvent
from subsai.karaoke_generator import KaraokeGenerator
from subsai.karaoke_styles import get_style

def test_vertical_margin():
    """测试垂直边距自定义功能"""
    print("=" * 60)
    print("测试字幕垂直位置自定义功能")
    print("=" * 60)

    # 创建测试字幕
    test_subs = SSAFile()
    test_subs.append(SSAEvent(
        start=0,
        end=2000,
        text="{\\i1}Hello{\\i0} {\\i1}world{\\i0}"
    ))

    # 测试1: 使用默认垂直边距
    print("\n1. 测试默认垂直边距...")
    generator_default = KaraokeGenerator(style_name="classic")
    print(f"   - 默认marginv: {generator_default.style.get_vertical_margin()}")

    karaoke_default = generator_default.generate(test_subs)
    for style_name, style_obj in karaoke_default.styles.items():
        print(f"   - 样式 {style_name}: marginv = {style_obj.marginv}")

    # 测试2: 使用自定义垂直边距（更靠下）
    print("\n2. 测试自定义垂直边距 (marginv=30, 更靠下边)...")
    generator_custom = KaraokeGenerator(
        style_name="classic",
        vertical_margin=30
    )
    print(f"   - 自定义marginv: {generator_custom.style.get_vertical_margin()}")

    karaoke_custom = generator_custom.generate(test_subs)
    for style_name, style_obj in karaoke_custom.styles.items():
        print(f"   - 样式 {style_name}: marginv = {style_obj.marginv}")

    # 测试3: 测试所有5种样式的默认值
    print("\n3. 测试所有样式的默认垂直边距...")
    for style_name in ["classic", "modern", "neon", "elegant", "anime"]:
        style = get_style(style_name)
        print(f"   - {style_name.capitalize()}: 默认marginv = {style.get_default_vertical_margin()}")

    # 测试4: 验证ASS文件内容
    print("\n4. 验证ASS文件中的marginv值...")

    # 保存默认配置
    default_file = "/tmp/test_vertical_default.ass"
    karaoke_default.save(default_file)

    # 保存自定义配置
    custom_file = "/tmp/test_vertical_custom.ass"
    karaoke_custom.save(custom_file)

    print(f"   ✅ 默认配置文件: {default_file}")
    print(f"   ✅ 自定义配置文件: {custom_file}")

    # 读取并显示ASS样式行
    with open(default_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith("Style: Classic"):
                print(f"\n   默认样式行:")
                print(f"   {line.strip()}")
                # 提取marginv值（倒数第二个参数）
                parts = line.strip().split(',')
                marginv = parts[-2]
                print(f"   → MarginV = {marginv}")

    with open(custom_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith("Style: Classic"):
                print(f"\n   自定义样式行:")
                print(f"   {line.strip()}")
                # 提取marginv值（倒数第二个参数）
                parts = line.strip().split(',')
                marginv = parts[-2]
                print(f"   → MarginV = {marginv}")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n说明：")
    print("  - marginv 值越小，字幕越靠近底部边缘")
    print("  - marginv 值越大，字幕越远离底部边缘")
    print("  - Classic 样式默认 marginv=120")
    print("  - 建议范围：30-200 像素")

if __name__ == '__main__':
    test_vertical_margin()
