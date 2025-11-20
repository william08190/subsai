#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试分辨率修复 - 验证9:16视频能正确生成1080x1920
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

def test_resolution_fix():
    """测试720p视频生成1080x1920的9:16输出"""
    print("\n" + "="*60)
    print("🔬 测试分辨率修复 - 验证1080x1920输出")
    print("="*60)

    # 检查测试文件
    test_srt = Path('test_data/test.srt')
    test_video = Path('test_data/test_video.mp4')

    if not test_srt.exists() or not test_video.exists():
        print("❌ 测试文件不存在")
        print(f"   需要: {test_srt} 和 {test_video}")
        return False

    try:
        # 1. 加载字幕
        print("\n📝 加载字幕...")
        subs = pysubs2.load(str(test_srt))
        karaoke_subs = create_karaoke_subtitles(subs, style_name='modern')
        print(f"✅ 字幕加载成功: {len(subs)} 行")

        # 2. 生成9:16视频，最小分辨率1080p
        print("\n🎬 生成9:16视频 (目标: 1080x1920)...")
        output = Tools.burn_karaoke_subtitles(
            karaoke_subs,
            str(test_video),
            'output_resolution_test',
            aspect_ratio='9:16',
            min_resolution=1080,
            enable_uniqueness=True,
            uniqueness_index=0
        )

        print(f"\n✅ 视频生成完成: {output}")

        # 3. 验证输出分辨率
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

        # 验证宽高比
        ratio = width / height
        expected_ratio = 9 / 16

        print(f"\n📊 详细验证:")
        print(f"   宽度: {width}px (期望: 1080px)")
        print(f"   高度: {height}px (期望: 1920px)")
        print(f"   宽高比: {ratio:.4f} (期望: {expected_ratio:.4f})")

        # 检查是否符合要求
        success = True
        if width != 1080:
            print(f"   ❌ 宽度不正确: {width} != 1080")
            success = False
        else:
            print(f"   ✅ 宽度正确: 1080px")

        if height != 1920:
            print(f"   ❌ 高度不正确: {height} != 1920")
            success = False
        else:
            print(f"   ✅ 高度正确: 1920px")

        if abs(ratio - expected_ratio) > 0.01:
            print(f"   ❌ 宽高比不正确: {ratio:.4f} != {expected_ratio:.4f}")
            success = False
        else:
            print(f"   ✅ 宽高比正确: 9:16")

        # 文件大小
        file_size = os.path.getsize(output) / (1024*1024)
        print(f"\n📁 文件大小: {file_size:.2f} MB")

        if success:
            print(f"\n🎉 测试通过！分辨率修复成功")
            print(f"   输出视频: {output}")
            print(f"   分辨率: {width}x{height} (9:16)")
            return True
        else:
            print(f"\n❌ 测试失败！分辨率不符合预期")
            return False

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_resolution_fix()
    sys.exit(0 if success else 1)
