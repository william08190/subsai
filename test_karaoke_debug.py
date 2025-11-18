#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
调试卡拉OK样式问题
"""

import sys
sys.path.insert(0, '/subsai/src')

from subsai import SubsAI
from subsai.karaoke_generator import create_karaoke_subtitles
from pysubs2 import SSAFile, SSAEvent

def test_karaoke_styles():
    """测试卡拉OK样式"""
    print("=" * 60)
    print("🔍 调试卡拉OK样式问题")
    print("=" * 60)

    # 创建简单的测试字幕
    subs = SSAFile()
    subs.append(SSAEvent(start=0, end=5000, text="Hello world test"))
    subs.append(SSAEvent(start=5000, end=10000, text="This is a test"))

    print(f"\n✅ 创建了 {len(subs)} 个测试字幕")

    # 生成卡拉OK字幕
    print("\n📝 生成卡拉OK字幕...")
    karaoke_subs = create_karaoke_subtitles(
        subs=subs,
        style_name='classic',
        words_per_line=10
    )

    print(f"✅ 生成了 {len(karaoke_subs)} 个卡拉OK字幕事件")

    # 检查styles
    print(f"\n🔍 检查karaoke_subs.styles:")
    print(f"   类型: {type(karaoke_subs.styles)}")
    print(f"   长度: {len(karaoke_subs.styles)}")
    print(f"   键: {list(karaoke_subs.styles.keys())}")

    for key, value in karaoke_subs.styles.items():
        print(f"\n   样式 '{key}':")
        print(f"      类型: {type(value)}")
        print(f"      值: {value}")

        if hasattr(value, 'fontname'):
            print(f"      ✅ 有fontname属性: {value.fontname}")
        else:
            print(f"      ❌ 没有fontname属性")

    # 尝试保存
    print(f"\n💾 尝试保存ASS文件...")
    try:
        karaoke_subs.save('/tmp/test_debug.ass')
        print(f"   ✅ 保存成功!")
    except Exception as e:
        print(f"   ❌ 保存失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_karaoke_styles()
