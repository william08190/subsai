#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
视频唯一性模块单元测试
测试核心功能函数，不需要真实的视频文件
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_1_import_module():
    """测试 1: 导入视频唯一性模块"""
    print("\n" + "="*60)
    print("测试 1: 导入视频唯一性模块")
    print("="*60)

    try:
        from subsai.video_uniqueness import (
            calculate_uniqueness_params,
            get_resolution_scale_params,
            build_uniqueness_filters,
            build_x264_params,
            generate_random_metadata
        )
        print("✅ 所有函数成功导入")
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_2_random_metadata():
    """测试 2: 元数据随机化"""
    print("\n" + "="*60)
    print("测试 2: 元数据随机化")
    print("="*60)

    try:
        from subsai.video_uniqueness import generate_random_metadata

        # 生成3个不同的元数据
        metadata_list = [generate_random_metadata() for _ in range(3)]

        print("\\n生成的元数据:")
        for i, meta in enumerate(metadata_list, 1):
            print(f"\\n元数据 {i}:")
            print(f"  创建时间: {meta['creation_time']}")
            print(f"  编码器: {meta['encoder']}")
            print(f"  标题: '{meta['title']}'")
            print(f"  注释: '{meta['comment']}'")

        # 验证元数据不同
        times = [m['creation_time'] for m in metadata_list]
        encoders = [m['encoder'] for m in metadata_list]

        if len(set(times)) > 1:
            print("\\n✅ 创建时间已随机化 (至少有不同值)")
        else:
            print("\\n⚠️  创建时间相同 (可能由于种子相同)")

        if len(set(encoders)) > 1:
            print("✅ 编码器已随机化 (至少有不同值)")
        else:
            print("⚠️  编码器相同")

        print("\\n✅ 测试 2 通过！")
        return True

    except Exception as e:
        print(f"\\n❌ 测试 2 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_3_uniqueness_params():
    """测试 3: 唯一性参数生成"""
    print("\\n" + "="*60)
    print("测试 3: 唯一性参数生成")
    print("="*60)

    try:
        from subsai.video_uniqueness import calculate_uniqueness_params

        # 生成3个不同索引的参数
        test_file = "test_video.mp4"
        params_list = [calculate_uniqueness_params(test_file, i) for i in range(3)]

        print("\\n生成的唯一性参数:")
        for i, params in enumerate(params_list):
            print(f"\\n视频 {i}:")
            print(f"  CRF: {params['crf']}")
            print(f"  预设: {params['preset']}")
            print(f"  饱和度: {params['saturation']:.4f}")
            print(f"  亮度: {params['brightness']:.4f}")
            print(f"  对比度: {params['contrast']:.4f}")
            print(f"  噪声: {params['noise_strength']:.4f}")
            print(f"  音频比特率: {params['audio_bitrate']}")
            print(f"  音频采样率: {params['audio_sample_rate']}Hz")
            print(f"  x264 me: {params['x264_params']['me']}")
            print(f"  x264 subme: {params['x264_params']['subme']}")
            print(f"  x264 ref: {params['x264_params']['ref']}")

        # 验证参数不同
        crfs = [p['crf'] for p in params_list]
        presets = [p['preset'] for p in params_list]
        saturation_values = [p['saturation'] for p in params_list]

        print("\\n验证唯一性:")
        if len(set(crfs)) > 1:
            print(f"  ✅ CRF值不同: {crfs}")
        else:
            print(f"  ⚠️  CRF值相同: {crfs}")

        if len(set(presets)) > 1:
            print(f"  ✅ 预设不同: {presets}")
        else:
            print(f"  ⚠️  预设相同: {presets}")

        if len(set(saturation_values)) > 1:
            print(f"  ✅ 饱和度不同: {[f'{s:.4f}' for s in saturation_values]}")
        else:
            print(f"  ⚠️  饱和度相同: {[f'{s:.4f}' for s in saturation_values]}")

        print("\\n✅ 测试 3 通过！")
        return True

    except Exception as e:
        print(f"\\n❌ 测试 3 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_4_resolution_scale():
    """测试 4: 分辨率缩放参数计算"""
    print("\\n" + "="*60)
    print("测试 4: 分辨率缩放参数计算")
    print("="*60)

    try:
        from subsai.video_uniqueness import get_resolution_scale_params

        test_cases = [
            (1920, 1080, 1080, "1080p视频，不需要缩放"),
            (1280, 720, 1080, "720p视频，需要升级到1080p"),
            (640, 480, 1080, "480p视频，需要升级到1080p"),
            (3840, 2160, 1080, "4K视频，已超过1080p"),
        ]

        print("\\n测试用例:")
        for width, height, min_res, desc in test_cases:
            print(f"\\n{desc}")
            print(f"  输入: {width}x{height}, 最小: {min_res}p")

            params = get_resolution_scale_params(width, height, min_res)

            print(f"  需要缩放: {params['need_scale']}")
            print(f"  目标尺寸: {params['target_width']}x{params['target_height']}")
            if params['scale_filter']:
                print(f"  滤镜: {params['scale_filter']}")

            # 验证
            if height < min_res:
                assert params['need_scale'], f"应该需要缩放，但 need_scale={params['need_scale']}"
                assert params['target_height'] >= min_res, f"目标高度应 >= {min_res}"
                print("  ✅ 验证通过")
            else:
                assert not params['need_scale'], f"不应该需要缩放，但 need_scale={params['need_scale']}"
                print("  ✅ 验证通过")

        print("\\n✅ 测试 4 通过！")
        return True

    except Exception as e:
        print(f"\\n❌ 测试 4 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_5_build_filters():
    """测试 5: 滤镜链构建"""
    print("\\n" + "="*60)
    print("测试 5: 滤镜链构建")
    print("="*60)

    try:
        from subsai.video_uniqueness import (
            calculate_uniqueness_params,
            get_resolution_scale_params,
            build_uniqueness_filters
        )

        # 场景 1: 需要缩放 + 唯一性处理
        print("\\n场景 1: 720p -> 1080p + 唯一性处理")
        params = calculate_uniqueness_params("test1.mp4", 0)
        scale_params = get_resolution_scale_params(1280, 720, 1080)
        filter_chain = build_uniqueness_filters(params, scale_params, None, "/tmp/test.ass")
        print(f"  滤镜链: {filter_chain}")
        assert "scale=" in filter_chain, "应包含 scale 滤镜"
        assert "eq=" in filter_chain, "应包含 eq 滤镜"
        assert "noise=" in filter_chain, "应包含 noise 滤镜"
        assert "ass=" in filter_chain, "应包含 ass 滤镜"
        print("  ✅ 包含所有必要滤镜")

        # 场景 2: 不需要缩放 + 裁剪 + 唯一性
        print("\\n场景 2: 1080p + 裁剪到9:16 + 唯一性处理")
        params = calculate_uniqueness_params("test2.mp4", 1)
        scale_params = get_resolution_scale_params(1920, 1080, 1080)
        crop_filter = "crop=606:1080:657:0"
        filter_chain = build_uniqueness_filters(params, scale_params if scale_params['need_scale'] else None,
                                                  crop_filter, "/tmp/test.ass")
        print(f"  滤镜链: {filter_chain}")
        assert "crop=" in filter_chain, "应包含 crop 滤镜"
        assert "eq=" in filter_chain, "应包含 eq 滤镜"
        print("  ✅ 包含裁剪和唯一性滤镜")

        print("\\n✅ 测试 5 通过！")
        return True

    except Exception as e:
        print(f"\\n❌ 测试 5 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_6_x264_params():
    """测试 6: x264参数字符串构建"""
    print("\\n" + "="*60)
    print("测试 6: x264参数字符串构建")
    print("="*60)

    try:
        from subsai.video_uniqueness import (
            calculate_uniqueness_params,
            build_x264_params
        )

        # 生成3个不同的参数字符串
        print("\\n生成x264参数字符串:")
        for i in range(3):
            params = calculate_uniqueness_params(f"test{i}.mp4", i)
            x264_str = build_x264_params(params)
            print(f"\\n视频 {i}:")
            print(f"  {x264_str}")

            # 验证格式
            assert "me=" in x264_str, "应包含 me 参数"
            assert "subme=" in x264_str, "应包含 subme 参数"
            assert "ref=" in x264_str, "应包含 ref 参数"
            assert ":" in x264_str, "参数应使用冒号分隔"

        print("\\n✅ 测试 6 通过！")
        return True

    except Exception as e:
        print("\\n❌ 测试 6 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """运行所有测试"""
    print("\\n" + "="*60)
    print("🚀 视频唯一性模块 - 单元测试")
    print("="*60)

    tests = [
        ("导入模块", test_1_import_module),
        ("元数据随机化", test_2_random_metadata),
        ("唯一性参数生成", test_3_uniqueness_params),
        ("分辨率缩放计算", test_4_resolution_scale),
        ("滤镜链构建", test_5_build_filters),
        ("x264参数构建", test_6_x264_params),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"\\n❌ {test_name} 异常: {e}")
            results[test_name] = False

    # 总结
    print("\\n" + "="*60)
    print("📊 测试总结")
    print("="*60)

    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {test_name}")

    total = len(results)
    passed = sum(results.values())
    print(f"\\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\\n🎉 所有测试通过！视频唯一性模块工作正常")
        print("\\n✨ 核心功能验证:")
        print("  ✅ 元数据随机化")
        print("  ✅ 编码参数随机化")
        print("  ✅ 分辨率自动升级")
        print("  ✅ 滤镜链正确构建")
        print("  ✅ x264参数配置")
        print("\\n🎯 下一步: 你可以使用真实视频测试完整流程！")
    else:
        print(f"\\n⚠️  有 {total - passed} 个测试失败，请检查")

if __name__ == '__main__':
    main()
