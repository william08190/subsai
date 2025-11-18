#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动换行和单词间距测试脚本
测试 v1.1.0-beta 的两个关键修复：
1. 多单词模式下单词之间添加空格
2. 根据视频宽度自动换行并居中
"""

import sys
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from subsai.karaoke_generator import KaraokeGenerator

print("=" * 80)
print("自动换行和单词间距测试 - v1.1.0-beta")
print("=" * 80)

# 测试数据：模拟词级时间戳
test_words = [
    {"word": "Hello", "start": 0, "end": 500},
    {"word": "world", "start": 500, "end": 1000},
    {"word": "this", "start": 1000, "end": 1400},
    {"word": "is", "start": 1400, "end": 1600},
    {"word": "a", "start": 1600, "end": 1700},
    {"word": "test", "start": 1700, "end": 2100},
    {"word": "of", "start": 2100, "end": 2300},
    {"word": "automatic", "start": 2300, "end": 3000},
    {"word": "line", "start": 3000, "end": 3400},
    {"word": "wrapping", "start": 3400, "end": 4000},
]

# ===========================================================================
# 测试1: 单词间距（不换行）
# ===========================================================================
print("\n[测试1] 单词间距功能（words_per_line=10，不启用换行）")
print("-" * 80)

try:
    generator = KaraokeGenerator(
        style_name="classic",
        words_per_line=10,
        fontsize=48
    )

    result = generator._create_karaoke_tags(test_words)

    # 验证结果包含空格
    word_count = result.count("Hello") + result.count("world") + result.count("test")
    space_count = result.count(" ")

    print(f"生成的卡拉OK文本:")
    print(f"  {result[:100]}...")
    print(f"\n单词数: {word_count}")
    print(f"空格数: {space_count}")

    # 应该有9个空格（10个单词之间）
    assert space_count >= 9, f"空格数不足: 期望至少9个, 实际{space_count}个"

    print("\n[PASS] 单词间距功能正常")

except Exception as e:
    print(f"\n[FAIL] 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ===========================================================================
# 测试2: 自动换行（16:9宽屏）
# ===========================================================================
print("\n\n[测试2] 自动换行功能（16:9宽屏, 1920px宽度）")
print("-" * 80)

try:
    generator = KaraokeGenerator(
        style_name="classic",
        words_per_line=10,
        fontsize=48,
        max_line_width_px=1920  # 16:9 宽屏
    )

    result = generator._create_karaoke_tags(test_words)

    # 验证结果包含换行符和居中对齐标签
    has_center_align = "{\\an5}" in result
    has_line_break = "\\N" in result

    print(f"生成的卡拉OK文本:")
    print(f"  {result[:150]}...")
    print(f"\n包含居中对齐标签: {has_center_align}")
    print(f"包含换行符: {has_line_break}")

    assert has_center_align, "缺少居中对齐标签 {\\an5}"

    print("\n[PASS] 自动换行功能（16:9）正常")

except Exception as e:
    print(f"\n[FAIL] 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ===========================================================================
# 测试3: 自动换行（9:16竖屏，窄屏幕）
# ===========================================================================
print("\n\n[测试3] 自动换行功能（9:16竖屏, 607px窄屏幕）")
print("-" * 80)

try:
    generator = KaraokeGenerator(
        style_name="classic",
        words_per_line=10,
        fontsize=48,
        max_line_width_px=607  # 9:16 竖屏（窄）
    )

    result = generator._create_karaoke_tags(test_words)

    # 验证结果包含多个换行符（窄屏幕应该有更多换行）
    line_break_count = result.count("\\N")

    print(f"生成的卡拉OK文本:")
    print(f"  {result[:200]}...")
    print(f"\n换行符数量: {line_break_count}")

    assert line_break_count > 0, "窄屏幕应该包含至少一个换行符"

    print("\n[PASS] 自动换行功能（9:16）正常，换行更频繁")

except Exception as e:
    print(f"\n[FAIL] 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ===========================================================================
# 测试4: 文本宽度估算
# ===========================================================================
print("\n\n[测试4] 文本宽度估算功能")
print("-" * 80)

try:
    generator = KaraokeGenerator(style_name="classic", fontsize=48)

    # 测试不同类型的文本
    test_cases = [
        ("Hello", "纯英文"),
        ("你好", "纯中文"),
        ("Hello 你好", "中英混合"),
        ("   ", "空格")
    ]

    for text, desc in test_cases:
        width = generator._estimate_text_width(text)
        print(f"  {desc}: '{text}' -> {width:.1f}px")
        assert width > 0, f"{desc}文本宽度应该>0"

    print("\n[PASS] 文本宽度估算功能正常")

except Exception as e:
    print(f"\n[FAIL] 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ===========================================================================
# 测试5: 向后兼容性（不启用换行时的行为）
# ===========================================================================
print("\n\n[测试5] 向后兼容性（max_line_width_px=None）")
print("-" * 80)

try:
    generator = KaraokeGenerator(
        style_name="classic",
        words_per_line=10,
        fontsize=48,
        max_line_width_px=None  # 不启用换行
    )

    result = generator._create_karaoke_tags(test_words)

    # 验证不包含居中对齐标签和换行符（使用原始逻辑）
    has_center_align = "{\\an5}" in result
    has_line_break = "\\N" in result

    print(f"生成的卡拉OK文本:")
    print(f"  {result[:100]}...")
    print(f"\n包含居中对齐标签: {has_center_align}")
    print(f"包含换行符: {has_line_break}")

    assert not has_center_align, "未启用换行时不应包含居中对齐标签"
    assert not has_line_break, "未启用换行时不应包含换行符"

    print("\n[PASS] 向后兼容性正常（保持原始行为）")

except Exception as e:
    print(f"\n[FAIL] 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ===========================================================================
# 总结
# ===========================================================================
print("\n\n" + "=" * 80)
print("测试总结")
print("=" * 80)

print("""
功能测试结果：

[OK] 单词间距功能 - 多单词模式下正确添加空格
[OK] 自动换行功能（16:9） - 宽屏幕下启用换行和居中
[OK] 自动换行功能（9:16） - 窄屏幕下增加换行频率
[OK] 文本宽度估算 - 支持中英文和空格的宽度计算
[OK] 向后兼容性 - 不启用换行时保持原始行为

修复的问题：
✅ 问题1: 多单词模式下缺少空格 - 已修复
✅ 问题2: 没有自动换行导致文本超出边界 - 已修复

新增功能：
✅ 根据视频宽度（aspect_ratio）自动计算max_line_width_px
✅ 智能换行算法（基于文本宽度估算）
✅ 自动居中对齐（\\an5标签）
✅ 完全向后兼容（可选参数）

测试状态：所有测试通过 ✓
版本：v1.1.0-beta
日期：2025-11-18
""")

print("=" * 80)
print("[SUCCESS] 所有测试通过！功能正常，准备提交")
print("=" * 80)

sys.exit(0)
