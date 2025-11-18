#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试卡拉OK样式和效果修复

验证内容：
1. 样式名称正确匹配 (Classic 而不是 Default)
2. 卡拉OK标签使用 \kf (填充效果)
3. SecondaryColour 正确设置 (黄色高亮)
"""

import sys
sys.path.insert(0, '/subsai/src')

from pysubs2 import SSAFile, SSAEvent
from subsai.karaoke_generator import KaraokeGenerator
from subsai.karaoke_styles import get_style

def test_style_fix():
    """测试样式修复"""
    print("=" * 60)
    print("测试卡拉OK样式和效果修复")
    print("=" * 60)

    # 1. 创建测试字幕
    test_subs = SSAFile()
    test_subs.append(SSAEvent(
        start=0,
        end=2000,
        text="{\\i1}Hello{\\i0} world test"
    ))

    print("\n1. 创建Classic样式生成器...")
    generator = KaraokeGenerator(
        style_name="classic",
        words_per_line=5,
        fontsize=36
    )

    # 检查样式属性
    print(f"   - 样式名称: {generator.style.name}")
    print(f"   - 样式key: {generator.style.style_key}")
    print(f"   - 字体大小: {generator.style.get_fontsize()}")

    # 2. 测试卡拉OK标签格式
    print("\n2. 测试卡拉OK标签格式...")
    karaoke_tag = generator.style.get_karaoke_tags(50)
    print(f"   - 生成的标签: {karaoke_tag}")

    if "{\\kf50}" in karaoke_tag:
        print("   ✅ 卡拉OK标签格式正确 (使用 \\kf 填充效果)")
    else:
        print(f"   ❌ 卡拉OK标签格式错误: {karaoke_tag}")

    # 3. 生成卡拉OK字幕
    print("\n3. 生成卡拉OK字幕...")
    karaoke_subs = generator.generate(test_subs)

    # 检查样式
    print(f"   - 样式数量: {len(karaoke_subs.styles)}")
    for style_name, style_obj in karaoke_subs.styles.items():
        print(f"   - 样式名称: {style_name}")
        print(f"   - 字体大小: {style_obj.fontsize}")
        print(f"   - 主色 (PrimaryColour): 0x{style_obj.primarycolor:08X}")
        print(f"   - 次色 (SecondaryColour): 0x{style_obj.secondarycolor:08X}")

        # 验证样式名称
        if style_name == "Classic":
            print("   ✅ 样式名称正确 (Classic)")
        else:
            print(f"   ❌ 样式名称错误: {style_name} (应该是 Classic)")

        # 验证黄色高亮 (0x0000FFFF)
        if style_obj.secondarycolor == 0x0000FFFF:
            print("   ✅ 次色正确 (黄色 0x0000FFFF)")
        else:
            print(f"   ❌ 次色错误: 0x{style_obj.secondarycolor:08X}")

    # 4. 检查事件内容
    print("\n4. 检查事件内容...")
    for i, event in enumerate(karaoke_subs):
        print(f"   事件{i+1}: {event.text[:50]}...")
        if "{\\kf" in event.text:
            print(f"   ✅ 包含 \\kf 标签")
        else:
            print(f"   ❌ 没有 \\kf 标签")

        if event.style == "Classic":
            print(f"   ✅ 事件样式正确: {event.style}")
        else:
            print(f"   ❌ 事件样式错误: {event.style}")

    # 5. 保存测试文件
    test_file = "/tmp/test_karaoke_style_fix.ass"
    karaoke_subs.save(test_file)
    print(f"\n5. 测试文件已保存: {test_file}")

    # 读取并显示ASS文件头部
    with open(test_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()[:25]
        print("\nASS文件头部内容:")
        print("---")
        for line in lines:
            print(line.rstrip())
        print("---")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == '__main__':
    test_style_fix()
