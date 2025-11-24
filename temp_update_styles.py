#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
临时脚本：批量更新样式类以支持自定义字体和颜色
"""

import re

# 读取文件
with open('src/subsai/karaoke_styles.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ModernStyle 修改
content = re.sub(
    r'class ModernStyle\(KaraokeStyle\):\s*"""现代风格 - 简约设计，橙色渐变，顶部居中"""\s*def __init__\(self, fontsize: Optional\[int\] = None, vertical_margin: Optional\[int\] = None\):',
    '''class ModernStyle(KaraokeStyle):
    """现代风格 - 简约设计，橙色渐变，顶部居中"""

    def __init__(self, fontsize: Optional[int] = None, vertical_margin: Optional[int] = None,
                 fontname: Optional[str] = None, primary_color: Optional[str] = None,
                 secondary_color: Optional[str] = None):''',
    content
)

content = re.sub(
    r'(class ModernStyle.*?def __init__.*?super\(\).__init__\(\s*style_id=2,\s*name="现代风格 Modern",\s*description="现代简约设计，橙色渐变高亮，顶部居中显示",\s*style_key="Modern",\s*fontsize=fontsize,\s*vertical_margin=vertical_margin)\s*\)',
    r'\1,\n            fontname=fontname,\n            primary_color=primary_color,\n            secondary_color=secondary_color\n        )',
    content,
    flags=re.DOTALL
)

# 为每个样式类添加颜色方法
# 由于正则表达式很复杂，我们手动构建内容

print("正在更新样式文件...")
print("警告：此脚本需要手动修改，因为正则表达式过于复杂")
print("建议手动修改剩余的4个样式类")
