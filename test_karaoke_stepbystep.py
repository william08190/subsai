#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
详细调试卡拉OK生成过程
"""

import sys
sys.path.insert(0, '/subsai/src')

from pysubs2 import SSAFile, SSAEvent
from subsai.karaoke_generator import KaraokeGenerator
from subsai.karaoke_styles import ClassicStyle

def test_generation_step_by_step():
    """逐步测试生成过程"""
    print("=" * 60)
    print("🔍 逐步调试卡拉OK生成过程")
    print("=" * 60)

    # 1. 创建测试字幕
    subs = SSAFile()
    subs.append(SSAEvent(start=0, end=5000, text="Hello world test"))
    print("\n1️⃣ 创建测试字幕")
    print(f"   字幕数: {len(subs)}")

    # 2. 创建样式对象
    print("\n2️⃣ 创建样式对象")
    style = ClassicStyle()
    print(f"   样式类型: {type(style)}")
    print(f"   样式名称: {style.name}")

    # 3. 测试get_ssa_style
    print("\n3️⃣ 测试get_ssa_style()")
    ssa_style = style.get_ssa_style()
    print(f"   返回类型: {type(ssa_style)}")
    print(f"   返回值: {ssa_style}")

    # 4. 创建生成器
    print("\n4️⃣ 创建卡拉OK生成器")
    generator = KaraokeGenerator(style_name='classic', words_per_line=10)
    print(f"   生成器类型: {type(generator)}")
    print(f"   生成器样式: {generator.style}")
    print(f"   生成器样式类型: {type(generator.style)}")

    # 5. 调用generate()
    print("\n5️⃣ 调用generate()方法")
    try:
        karaoke_subs = generator.generate(subs)
        print(f"   ✅ 生成成功")
        print(f"   卡拉OK字幕数: {len(karaoke_subs)}")

        # 6. 检查styles
        print("\n6️⃣ 检查生成的styles")
        print(f"   styles类型: {type(karaoke_subs.styles)}")
        print(f"   styles长度: {len(karaoke_subs.styles)}")
        print(f"   styles键: {list(karaoke_subs.styles.keys())}")

        for key, value in karaoke_subs.styles.items():
            print(f"\n   样式 '{key}':")
            print(f"      类型: {type(value)}")
            print(f"      值: {value}")
            if hasattr(value, 'fontname'):
                print(f"      ✅ 有fontname: {value.fontname}")
            else:
                print(f"      ❌ 没有fontname")

        # 7. 尝试保存
        print("\n7️⃣ 尝试保存")
        karaoke_subs.save('/tmp/test_step_by_step.ass')
        print(f"   ✅ 保存成功!")

    except Exception as e:
        print(f"   ❌ 失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_generation_step_by_step()
