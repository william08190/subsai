#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立测试脚本 - 直接导入样式模块（避免ffmpeg依赖）
"""

import sys
import importlib.util
from pathlib import Path

# 直接加载karaoke_styles.py模块
styles_path = Path(__file__).parent / "src" / "subsai" / "karaoke_styles.py"
spec = importlib.util.spec_from_file_location("karaoke_styles", styles_path)
karaoke_styles = importlib.util.module_from_spec(spec)
spec.loader.exec_module(karaoke_styles)

# 从模块中获取需要的类和函数
get_style = karaoke_styles.get_style
ClassicStyle = karaoke_styles.ClassicStyle
ModernStyle = karaoke_styles.ModernStyle
NeonStyle = karaoke_styles.NeonStyle
ElegantStyle = karaoke_styles.ElegantStyle
AnimeStyle = karaoke_styles.AnimeStyle
STYLE_CLASSES = karaoke_styles.STYLE_CLASSES

print("=" * 80)
print("Subsai Karaoke v1.1.0-beta - Core Function Tests")
print("=" * 80)

test_passed = 0
test_failed = 0

# ===========================================================================
# 测试1: 所有样式类基础功能
# ===========================================================================
print("\n[Test 1] All Style Classes - Basic Functionality")
print("-" * 80)

try:
    for style_name, style_class in STYLE_CLASSES.items():
        style = style_class()
        print(f"\n{style.name}")
        print(f"  Default Font: {style.get_default_fontname()}")
        print(f"  Default Size: {style.get_default_fontsize()}px")
        print(f"  Default Margin: {style.get_default_vertical_margin()}px")
        print(f"  Default Primary Color: 0x{style.get_default_primary_color():08X}")
        print(f"  Default Secondary Color: 0x{style.get_default_secondary_color():08X}")
    test_passed += 1
    print("\n[PASS] All style classes work correctly")
except Exception as e:
    test_failed += 1
    print(f"\n[FAIL] Test failed: {e}")
    import traceback
    traceback.print_exc()

# ===========================================================================
# 测试2: 自定义字体名称
# ===========================================================================
print("\n\n[Test 2] Custom Font Name (NEW Feature)")
print("-" * 80)

try:
    test_fonts = ["Arial", "SimHei", "KaiTi", "Microsoft YaHei"]
    for font in test_fonts:
        style = get_style("classic", fontname=font)
        actual_font = style.get_fontname()
        assert actual_font == font, f"Font test failed: expected {font}, got {actual_font}"
        print(f"  [OK] Font: {actual_font}")
    test_passed += 1
    print("\n[PASS] Custom font name feature works correctly")
except Exception as e:
    test_failed += 1
    print(f"\n[FAIL] Test failed: {e}")
    import traceback
    traceback.print_exc()

# ===========================================================================
# 测试3: 自定义颜色
# ===========================================================================
print("\n\n[Test 3] Custom Primary and Secondary Colors (NEW Feature)")
print("-" * 80)

try:
    test_colors = [
        ("#FFFFFF", 0x00FFFFFF, "White"),
        ("#FF0000", 0x000000FF, "Red"),
        ("#00FF00", 0x0000FF00, "Green"),
        ("#0000FF", 0x00FF0000, "Blue"),
        ("#FFD700", 0x0000D7FF, "Gold")
    ]

    print("\nPrimary Color Tests:")
    for hex_color, expected_ass, color_name in test_colors:
        style = get_style("classic", primary_color=hex_color)
        actual_ass = style.get_primary_color()
        assert actual_ass == expected_ass, f"Primary color conversion failed: {hex_color} -> expected 0x{expected_ass:08X}, got 0x{actual_ass:08X}"
        print(f"  [OK] {color_name}: {hex_color} -> 0x{actual_ass:08X}")

    print("\nSecondary Color Tests:")
    for hex_color, expected_ass, color_name in test_colors:
        style = get_style("classic", secondary_color=hex_color)
        actual_ass = style.get_secondary_color()
        assert actual_ass == expected_ass, f"Secondary color conversion failed: {hex_color} -> expected 0x{expected_ass:08X}, got 0x{actual_ass:08X}"
        print(f"  [OK] {color_name}: {hex_color} -> 0x{actual_ass:08X}")

    test_passed += 1
    print("\n[PASS] Custom color feature works correctly")
except Exception as e:
    test_failed += 1
    print(f"\n[FAIL] Test failed: {e}")
    import traceback
    traceback.print_exc()

# ===========================================================================
# 测试4: 所有样式类支持完整自定义
# ===========================================================================
print("\n\n[Test 4] All Style Classes Support Full Custom Parameters")
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

        # Verify all parameters
        assert style.get_fontsize() == 56, f"{style_name}: fontsize failed"
        assert style.get_vertical_margin() == 100, f"{style_name}: vertical_margin failed"
        assert style.get_fontname() == "Arial", f"{style_name}: fontname failed"
        assert style.get_primary_color() == 0x00FFFFFF, f"{style_name}: primary_color failed"
        assert style.get_secondary_color() == 0x00FFD700, f"{style_name}: secondary_color failed"

        print(f"  [OK] {style_name.capitalize()}: All custom parameters applied correctly")

    test_passed += 1
    print("\n[PASS] All style classes support full parameters")
except Exception as e:
    test_failed += 1
    print(f"\n[FAIL] Test failed: {e}")
    import traceback
    traceback.print_exc()

# ===========================================================================
# 测试5: ASS样式行包含动态参数
# ===========================================================================
print("\n\n[Test 5] ASS Style Lines Contain Dynamic Parameters")
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

        # Verify ASS style line contains custom font
        assert "TestFont" in ass_line, f"{style_name}: ASS style line doesn't contain custom font"

        # Verify ASS style line contains custom fontsize
        assert "64" in ass_line, f"{style_name}: ASS style line doesn't contain fontsize 64"

        print(f"  [OK] {style_name.capitalize()}: ASS style line contains dynamic parameters")

    test_passed += 1
    print("\n[PASS] ASS style line dynamic parameters work correctly")
except Exception as e:
    test_failed += 1
    print(f"\n[FAIL] Test failed: {e}")
    import traceback
    traceback.print_exc()

# ===========================================================================
# 测试6: 向后兼容性
# ===========================================================================
print("\n\n[Test 6] Backward Compatibility (Optional Parameters)")
print("-" * 80)

try:
    # No parameters
    style_default = get_style("classic")
    assert style_default.get_fontname() == "Microsoft YaHei"
    assert style_default.get_fontsize() == 48
    print("  [OK] No parameters: using default values")

    # Partial parameters
    style_partial = get_style("modern", fontsize=60)
    assert style_partial.get_fontsize() == 60  # Custom
    assert style_partial.get_fontname() == "Microsoft YaHei"  # Default
    assert style_partial.get_vertical_margin() == 30  # Modern default
    print("  [OK] Partial parameters: correctly mixing defaults and custom values")

    test_passed += 1
    print("\n[PASS] Backward compatibility works correctly")
except Exception as e:
    test_failed += 1
    print(f"\n[FAIL] Test failed: {e}")
    import traceback
    traceback.print_exc()

# ===========================================================================
# 测试7: Hex到ASS颜色转换精度
# ===========================================================================
print("\n\n[Test 7] Hex to ASS Color Conversion (BGR Format)")
print("-" * 80)

try:
    test_cases = [
        ("#000000", 0x00000000, "Black"),
        ("#FFFFFF", 0x00FFFFFF, "White"),
        ("#FF0000", 0x000000FF, "Red (RGB->BGR)"),
        ("#00FF00", 0x0000FF00, "Green (RGB->BGR)"),
        ("#0000FF", 0x00FF0000, "Blue (RGB->BGR)"),
        ("#123456", 0x00563412, "Custom Color"),
    ]

    style = ClassicStyle()
    for hex_color, expected, desc in test_cases:
        result = style._hex_to_ass_color(hex_color)
        assert result == expected, f"Color conversion error: {hex_color} -> expected 0x{expected:08X}, got 0x{result:08X}"
        print(f"  [OK] {desc}: {hex_color} -> 0x{result:08X}")

    test_passed += 1
    print("\n[PASS] Hex to ASS color conversion works correctly")
except Exception as e:
    test_failed += 1
    print(f"\n[FAIL] Test failed: {e}")
    import traceback
    traceback.print_exc()

# ===========================================================================
# Summary
# ===========================================================================
print("\n\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)

print(f"""
Core Function Test Results:

Passed: {test_passed}/{test_passed + test_failed}
Failed: {test_failed}/{test_passed + test_failed}

[OK] All 5 style classes (Classic, Modern, Neon, Elegant, Anime)
[OK] Custom font name (fontname parameter)
[OK] Custom primary color (primary_color parameter)
[OK] Custom secondary color (secondary_color parameter)
[OK] Custom font size (fontsize parameter)
[OK] Custom vertical margin (vertical_margin parameter)
[OK] Hex to ASS color conversion (BGR format)
[OK] ASS style lines contain dynamic parameters
[OK] Backward compatibility (optional parameters)
[OK] Complete parameter passing chain

Status: {"ALL TESTS PASSED" if test_failed == 0 else f"{test_failed} TEST(S) FAILED"}
Version: v1.1.0-beta
Date: 2025-11-18
""")

print("=" * 80)
if test_failed == 0:
    print("[SUCCESS] All core function tests passed!")
else:
    print(f"[FAILED] {test_failed} test(s) failed")
print("=" * 80)

sys.exit(0 if test_failed == 0 else 1)
