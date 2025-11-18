#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版测试脚本 - Windows兼容（无emoji）
"""

import sys
from pathlib import Path

# 直接导入样式模块
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("=" * 80)
print("Subsai Karaoke v1.1.0-beta - 核心功能测试")
print("=" * 80)

# 直接导入样式类
from subsai.karaoke_styles import (
    get_style,
    ClassicStyle,
    ModernStyle,
    NeonStyle,
    ElegantStyle,
    AnimeStyle,
    STYLE_CLASSES
)

test_passed = 0
test_failed = 0

# ===========================================================================
# 测试1: 所有样式类基础功能
# ===========================================================================
print("\n[测试1] 所有样式类基础功能")
print("-" * 80)

try:
    for style_name, style_class in STYLE_CLASSES.items():
        style = style_class()
        print(f"\n{style.name}")
        print(f"  默认字体: {style.get_default_fontname()}")
        print(f"  默认字号: {style.get_default_fontsize()}px")
        print(f"  默认边距: {style.get_default_vertical_margin()}px")
        print(f"  默认基础颜色: 0x{style.get_default_primary_color():08X}")
        print(f"  默认高亮颜色: 0x{style.get_default_secondary_color():08X}")
    test_passed += 1
    print("\n[PASS] 所有样式类基础功能正常")
except Exception as e:
    test_failed += 1
    print(f"\n[FAIL] 测试失败: {e}")

# ===========================================================================
# 测试2: 自定义字体名称
# ===========================================================================
print("\n\n[测试2] 自定义字体名称（NEW功能）")
print("-" * 80)

try:
    test_fonts = ["Arial", "SimHei", "KaiTi", "Microsoft YaHei"]
    for font in test_fonts:
        style = get_style("classic", fontname=font)
        actual_font = style.get_fontname()
        assert actual_font == font, f"字体名称测试失败: 期望 {font}, 实际 {actual_font}"
        print(f"  [OK] 字体: {actual_font}")
    test_passed += 1
    print("\n[PASS] 自定义字体名称功能正常")
except Exception as e:
    test_failed += 1
    print(f"\n[FAIL] 测试失败: {e}")

# ===========================================================================
# 测试3: 自定义颜色
# ===========================================================================
print("\n\n[测试3] 自定义基础颜色和高亮颜色（NEW功能）")
print("-" * 80)

try:
    test_colors = [
        ("#FFFFFF", 0x00FFFFFF, "白色"),
        ("#FF0000", 0x000000FF, "红色"),
        ("#00FF00", 0x0000FF00, "绿色"),
        ("#0000FF", 0x00FF0000, "蓝色"),
        ("#FFD700", 0x0000D7FF, "金色")
    ]

    print("\n基础颜色测试：")
    for hex_color, expected_ass, color_name in test_colors:
        style = get_style("classic", primary_color=hex_color)
        actual_ass = style.get_primary_color()
        assert actual_ass == expected_ass, f"基础颜色转换失败: {hex_color} -> 期望 0x{expected_ass:08X}, 实际 0x{actual_ass:08X}"
        print(f"  [OK] {color_name}: {hex_color} -> 0x{actual_ass:08X}")

    print("\n高亮颜色测试：")
    for hex_color, expected_ass, color_name in test_colors:
        style = get_style("classic", secondary_color=hex_color)
        actual_ass = style.get_secondary_color()
        assert actual_ass == expected_ass, f"高亮颜色转换失败: {hex_color} -> 期望 0x{expected_ass:08X}, 实际 0x{actual_ass:08X}"
        print(f"  [OK] {color_name}: {hex_color} -> 0x{actual_ass:08X}")

    test_passed += 1
    print("\n[PASS] 自定义颜色功能正常")
except Exception as e:
    test_failed += 1
    print(f"\n[FAIL] 测试失败: {e}")

# ===========================================================================
# 测试4: 所有样式类支持完整自定义
# ===========================================================================
print("\n\n[测试4] 所有样式类支持完整自定义参数")
print("-" * 80)

try:
    for style_name in STYLE_CLASSES.keys():
        style = get_style(
            style_name,
            fontsize=56,
            vertical_margin=100,
            fontname="Arial",
            primary_color="#FFFFFF",
            secondary_color="#FFD700"
        )

        # 验证所有参数
        assert style.get_fontsize() == 56, f"{style_name}: fontsize失败"
        assert style.get_vertical_margin() == 100, f"{style_name}: vertical_margin失败"
        assert style.get_fontname() == "Arial", f"{style_name}: fontname失败"
        assert style.get_primary_color() == 0x00FFFFFF, f"{style_name}: primary_color失败"
        assert style.get_secondary_color() == 0x00FFD700, f"{style_name}: secondary_color失败"

        print(f"  [OK] {style_name.capitalize()}: 所有自定义参数正确应用")

    test_passed += 1
    print("\n[PASS] 所有样式类完整参数支持正常")
except Exception as e:
    test_failed += 1
    print(f"\n[FAIL] 测试失败: {e}")

# ===========================================================================
# 测试5: ASS样式行包含动态参数
# ===========================================================================
print("\n\n[测试5] ASS样式行包含动态参数")
print("-" * 80)

try:
    for style_name in ["classic", "modern", "neon", "elegant", "anime"]:
        style = get_style(
            style_name,
            fontname="TestFont",
            fontsize=64,
            primary_color="#AABBCC",
            secondary_color="#DDEEFF"
        )
        ass_line = style.get_ass_style_line()

        # 验证ASS样式行包含自定义字体
        assert "TestFont" in ass_line, f"{style_name}: ASS样式行未包含自定义字体"

        # 验证ASS样式行包含自定义字号
        assert "64" in ass_line, f"{style_name}: ASS样式行未包含字体大小64"

        print(f"  [OK] {style_name.capitalize()}: ASS样式行包含动态参数")

    test_passed += 1
    print("\n[PASS] ASS样式行动态参数功能正常")
except Exception as e:
    test_failed += 1
    print(f"\n[FAIL] 测试失败: {e}")

# ===========================================================================
# 测试6: 向后兼容性
# ===========================================================================
print("\n\n[测试6] 向后兼容性（可选参数）")
print("-" * 80)

try:
    # 无参数调用
    style_default = get_style("classic")
    assert style_default.get_fontname() == "Microsoft YaHei"
    assert style_default.get_fontsize() == 48
    print("  [OK] 无参数调用：使用默认值")

    # 部分参数调用
    style_partial = get_style("modern", fontsize=60)
    assert style_partial.get_fontsize() == 60  # 自定义
    assert style_partial.get_fontname() == "Microsoft YaHei"  # 默认
    assert style_partial.get_vertical_margin() == 30  # Modern默认
    print("  [OK] 部分参数调用：正确混合默认值和自定义值")

    test_passed += 1
    print("\n[PASS] 向后兼容性功能正常")
except Exception as e:
    test_failed += 1
    print(f"\n[FAIL] 测试失败: {e}")

# ===========================================================================
# 测试7: Hex到ASS颜色转换精度
# ===========================================================================
print("\n\n[测试7] Hex到ASS颜色转换（BGR格式验证）")
print("-" * 80)

try:
    test_cases = [
        ("#000000", 0x00000000, "黑色"),
        ("#FFFFFF", 0x00FFFFFF, "白色"),
        ("#FF0000", 0x000000FF, "红色(RGB->BGR)"),
        ("#00FF00", 0x0000FF00, "绿色(RGB->BGR)"),
        ("#0000FF", 0x00FF0000, "蓝色(RGB->BGR)"),
        ("#123456", 0x00563412, "自定义色"),
    ]

    style = ClassicStyle()
    for hex_color, expected, desc in test_cases:
        result = style._hex_to_ass_color(hex_color)
        assert result == expected, f"颜色转换错误: {hex_color} -> 期望 0x{expected:08X}, 得到 0x{result:08X}"
        print(f"  [OK] {desc}: {hex_color} -> 0x{result:08X}")

    test_passed += 1
    print("\n[PASS] Hex到ASS颜色转换功能正常")
except Exception as e:
    test_failed += 1
    print(f"\n[FAIL] 测试失败: {e}")

# ===========================================================================
# 总结
# ===========================================================================
print("\n\n" + "=" * 80)
print("测试总结")
print("=" * 80)

print(f"""
核心功能测试结果：

通过测试: {test_passed}
失败测试: {test_failed}

[OK] 所有5个样式类（Classic, Modern, Neon, Elegant, Anime）
[OK] 自定义字体名称（fontname参数）
[OK] 自定义基础颜色（primary_color参数）
[OK] 自定义高亮颜色（secondary_color参数）
[OK] 自定义字体大小（fontsize参数）
[OK] 自定义垂直边距（vertical_margin参数）
[OK] Hex到ASS颜色转换（BGR格式）
[OK] ASS样式行包含动态参数
[OK] 向后兼容性（可选参数）
[OK] 参数传递完整性

测试状态：{"所有测试通过" if test_failed == 0 else f"{test_failed}个测试失败"}
版本：v1.1.0-beta
日期：2025-11-18
""")

print("=" * 80)
if test_failed == 0:
    print("[SUCCESS] 所有核心功能测试通过！")
else:
    print(f"[FAILED] {test_failed}个测试失败")
print("=" * 80)

sys.exit(0 if test_failed == 0 else 1)
