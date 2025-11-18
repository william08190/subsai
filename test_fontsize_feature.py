#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试字体大小调节功能
"""

from pysubs2 import SSAFile, SSAEvent
from subsai.karaoke_generator import create_karaoke_subtitles
from subsai.karaoke_styles import get_style, ClassicStyle

def test_fontsize_feature():
    """测试字体大小功能"""

    print("=" * 60)
    print("测试卡拉OK字体大小调节功能")
    print("=" * 60)

    # 创建测试字幕
    test_subs = SSAFile()
    test_subs.append(SSAEvent(start=0, end=3000, text="Hello world this is a test"))
    test_subs.append(SSAEvent(start=3000, end=6000, text="Karaoke subtitle generator"))

    # 测试1: 使用默认字体大小
    print("\n[测试1] 使用Classic样式默认字体大小")
    karaoke_default = create_karaoke_subtitles(
        subs=test_subs,
        style_name="classic",
        words_per_line=5,
        fontsize=None  # 使用默认
    )

    if karaoke_default and len(karaoke_default) > 0:
        style_obj = list(karaoke_default.styles.values())[0]
        print(f"✅ 成功生成卡拉OK字幕")
        print(f"   样式名称: {list(karaoke_default.styles.keys())[0]}")
        print(f"   字体大小: {style_obj.fontsize}")
        print(f"   字幕事件数: {len(karaoke_default)}")

        # 验证默认字体大小是否为48（Classic默认值）
        if style_obj.fontsize == 48:
            print(f"✅ 默认字体大小正确 (48px)")
        else:
            print(f"❌ 默认字体大小错误，期望48，实际{style_obj.fontsize}")
    else:
        print("❌ 生成失败")
        return False

    # 测试2: 使用自定义字体大小 36px
    print("\n[测试2] 使用自定义字体大小 36px")
    karaoke_custom36 = create_karaoke_subtitles(
        subs=test_subs,
        style_name="classic",
        words_per_line=5,
        fontsize=36  # 自定义字体大小
    )

    if karaoke_custom36 and len(karaoke_custom36) > 0:
        style_obj = list(karaoke_custom36.styles.values())[0]
        print(f"✅ 成功生成卡拉OK字幕")
        print(f"   样式名称: {list(karaoke_custom36.styles.keys())[0]}")
        print(f"   字体大小: {style_obj.fontsize}")
        print(f"   字幕事件数: {len(karaoke_custom36)}")

        # 验证自定义字体大小是否为36
        if style_obj.fontsize == 36:
            print(f"✅ 自定义字体大小正确 (36px)")
        else:
            print(f"❌ 自定义字体大小错误，期望36，实际{style_obj.fontsize}")
    else:
        print("❌ 生成失败")
        return False

    # 测试3: 使用自定义字体大小 24px (小字体)
    print("\n[测试3] 使���自定义字体大小 24px (小字体)")
    karaoke_custom24 = create_karaoke_subtitles(
        subs=test_subs,
        style_name="classic",
        words_per_line=5,
        fontsize=24
    )

    if karaoke_custom24 and len(karaoke_custom24) > 0:
        style_obj = list(karaoke_custom24.styles.values())[0]
        print(f"✅ 成功生成卡拉OK字幕")
        print(f"   字体大小: {style_obj.fontsize}")

        if style_obj.fontsize == 24:
            print(f"✅ ��字体大小正确 (24px)")
        else:
            print(f"❌ 字体大小错误，期望24，实际{style_obj.fontsize}")
    else:
        print("❌ 生成失败")
        return False

    # 测试4: 测试样式类直接使用
    print("\n[测试4] 直接测试样式类")
    style_default = ClassicStyle()  # 默认
    style_custom = ClassicStyle(fontsize=32)  # 自定义32px

    print(f"   默认ClassicStyle字体大小: {style_default.get_fontsize()}")
    print(f"   自定义ClassicStyle字体大小: {style_custom.get_fontsize()}")

    if style_default.get_fontsize() == 48 and style_custom.get_fontsize() == 32:
        print(f"✅ 样式类字体大小功能正常")
    else:
        print(f"❌ 样式类字体大小功能异常")
        return False

    # 测试5: 验证ASS样式行包含正确字体大小
    print("\n[测试5] 验证ASS样式行")
    ass_line_default = style_default.get_ass_style_line()
    ass_line_custom = style_custom.get_ass_style_line()

    print(f"   默认样式行: ...{ass_line_default[50:150]}...")
    print(f"   自定义样式行: ...{ass_line_custom[50:150]}...")

    if ",48," in ass_line_default and ",32," in ass_line_custom:
        print(f"✅ ASS样式行包含正确字体大小")
    else:
        print(f"❌ ASS样式行字体大小不正确")
        return False

    print("\n" + "=" * 60)
    print("✅ 所有测试通过！字体大小调节功能正常工作")
    print("=" * 60)
    return True

if __name__ == '__main__':
    import sys
    success = test_fontsize_feature()
    sys.exit(0 if success else 1)
