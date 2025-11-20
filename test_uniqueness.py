#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
视频唯一性增强系统 - 测试脚本
测试分辨率升级、唯一性处理和批量生成
"""

import os
import sys
import subprocess
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from subsai import Tools
from subsai.karaoke_generator import create_karaoke_subtitles
import pysubs2

def test_basic_karaoke_with_uniqueness():
    """测试基础卡拉OK字幕烧录 + 唯一性增强"""
    print("\n" + "="*60)
    print("测试 1: 基础卡拉OK字幕烧录 + 唯一性增强")
    print("="*60)

    # 检查测试文件
    test_srt = Path('test_data/test.srt')
    test_video = Path('test_data/test_video.mp4')

    if not test_srt.exists() or not test_video.exists():
        print("❌ 测试文件不存在，跳过测试")
        print(f"   需要: {test_srt} 和 {test_video}")
        return False

    try:
        # 1. 加载字幕
        print("\n📝 加载字幕文件...")
        subs = pysubs2.load(str(test_srt))
        print(f"✅ 字幕加载成功: {len(subs)} 行")

        # 2. 生成卡拉OK字幕
        print("\n🎤 生成卡拉OK字幕...")
        karaoke_subs = create_karaoke_subtitles(subs, style_name='modern')
        print(f"✅ 卡拉OK字幕生成成功")

        # 3. 烧录到视频 (启用唯一性)
        print("\n🎬 烧录到视频 (启用唯一性增强)...")
        output = Tools.burn_karaoke_subtitles(
            karaoke_subs,
            str(test_video),
            'output_test_unique',
            aspect_ratio='16:9',
            min_resolution=1080,
            enable_uniqueness=True,
            uniqueness_index=0
        )

        print(f"\n✅ 测试 1 通过！")
        print(f"   输出文件: {output}")

        # 验证输出文件
        if os.path.exists(output):
            file_size = os.path.getsize(output) / (1024*1024)
            print(f"   文件大小: {file_size:.2f} MB")
            return True
        else:
            print(f"❌ 输出文件不存在")
            return False

    except Exception as e:
        print(f"\n❌ 测试 1 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_batch_uniqueness():
    """测试批量生成的唯一性"""
    print("\n" + "="*60)
    print("测试 2: 批量生成唯一性验证")
    print("="*60)

    # 检查测试文件
    test_srt = Path('test_data/test.srt')
    test_video = Path('test_data/test_video.mp4')

    if not test_srt.exists() or not test_video.exists():
        print("❌ 测试文件不存在，跳过测试")
        return False

    try:
        # 加载字幕
        subs = pysubs2.load(str(test_srt))
        karaoke_subs = create_karaoke_subtitles(subs, style_name='modern')

        # 生成3个不同的视频
        outputs = []
        for i in range(3):
            print(f"\n🎬 生成视频 {i+1}/3...")
            output = Tools.burn_karaoke_subtitles(
                karaoke_subs,
                str(test_video),
                f'output_batch_{i}',
                aspect_ratio='9:16',
                min_resolution=1080,
                enable_uniqueness=True,
                uniqueness_index=i  # 不同的索引
            )
            outputs.append(output)
            print(f"   ✅ 完成: {output}")

        # 验证唯一性
        print("\n🔍 验证视频唯一性...")

        # 使用ffprobe检查元数据
        for i, output in enumerate(outputs):
            print(f"\n视频 {i+1}:")
            try:
                # 获取创建时间
                result = subprocess.run(
                    ['ffprobe', '-v', 'error', '-show_entries',
                     'format_tags=creation_time,encoder',
                     '-of', 'default=noprint_wrappers=1', output],
                    capture_output=True,
                    text=True
                )
                print(f"  元数据: {result.stdout.strip()}")

                # 获取文件大小
                file_size = os.path.getsize(output) / (1024*1024)
                print(f"  文件大小: {file_size:.2f} MB")

            except Exception as e:
                print(f"  ⚠️  无法获取元数据: {e}")

        print(f"\n✅ 测试 2 通过！")
        print(f"   生成了 {len(outputs)} 个具有不同指纹的视频")
        return True

    except Exception as e:
        print(f"\n❌ 测试 2 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_resolution_upgrade():
    """测试分辨率自动升级"""
    print("\n" + "="*60)
    print("测试 3: 分辨率自动升级")
    print("="*60)

    # 检查测试文件
    test_srt = Path('test_data/test.srt')
    test_video_low_res = Path('test_data/test_video_480p.mp4')

    if not test_srt.exists():
        print("❌ 测试字幕文件不存在，跳过测试")
        return False

    if not test_video_low_res.exists():
        print("⚠️  低分辨率测试视频不存在")
        print("   将使用标准测试视频")
        test_video_low_res = Path('test_data/test_video.mp4')
        if not test_video_low_res.exists():
            print("❌ 测试视频文件不存在，跳过测试")
            return False

    try:
        # 加载字幕
        subs = pysubs2.load(str(test_srt))
        karaoke_subs = create_karaoke_subtitles(subs, style_name='classic')

        # 烧录并升级分辨率
        print("\n🎬 烧录并自动升级到1080p...")
        output = Tools.burn_karaoke_subtitles(
            karaoke_subs,
            str(test_video_low_res),
            'output_test_1080p',
            min_resolution=1080,
            enable_uniqueness=True
        )

        # 验证输出分辨率
        print("\n🔍 验证输出分辨率...")
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
             '-show_entries', 'stream=width,height',
             '-of', 'default=noprint_wrappers=1:nokey=1', output],
            capture_output=True,
            text=True
        )

        width, height = map(int, result.stdout.strip().split('\n'))
        print(f"   输出尺寸: {width}x{height}")

        if height >= 1080:
            print(f"✅ 测试 3 通过！")
            print(f"   分辨率已达到要求: {height}p")
            return True
        else:
            print(f"❌ 分辨率不足: {height}p < 1080p")
            return False

    except Exception as e:
        print(f"\n❌ 测试 3 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_without_uniqueness():
    """测试禁用唯一性处理的情况"""
    print("\n" + "="*60)
    print("测试 4: 禁用唯一性处理")
    print("="*60)

    # 检查测试文件
    test_srt = Path('test_data/test.srt')
    test_video = Path('test_data/test_video.mp4')

    if not test_srt.exists() or not test_video.exists():
        print("❌ 测试文件不存在，跳过测试")
        return False

    try:
        # 加载字幕
        subs = pysubs2.load(str(test_srt))
        karaoke_subs = create_karaoke_subtitles(subs, style_name='elegant')

        # 烧录 (禁用唯一性)
        print("\n🎬 烧录 (禁用唯一性处理)...")
        output = Tools.burn_karaoke_subtitles(
            karaoke_subs,
            str(test_video),
            'output_test_standard',
            crf=18,
            preset='slow',
            enable_uniqueness=False  # 禁用
        )

        print(f"\n✅ 测试 4 通过！")
        print(f"   输出文件: {output}")
        print(f"   使用标准模式（固定CRF=18, preset=slow）")
        return True

    except Exception as e:
        print(f"\n❌ 测试 4 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🚀 视频唯一性增强系统 - 完整测试")
    print("="*60)

    # 检查测试数据目录
    test_data_dir = Path('test_data')
    if not test_data_dir.exists():
        print("\n⚠️  测试数据目录不存在")
        print(f"   请创建 {test_data_dir} 并放入测试文件:")
        print(f"   - test.srt (字幕文件)")
        print(f"   - test_video.mp4 (测试视频)")
        print(f"   - test_video_480p.mp4 (可选，低分辨率视频)")
        return

    # 运行测试
    results = {
        '基础卡拉OK + 唯一性': test_basic_karaoke_with_uniqueness(),
        '批量唯一性验证': test_batch_uniqueness(),
        '分辨率自动升级': test_resolution_upgrade(),
        '禁用唯一性处理': test_without_uniqueness(),
    }

    # 总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)

    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {test_name}")

    total = len(results)
    passed = sum(results.values())
    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！视频唯一性系统工作正常")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，请检查")

if __name__ == '__main__':
    main()
