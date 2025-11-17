#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
卡拉OK功能测试脚本
Karaoke Feature Test Script

自动化测试卡拉OK字幕生成功能
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pysubs2 import SSAFile, SSAEvent
from subsai.karaoke_styles import get_all_styles, get_style
from subsai.karaoke_generator import KaraokeGenerator, create_karaoke_subtitles


def test_karaoke_styles():
    """测试卡拉OK样式定义"""
    print("\n" + "="*60)
    print("测试 1: 卡拉OK样式定义")
    print("="*60)

    try:
        all_styles = get_all_styles()
        assert len(all_styles) == 5, "应该有5种样式"

        for style_name, style_obj in all_styles.items():
            print(f"\n✓ 样式: {style_obj.name}")
            print(f"  描述: {style_obj.description}")
            print(f"  ASS定义长度: {len(style_obj.get_ass_style_line())} 字符")
            print(f"  卡拉OK标签示例: {style_obj.get_karaoke_tags(50)}")

            # 验证ASS样式行格式
            style_line = style_obj.get_ass_style_line()
            assert style_line.startswith("Style: "), "ASS样式行应以'Style: '开头"
            assert len(style_line.split(',')) >= 20, "ASS样式应包含至少20个字段"

        print("\n✅ 样式定义测试通过")
        return True

    except Exception as e:
        print(f"\n❌ 样式定义测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_karaoke_generator():
    """测试卡拉OK生成器"""
    print("\n" + "="*60)
    print("测试 2: 卡拉OK生成器")
    print("="*60)

    try:
        # 创建测试字幕数据
        test_subs = SSAFile()
        test_subs.append(SSAEvent(start=0, end=3000, text="Hello world this is a test"))
        test_subs.append(SSAEvent(start=3000, end=6000, text="Karaoke subtitle generator"))
        test_subs.append(SSAEvent(start=6000, end=9000, text="Word level highlighting effects"))

        print(f"\n创建了 {len(test_subs)} 个测试字幕事件")

        # 测试每种样式
        for style_name in ['classic', 'modern', 'neon', 'elegant', 'anime']:
            generator = KaraokeGenerator(
                style_name=style_name,
                words_per_line=5
            )

            karaoke_subs = generator.generate(test_subs)

            print(f"\n✓ 样式 '{style_name}': 生成了 {len(karaoke_subs)} 个卡拉OK事件")

            # 验证生成的字幕
            assert len(karaoke_subs) > 0, "应该生成至少1个卡拉OK事件"

            # 检查第一个事件
            first_event = karaoke_subs[0]
            print(f"  第一个事件预览: {first_event.text[:80]}...")

            # 验证包含\k标签
            assert "\\k" in first_event.text, "卡拉OK字幕应包含\\k标签"

        print("\n✅ 卡拉OK生成器测试通过")
        return True

    except Exception as e:
        print(f"\n❌ 卡拉OK生成器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_convenience_function():
    """测试便捷函数"""
    print("\n" + "="*60)
    print("测试 3: 便捷函数")
    print("="*60)

    try:
        # 创建测试字幕数据
        test_subs = SSAFile()
        test_subs.append(SSAEvent(start=0, end=2000, text="Test one two three"))
        test_subs.append(SSAEvent(start=2000, end=4000, text="Four five six seven"))

        # 使用便捷函数生成卡拉OK字幕
        karaoke_subs = create_karaoke_subtitles(
            subs=test_subs,
            style_name="classic",
            words_per_line=8
        )

        print(f"\n✓ 便捷函数生成了 {len(karaoke_subs)} 个卡拉OK事件")

        # 验证
        assert len(karaoke_subs) > 0, "应该生成至少1个卡拉OK事件"

        for i, event in enumerate(karaoke_subs):
            print(f"  事件{i+1}: {event.start}ms - {event.end}ms")
            print(f"    内容: {event.text[:60]}...")

        print("\n✅ 便捷函数测试通过")
        return True

    except Exception as e:
        print(f"\n❌ 便捷函数测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ass_file_generation():
    """测试ASS文件生成"""
    print("\n" + "="*60)
    print("测试 4: ASS文件生成")
    print("="*60)

    try:
        import tempfile

        # 创建测试字幕
        test_subs = SSAFile()
        test_subs.append(SSAEvent(start=0, end=3000, text="Testing ASS file generation"))

        # 生成卡拉OK字幕
        karaoke_subs = create_karaoke_subtitles(test_subs, style_name="neon")

        # 保存到临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ass', delete=False, encoding='utf-8') as tmp:
            karaoke_subs.save(tmp.name)
            tmp_path = tmp.name

        print(f"\n✓ ASS文件已保存到: {tmp_path}")

        # 读取并验证文件内容
        with open(tmp_path, 'r', encoding='utf-8') as f:
            content = f.read()

        print(f"  文件大小: {len(content)} 字节")

        # 验证ASS文件格式
        assert "[Script Info]" in content, "ASS文件应包含[Script Info]"
        assert "[V4+ Styles]" in content, "ASS文件应包含[V4+ Styles]"
        assert "[Events]" in content, "ASS文件应包含[Events]"
        assert "\\k" in content, "ASS文件应包含\\k卡拉OK标签"

        print(f"\n  ✓ ASS文件格式正确")

        # 清理临时文件
        os.unlink(tmp_path)

        print("\n✅ ASS文件生成测试通过")
        return True

    except Exception as e:
        print(f"\n❌ ASS文件生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "🎵"*30)
    print("   卡拉OK功能自动化测试套件")
    print("🎵"*30)

    results = []

    # 运行所有测试
    results.append(("样式定义", test_karaoke_styles()))
    results.append(("卡拉OK生成器", test_karaoke_generator()))
    results.append(("便捷函数", test_convenience_function()))
    results.append(("ASS文件生成", test_ass_file_generation()))

    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}: {test_name}")

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！卡拉OK功能正常工作。")
        return 0
    else:
        print(f"\n⚠️ {total - passed} 个测试失败，请检查错误信息。")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
