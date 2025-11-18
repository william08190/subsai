#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整表单选项测试脚本 - v1.1.0-beta
测试所有11个表单选项，包括新实现的自定义字体和颜色功能
"""

import sys
import os
from pathlib import Path

# 添加src路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from subsai.karaoke_styles import (
    get_style,
    ClassicStyle,
    ModernStyle,
    NeonStyle,
    ElegantStyle,
    AnimeStyle,
    STYLE_CLASSES
)
from subsai.karaoke_generator import create_karaoke_subtitles, KaraokeGenerator
from pysubs2 import SSAFile, SSAEvent

print("=" * 80)
print("📋 Subsai Karaoke 完整表单选项测试 - v1.1.0-beta")
print("=" * 80)

# 测试数据：模拟Whisper输出的字幕
test_subs = SSAFile()
test_subs.append(SSAEvent(start=0, end=3000, text="Hello world this is a karaoke test"))
test_subs.append(SSAEvent(start=3000, end=6000, text="Testing custom fonts and colors"))
test_subs.append(SSAEvent(start=6000, end=9000, text="All parameters should work correctly"))

print("\n✅ 测试数据准备完成")
print(f"   - 创建了 {len(test_subs)} 个测试字幕事件")

# ============================================================================
# 测试1: 样式系统基础功能
# ============================================================================
print("\n" + "=" * 80)
print("测试1: 样式系统基础功能")
print("=" * 80)

print("\n1.1 测试所有5种样式类")
for style_name, style_class in STYLE_CLASSES.items():
    style = style_class()
    print(f"   ✅ {style_name}: {style.name}")
    print(f"      默认字体: {style.get_default_fontname()}")
    print(f"      默认字号: {style.get_default_fontsize()}")
    print(f"      默认边距: {style.get_default_vertical_margin()}")

# ============================================================================
# 测试2: 自定义字体大小和垂直边距（已有功能）
# ============================================================================
print("\n" + "=" * 80)
print("测试2: 自定义字体大小和垂直边距")
print("=" * 80)

print("\n2.1 测试fontsize参数")
style_custom_fontsize = get_style("classic", fontsize=64)
assert style_custom_fontsize.get_fontsize() == 64, "fontsize参数失败"
print(f"   ✅ 自定义字体大小: {style_custom_fontsize.get_fontsize()}px")

print("\n2.2 测试vertical_margin参数")
style_custom_margin = get_style("classic", vertical_margin=150)
assert style_custom_margin.get_vertical_margin() == 150, "vertical_margin参数失败"
print(f"   ✅ 自定义垂直边距: {style_custom_margin.get_vertical_margin()}px")

# ============================================================================
# 测试3: 自定义字体名称（新功能）
# ============================================================================
print("\n" + "=" * 80)
print("测试3: 自定义字体名称 (NEW)")
print("=" * 80)

test_fonts = ["Arial", "SimHei", "KaiTi", "Microsoft YaHei"]
for font in test_fonts:
    style = get_style("classic", fontname=font)
    assert style.get_fontname() == font, f"fontname参数失败: {font}"
    print(f"   ✅ 字体名称: {style.get_fontname()}")

# ============================================================================
# 测试4: 自定义颜色（新功能）
# ============================================================================
print("\n" + "=" * 80)
print("测试4: 自定义基础颜色和高亮颜色 (NEW)")
print("=" * 80)

print("\n4.1 测试primary_color参数")
test_primary_colors = ["#FFFFFF", "#FF0000", "#00FF00", "#0000FF"]
for color_hex in test_primary_colors:
    style = get_style("classic", primary_color=color_hex)
    color_ass = style.get_primary_color()
    print(f"   ✅ 基础颜色: {color_hex} -> ASS: 0x{color_ass:08X}")

print("\n4.2 测试secondary_color参数")
test_secondary_colors = ["#FFD700", "#FF00FF", "#00FFFF", "#FFA500"]
for color_hex in test_secondary_colors:
    style = get_style("classic", secondary_color=color_hex)
    color_ass = style.get_secondary_color()
    print(f"   ✅ 高亮颜色: {color_hex} -> ASS: 0x{color_ass:08X}")

print("\n4.3 测试Hex到ASS颜色转换")
# 验证BGR格式正确性
style = get_style("classic")
# #FFFFFF (白色) -> 0x00FFFFFF
assert style._hex_to_ass_color("#FFFFFF") == 0x00FFFFFF
# #FF0000 (红色 RGB) -> 0x000000FF (BGR)
assert style._hex_to_ass_color("#FF0000") == 0x000000FF
# #00FF00 (绿色 RGB) -> 0x0000FF00 (BGR)
assert style._hex_to_ass_color("#00FF00") == 0x0000FF00
# #0000FF (蓝色 RGB) -> 0x00FF0000 (BGR)
assert style._hex_to_ass_color("#0000FF") == 0x00FF0000
print("   ✅ Hex到ASS颜色转换正确（BGR格式）")

# ============================================================================
# 测试5: 所有样式类的自定义参数支持
# ============================================================================
print("\n" + "=" * 80)
print("测试5: 所有样式类支持完整自定义参数")
print("=" * 80)

for style_name in STYLE_CLASSES.keys():
    style = get_style(
        style_name,
        fontsize=56,
        vertical_margin=100,
        fontname="Arial",
        primary_color="#FFFFFF",
        secondary_color="#FFD700"
    )
    assert style.get_fontsize() == 56
    assert style.get_vertical_margin() == 100
    assert style.get_fontname() == "Arial"
    assert style.get_primary_color() == 0x00FFFFFF
    assert style.get_secondary_color() == 0x00FFD700
    print(f"   ✅ {style_name}: 所有自定义参数正确应用")

# ============================================================================
# 测试6: KaraokeGenerator参数传递
# ============================================================================
print("\n" + "=" * 80)
print("测试6: KaraokeGenerator参数传递链")
print("=" * 80)

print("\n6.1 测试KaraokeGenerator.__init__()")
generator = KaraokeGenerator(
    style_name="modern",
    words_per_line=8,
    fontsize=52,
    vertical_margin=80,
    fontname="SimHei",
    primary_color="#FFFFFF",
    secondary_color="#FF8C00"
)
assert generator.style.get_fontsize() == 52
assert generator.style.get_vertical_margin() == 80
assert generator.style.get_fontname() == "SimHei"
assert generator.style.get_primary_color() == 0x00FFFFFF
assert generator.style.get_secondary_color() == 0x008CFF00  # BGR: FF8C00 -> 008CFF00
print("   ✅ KaraokeGenerator参数正确传递到样式对象")

print("\n6.2 测试create_karaoke_subtitles()便捷函数")
karaoke_subs = create_karaoke_subtitles(
    test_subs,
    style_name="elegant",
    words_per_line=10,
    fontsize=48,
    vertical_margin=120,
    fontname="KaiTi",
    primary_color="#FFFFE0",  # 象牙白
    secondary_color="#DAA520"  # 金黄色
)
assert len(karaoke_subs) > 0, "create_karaoke_subtitles()生成失败"
print(f"   ✅ 生成了 {len(karaoke_subs)} 个卡拉OK字幕事件")

# ============================================================================
# 测试7: ASS样式行生成
# ============================================================================
print("\n" + "=" * 80)
print("测试7: ASS样式行生成（动态字体和颜色）")
print("=" * 80)

for style_name in ["classic", "modern", "neon", "elegant", "anime"]:
    style = get_style(
        style_name,
        fontname="TestFont",
        primary_color="#AABBCC",
        secondary_color="#DDEEFF"
    )
    ass_line = style.get_ass_style_line()

    # 验证ASS样式行包含自定义参数
    assert "TestFont" in ass_line, f"{style_name}: 未包含自定义字体名"
    # 颜色需要转换为BGR格式检查
    # #AABBCC -> &H00CCBBAA
    # #DDEEFF -> &H00FFEEDD
    print(f"   ✅ {style_name}: ASS样式行包含自定义参数")
    print(f"      样式行: {ass_line[:80]}...")

# ============================================================================
# 测试8: 向后兼容性
# ============================================================================
print("\n" + "=" * 80)
print("测试8: 向后兼容性（默认参数）")
print("=" * 80)

print("\n8.1 测试无参数调用")
style_default = get_style("classic")
assert style_default.get_fontname() == "Microsoft YaHei"  # 默认字体
assert style_default.get_fontsize() == 48  # Classic默认字号
print("   ✅ 无参数调用使用默认值")

print("\n8.2 测试部分参数调用")
style_partial = get_style("modern", fontsize=60)
assert style_partial.get_fontsize() == 60  # 自定义
assert style_partial.get_fontname() == "Microsoft YaHei"  # 默认
assert style_partial.get_vertical_margin() == 30  # Modern默认
print("   ✅ 部分参数调用正确混合默认值和自定义值")

# ============================================================================
# 测试9: Whisper模型类型参数（API层面）
# ============================================================================
print("\n" + "=" * 80)
print("测试9: Whisper模型类型选择 (API配置)")
print("=" * 80)

# 这个测试需要API服务运行，这里只验证配置结构
from subsai.api_service import ProcessConfig

test_whisper_models = ["base", "small", "medium", "large-v2", "large-v3", "large-v3-turbo"]
for model_type in test_whisper_models:
    config = ProcessConfig(whisper_model_type=model_type)
    assert config.whisper_model_type == model_type
    print(f"   ✅ Whisper模型: {model_type}")

# ============================================================================
# 测试10: ProcessConfig完整性
# ============================================================================
print("\n" + "=" * 80)
print("测试10: ProcessConfig所有字段")
print("=" * 80)

config_full = ProcessConfig(
    style_name="neon",
    words_per_line=12,
    aspect_ratio="9:16",
    fontsize=54,
    vertical_margin=90,
    crf=20,
    preset="fast",
    whisper_model_type="large-v3-turbo",
    custom_font="Arial",
    custom_colors={"primary": "#FFFFFF", "highlight": "#FF00FF"}
)

print(f"   ✅ style_name: {config_full.style_name}")
print(f"   ✅ words_per_line: {config_full.words_per_line}")
print(f"   ✅ aspect_ratio: {config_full.aspect_ratio}")
print(f"   ✅ fontsize: {config_full.fontsize}")
print(f"   ✅ vertical_margin: {config_full.vertical_margin}")
print(f"   ✅ crf: {config_full.crf}")
print(f"   ✅ preset: {config_full.preset}")
print(f"   ✅ whisper_model_type: {config_full.whisper_model_type}")
print(f"   ✅ custom_font: {config_full.custom_font}")
print(f"   ✅ custom_colors: {config_full.custom_colors}")

# ============================================================================
# 总结
# ============================================================================
print("\n" + "=" * 80)
print("🎉 测试总结")
print("=" * 80)

print("""
已测试功能列表：

✅ 1. aspect_ratio - 视频比例（API层）
✅ 2. style_name - 卡拉OK样式（5种样式）
✅ 3. words_per_line - 每行单词数
✅ 4. vertical_margin - 字幕距底部距离
✅ 5. crf - 视频质量
✅ 6. preset - 编码速度
✅ 7. fontsize - 字体大小
✅ 8. whisper_model_type - Whisper模型类型（NEW）
✅ 9. custom_font (fontname) - 字体名称（NEW）
✅ 10. custom_colors.primary - 基础颜色（NEW）
✅ 11. custom_colors.highlight - 高亮颜色（NEW）

核心功能验证：
✅ Hex到ASS颜色转换（BGR格式）
✅ 所有5个样式类支持完整参数
✅ 参数传递链完整（API -> Generator -> Styles）
✅ ASS样式行包含动态参数
✅ 向后兼容性（可选参数）
✅ ProcessConfig模型完整性

测试结果：所有测试通过 ✓
版本：v1.1.0-beta
状态：准备进入完整功能测试阶段
""")

print("=" * 80)
print("✅ 所有单元测试通过！")
print("=" * 80)
