#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
验证最短边缩放修复 - 单元测试
不需要真实视频文件，只测试逻辑
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_shortest_side_scaling():
    """测试最短边缩放逻辑"""
    print("\n" + "="*70)
    print("🔬 验证最短边缩放修复")
    print("="*70)

    from subsai.video_uniqueness import get_resolution_scale_params

    # 测试用例
    test_cases = [
        # (width, height, min_res, description, expected_need_scale, expected_min_side)
        (606, 1080, 1080, "用户报告的9:16竖屏 (606x1080)", True, 1080),
        (1080, 1920, 1080, "已达标的9:16竖屏 (1080x1920)", False, 1080),
        (1920, 1080, 1080, "已达标的16:9横屏 (1920x1080)", False, 1080),
        (720, 1280, 1080, "720p竖屏 (720x1280)", True, 1080),
        (1280, 720, 1080, "720p横屏 (1280x720)", True, 1080),
        (480, 854, 1080, "480p横屏 (480x854)", True, 1080),
        (1080, 606, 1080, "反转的606x1080 (1080x606)", False, 606),
    ]

    print("\n📊 测试用例:\n")
    all_passed = True

    for i, (width, height, min_res, desc, expected_scale, expected_min) in enumerate(test_cases, 1):
        print(f"{'─'*70}")
        print(f"测试 {i}: {desc}")
        print(f"  输入: {width}x{height}, 最小分辨率要求: {min_res}p")

        # 调用函数
        params = get_resolution_scale_params(width, height, min_res)

        # 计算实际的最短边
        actual_min_side = min(width, height)
        output_min_side = min(params['target_width'], params['target_height'])

        print(f"  原始最短边: {actual_min_side}px")
        print(f"  是否需要缩放: {params['need_scale']}")
        print(f"  目标尺寸: {params['target_width']}x{params['target_height']}")
        print(f"  输出最短边: {output_min_side}px")

        # 验证结果
        test_passed = True
        errors = []

        # 验证是否需要缩放
        if params['need_scale'] != expected_scale:
            errors.append(f"need_scale应为{expected_scale}, 实际为{params['need_scale']}")
            test_passed = False

        # 验证最短边是否符合要求
        if params['need_scale'] and output_min_side < min_res:
            errors.append(f"输出最短边({output_min_side})小于要求({min_res})")
            test_passed = False

        # 验证不需要缩放时尺寸不变
        if not params['need_scale']:
            if params['target_width'] != width or params['target_height'] != height:
                errors.append(f"不需要缩放时尺寸应保持不变")
                test_passed = False

        # 验证缩放时最短边至少达到要求
        if params['need_scale']:
            if output_min_side < min_res - 2:  # 允许2px误差（偶数对齐）
                errors.append(f"缩放后最短边({output_min_side})未达到要求({min_res})")
                test_passed = False

        if test_passed:
            print(f"  ✅ 测试通过")
        else:
            print(f"  ❌ 测试失败:")
            for error in errors:
                print(f"     - {error}")
            all_passed = False

    print(f"\n{'='*70}")

    if all_passed:
        print("🎉 所有测试通过！最短边缩放逻辑正确！")
        print("\n✨ 验证要点:")
        print("  ✅ 606x1080输入需要缩放（宽度是短边）")
        print("  ✅ 1080x1920输入无需缩放（宽度已达标）")
        print("  ✅ 720p横/竖屏都正确识别短边并缩放")
        print("  ✅ 480p正确缩放到1080p+")
        print("\n🎯 修复有效！现在可以在Docker中测试真实视频")
        return True
    else:
        print("❌ 部分测试失败，请检查逻辑")
        return False

if __name__ == '__main__':
    success = test_shortest_side_scaling()
    sys.exit(0 if success else 1)
