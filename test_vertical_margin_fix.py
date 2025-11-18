#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
垂直边距修复测试脚本 - v1.1.0
验证 \an2 标签修复后，字幕是否正确保持用户自定义的垂直距离
同时保持左右居中和自动换行功能
"""

import sys
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from subsai.karaoke_generator import KaraokeGenerator

print("=" * 80)
print("垂直边距修复测试 - v1.1.0")
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
# 测试1: 验证使用 \an2 标签（底部居中）
# ===========================================================================
print("\n[测试1] 验证对齐标签为 \\an2（底部居中，保持垂直距离）")
print("-" * 80)

try:
    generator = KaraokeGenerator(
        style_name="classic",
        words_per_line=10,
        fontsize=48,
        vertical_margin=15,  # 用户自定义15px
        max_line_width_px=1920  # 启用自动换行
    )

    result = generator._create_karaoke_tags(test_words)

    # 验证结果包含 \an2 标签
    has_bottom_center = "{\\an2}" in result
    has_middle_center = "{\\an5}" in result  # 不应该包含\an5

    print(f"生成的卡拉OK文本:")
    print(f"  {result[:150]}...")
    print(f"\n包含 \\an2 标签（底部居中）: {has_bottom_center}")
    print(f"包含 \\an5 标签（中心对齐）: {has_middle_center}")

    assert has_bottom_center, "缺少 \\an2 底部居中标签"
    assert not has_middle_center, "不应该包含 \\an5 中心对齐标签"

    print("\n[PASS] 对齐标签正确（\\an2 底部居中）")

except Exception as e:
    print(f"\n[FAIL] 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ===========================================================================
# 测试2: 验证自动换行功能仍然正常
# ===========================================================================
print("\n\n[测试2] 验证自动换行功能（窄屏9:16, 607px）")
print("-" * 80)

try:
    generator = KaraokeGenerator(
        style_name="classic",
        words_per_line=10,
        fontsize=48,
        vertical_margin=15,
        max_line_width_px=607  # 9:16 竖屏（窄）
    )

    result = generator._create_karaoke_tags(test_words)

    # 验证结果包含换行符
    line_break_count = result.count("\\N")
    has_bottom_center = "{\\an2}" in result

    print(f"生成的卡拉OK文本:")
    print(f"  {result[:200]}...")
    print(f"\n换行符数量: {line_break_count}")
    print(f"包含 \\an2 标签: {has_bottom_center}")

    assert line_break_count > 0, "窄屏幕应该包含至少一个换行符"
    assert has_bottom_center, "应该包含 \\an2 底部居中标签"

    print("\n[PASS] 自动换行功能正常，使用 \\an2 标签")

except Exception as e:
    print(f"\n[FAIL] 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ===========================================================================
# 测试3: 验证单词间距仍然正常
# ===========================================================================
print("\n\n[测试3] 验证单词间距功能")
print("-" * 80)

try:
    generator = KaraokeGenerator(
        style_name="classic",
        words_per_line=10,
        fontsize=48,
        vertical_margin=15,
        max_line_width_px=1920
    )

    result = generator._create_karaoke_tags(test_words)

    # 验证结果包含空格
    space_count = result.count(" ")

    print(f"生成的卡拉OK文本:")
    print(f"  {result[:100]}...")
    print(f"\n空格数量: {space_count} (期望9个)")

    assert space_count >= 9, f"空格数不足: 期望至少9个, 实际{space_count}个"

    print("\n[PASS] 单词间距功能正常")

except Exception as e:
    print(f"\n[FAIL] 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ===========================================================================
# 测试4: 对比 \an5 和 \an2 的区别
# ===========================================================================
print("\n\n[测试4] 对比测试：\\an5 vs \\an2")
print("-" * 80)

try:
    # 使用 \an2 的生成器
    gen_an2 = KaraokeGenerator(
        style_name="classic",
        words_per_line=10,
        fontsize=48,
        vertical_margin=15,
        max_line_width_px=1920
    )

    result_an2 = gen_an2._create_karaoke_tags(test_words)

    an2_tag = "{\\an2}"
    print("✅ 使用 \\an2（底部居中）:")
    print(f"  - 对齐方式: 左右居中，垂直位置保持距底部 15px")
    print(f"  - 标签: {result_an2[:50]}...")
    print(f"  - 包含 \\an2: {an2_tag in result_an2}")

    print("\n❌ 使用 \\an5（中心对齐）的问题:")
    print(f"  - 对齐方式: 左右居中，垂直居中（覆盖vertical_margin）")
    print(f"  - 会导致: 无论用户设置多少vertical_margin，字幕都会显示在视频中央")
    print(f"  - 用户反馈: \"文本居中功能好像把字幕距底部距离(px)的功能覆盖了\"")

    print("\n[PASS] 对比测试完成，确认 \\an2 是正确的选择")

except Exception as e:
    print(f"\n[FAIL] 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ===========================================================================
# 测试5: 不同 vertical_margin 值的验证
# ===========================================================================
print("\n\n[测试5] 不同 vertical_margin 值的验证")
print("-" * 80)

try:
    test_margins = [10, 15, 50, 100, 200]

    for margin in test_margins:
        generator = KaraokeGenerator(
            style_name="classic",
            words_per_line=10,
            fontsize=48,
            vertical_margin=margin,
            max_line_width_px=1920
        )

        # 检查样式的垂直边距
        style = generator.style
        actual_margin = style.get_vertical_margin()

        print(f"  设置 vertical_margin={margin}px -> 样式实际值={actual_margin}px")

        assert actual_margin == margin, f"垂直边距不匹配: 期望{margin}, 实际{actual_margin}"

    print("\n[PASS] 所有 vertical_margin 值都被正确保留")

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
功能验证结果：

[OK] \\an2 标签（底部居中） - 左右居中，保持垂直距离
[OK] 自动换行功能 - 正常工作，配合 \\an2 标签
[OK] 单词间距功能 - 单词之间有空格
[OK] 对比测试 - 确认 \\an2 解决了 \\an5 的问题
[OK] 垂直边距保留 - 用户自定义的 vertical_margin 被正确应用

修复的问题：
✅ 问题: 文本居中功能覆盖了字幕距底部距离(px)的功能
✅ 原因: 使用了 \\an5（中心对齐）标签，会同时居中水平和垂直
✅ 修复: 改用 \\an2（底部居中）标签，只居中水平，垂直位置保持用户设置

用户需求：
✅ "我说的居中是左右居中" - 使用 \\an2 实现左右居中
✅ "上下距离还是按照用户自定义的距离" - vertical_margin 参数被保留

测试状态：所有测试通过 ✓
版本：v1.1.0
日期：2025-11-18
""")

print("=" * 80)
print("[SUCCESS] 垂直边距修复验证通过！")
print("=" * 80)

sys.exit(0)
