#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试标准尺寸裁剪修复 - 验证1052*1872能正确裁剪到1080*1920
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_standard_crop_logic():
    """测试标准尺寸裁剪逻辑"""
    print("\n" + "="*70)
    print("🔬 测试标准尺寸裁剪修复")
    print("="*70)

    from subsai.video_uniqueness import get_resolution_scale_params

    # 用户报告的实际案例
    print("\n📊 测试用例: 480*832 输入\n")
    print(f"{'─'*70}")

    # 第一步：缩放
    print("🔍 第1步: 分辨率缩放")
    original_width, original_height = 480, 832
    min_resolution = 1080

    print(f"  输入尺寸: {original_width}x{original_height}")
    print(f"  最小分辨率要求: {min_resolution}p")

    params = get_resolution_scale_params(original_width, original_height, min_resolution)

    print(f"  需要缩放: {params['need_scale']}")
    print(f"  缩放后尺寸: {params['target_width']}x{params['target_height']}")

    scaled_width = params['target_width']
    scaled_height = params['target_height']

    # 第二步：计算裁剪参数（模拟main.py中的逻辑）
    print(f"\n✂️  第2步: 计算9:16标准裁剪")

    aspect_ratio = "9:16"
    target_w, target_h = map(int, aspect_ratio.split(':'))
    target_ratio = target_w / target_h

    base_width = scaled_width
    base_height = scaled_height
    base_ratio = base_width / base_height

    print(f"  缩放后尺寸: {base_width}x{base_height}")
    print(f"  当前宽高比: {base_ratio:.4f}")
    print(f"  目标宽高比: {target_ratio:.4f} (9:16)")

    # 计算标准目标尺寸（与main.py中的逻辑相同）
    min_side = min(base_width, base_height)
    print(f"  最短边: {min_side}px")

    if min_side >= min_resolution:
        print(f"  ✅ 最短边满足要求({min_resolution}p)")

        # 计算标准尺寸
        if base_ratio > target_ratio:
            # Video is wider, short side is height
            target_crop_height = base_height
            target_crop_width = int(target_crop_height * target_ratio)
        else:
            # Video is taller, short side is width
            target_crop_width = base_width
            target_crop_height = int(target_crop_width / target_ratio)

        print(f"  初步计算: {target_crop_width}x{target_crop_height}")

        # 确保裁剪后尺寸满足min_resolution
        crop_min_side = min(target_crop_width, target_crop_height)
        if crop_min_side < min_resolution:
            print(f"  ⚠️  裁剪后最短边({crop_min_side})不足，调整中...")
            if target_crop_width < target_crop_height:
                target_crop_width = min_resolution
                target_crop_height = int(min_resolution / target_ratio)
            else:
                target_crop_height = min_resolution
                target_crop_width = int(min_resolution * target_ratio)
            print(f"  调整后: {target_crop_width}x{target_crop_height}")

        # 确保偶数尺寸
        target_crop_width = target_crop_width - (target_crop_width % 2)
        target_crop_height = target_crop_height - (target_crop_height % 2)

        print(f"  偶数对齐: {target_crop_width}x{target_crop_height}")

        # 检查是否需要裁剪
        if target_crop_width != base_width or target_crop_height != base_height:
            crop_x = (base_width - target_crop_width) // 2
            crop_y = (base_height - target_crop_height) // 2

            crop_filter = f"crop={target_crop_width}:{target_crop_height}:{crop_x}:{crop_y}"
            print(f"\n  🎯 裁剪滤镜: {crop_filter}")
            print(f"  📏 输出尺寸: {target_crop_width}x{target_crop_height}")

            # 验证结果
            print(f"\n{'─'*70}")
            print("📋 验证结果:")

            output_ratio = target_crop_width / target_crop_height
            output_min_side = min(target_crop_width, target_crop_height)

            tests_passed = []
            tests_failed = []

            # 检查1：宽度是否为1080
            if target_crop_width == 1080:
                tests_passed.append("✅ 宽度正确: 1080px")
            else:
                tests_failed.append(f"❌ 宽度错误: {target_crop_width} != 1080")

            # 检查2：高度是否为1920
            if target_crop_height == 1920:
                tests_passed.append("✅ 高度正确: 1920px")
            else:
                tests_failed.append(f"❌ 高度错误: {target_crop_height} != 1920")

            # 检查3：宽高比是否为9:16
            if abs(output_ratio - target_ratio) < 0.001:
                tests_passed.append(f"✅ 宽高比正确: {output_ratio:.4f} ≈ {target_ratio:.4f}")
            else:
                tests_failed.append(f"❌ 宽高比错误: {output_ratio:.4f} != {target_ratio:.4f}")

            # 检查4：最短边是否满足要求
            if output_min_side >= min_resolution:
                tests_passed.append(f"✅ 最短边满足: {output_min_side}px >= {min_resolution}px")
            else:
                tests_failed.append(f"❌ 最短边不足: {output_min_side}px < {min_resolution}px")

            # 打印结果
            for test in tests_passed:
                print(f"  {test}")
            for test in tests_failed:
                print(f"  {test}")

            print(f"\n{'='*70}")

            if not tests_failed:
                print("🎉 测试通过！标准尺寸裁剪逻辑正确！")
                print(f"\n✨ 完整流程验证:")
                print(f"  📥 输入: {original_width}x{original_height}")
                print(f"  🔄 缩放: {scaled_width}x{scaled_height}")
                print(f"  ✂️  裁剪: {target_crop_width}x{target_crop_height}")
                print(f"  🎯 比例: 9:16")
                print(f"\n🎬 用户期望的1080*1920标准尺寸已实现！")
                return True
            else:
                print("❌ 测试失败！发现以下问题:")
                for test in tests_failed:
                    print(f"  {test}")
                return False
        else:
            print(f"  ℹ️  尺寸已是标准尺寸，无需裁剪")
            # 这种情况下也应该验证尺寸
            if base_width == 1080 and base_height == 1920:
                print(f"\n🎉 尺寸已经是1080*1920标准尺寸！")
                return True
            else:
                print(f"\n⚠️  尺寸不是预期的1080*1920")
                return False
    else:
        print(f"  ❌ 缩放后最短边({min_side})仍未达到要求({min_resolution})")
        return False

if __name__ == '__main__':
    success = test_standard_crop_logic()
    sys.exit(0 if success else 1)
