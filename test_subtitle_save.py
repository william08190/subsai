#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试字幕保存功能
Test subtitle file saving functionality
"""

import tempfile
import os
import pysubs2
from pysubs2 import SSAFile, SSAEvent

def test_subtitle_save():
    """测试字幕文件保存"""
    print("=== 测试字幕保存功能 ===\n")

    # 创建测试字幕
    print("1. 创建测试字幕...")
    subs = SSAFile()
    subs.append(SSAEvent(start=0, end=1000, text="Hello"))
    subs.append(SSAEvent(start=1000, end=2000, text="World"))
    subs.append(SSAEvent(start=2000, end=3000, text="Test"))
    print(f"   ✅ 创建了 {len(subs)} 个字幕事件\n")

    # 测试方法1: 使用NamedTemporaryFile (错误方式)
    print("2. 测试方法1 - NamedTemporaryFile不关闭文件句柄:")
    temp1 = tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False, encoding='utf-8')
    path1 = temp1.name
    print(f"   临时文件路径: {path1}")

    try:
        # 不关闭文件句柄就尝试保存
        subs.save(path1)

        if os.path.exists(path1):
            size1 = os.path.getsize(path1)
            print(f"   文件存在，大小: {size1} 字节")
            if size1 > 0:
                with open(path1, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"   内容预览: {content[:100]}...")
                    print(f"   ❌ 方法1: 可能成功（取决于系统）\n")
            else:
                print(f"   ⚠️ 方法1: 文件存在但大小为0\n")
        else:
            print(f"   ❌ 方法1: 文件不存在\n")
    except Exception as e:
        print(f"   ❌ 方法1失败: {e}\n")
    finally:
        temp1.close()
        if os.path.exists(path1):
            os.unlink(path1)

    # 测试方法2: 先关闭文件句柄再保存 (正确方式)
    print("3. 测试方法2 - 先关闭文件句柄:")
    temp2 = tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False, encoding='utf-8')
    path2 = temp2.name
    temp2.close()  # 立即关闭
    print(f"   临时文件路径: {path2}")

    try:
        # 文件句柄已关闭，现在保存
        subs.save(path2)

        if os.path.exists(path2):
            size2 = os.path.getsize(path2)
            print(f"   ✅ 文件存在，大小: {size2} 字节")
            if size2 > 0:
                with open(path2, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"   内容预览:\n{content[:150]}")
                    print(f"   ✅ 方法2: 成功！\n")
            else:
                print(f"   ⚠️ 方法2: 文件存在但大小为0\n")
        else:
            print(f"   ❌ 方法2: 文件不存在\n")
    except Exception as e:
        print(f"   ❌ 方法2失败: {e}\n")
    finally:
        if os.path.exists(path2):
            os.unlink(path2)

    # 测试方法3: 直接保存到指定路径
    print("4. 测试方法3 - 直接保存到指定路径:")
    path3 = "/tmp/test_subs.srt"

    try:
        subs.save(path3)

        if os.path.exists(path3):
            size3 = os.path.getsize(path3)
            print(f"   ✅ 文件存在，大小: {size3} 字节")
            if size3 > 0:
                with open(path3, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"   内容:\n{content}")
                    print(f"   ✅ 方法3: 成功！\n")
            else:
                print(f"   ⚠️ 方法3: 文件存在但大小为0\n")
        else:
            print(f"   ❌ 方法3: 文件不存在\n")
    except Exception as e:
        print(f"   ❌ 方法3失败: {e}\n")
    finally:
        if os.path.exists(path3):
            os.unlink(path3)

    print("=== 测试完成 ===")

if __name__ == '__main__':
    test_subtitle_save()
