#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量更新NeonStyle, ElegantStyle, AnimeStyle以支持自定义字体和颜色
"""

import re

file_path = 'src/subsai/karaoke_styles.py'

# 读取文件
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 定义样式更新规则
updates = [
    {
        'name': 'NeonStyle',
        'default_primary': '0x00FFFFFF',  # 白色
        'default_secondary': '0x00FF00FF',  # 紫红色
    },
    {
        'name': 'ElegantStyle',
        'default_primary': '0x00FFFFFF',  # 白色
        'default_secondary': '0x00FFD700',  # 金色
    },
    {
        'name': 'AnimeStyle',
        'default_primary': '0x00FFFFFF',  # 白色
        'default_secondary': '0x0000FFFF',  # 青色
    }
]

for update in updates:
    style_name = update['name']

    # 1. 更新构造函数参数
    pattern = rf'(class {style_name}\(KaraokeStyle\):.*?def __init__\(self, fontsize: Optional\[int\] = None, vertical_margin: Optional\[int\] = None)\):'
    replacement = r'\1,\n                 fontname: Optional[str] = None, primary_color: Optional[str] = None,\n                 secondary_color: Optional[str] = None):'
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # 2. 更新super().__init__调用
    pattern = rf'({style_name}.*?super\(\).__init__\(.*?fontsize=fontsize,\s*vertical_margin=vertical_margin)\s*\)'
    replacement = r'\1,\n            fontname=fontname,\n            primary_color=primary_color,\n            secondary_color=secondary_color\n        )'
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # 3. 添加默认颜色方法（在get_default_vertical_margin后面）
    pattern = rf'({style_name}.*?def get_default_vertical_margin\(self\) -> int:\s*return \d+)'
    color_methods = f'''

    def get_default_primary_color(self) -> int:
        return {update['default_primary']}  # 默认基础颜色

    def get_default_secondary_color(self) -> int:
        return {update['default_secondary']}  # 默认高亮颜色'''

    replacement = r'\1' + color_methods
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # 4. 更新get_ass_style_line()方法
    #    查找并替换硬编码的fontname
    pattern = rf'({style_name}.*?def get_ass_style_line\(self\) -> str:.*?fontsize = self\.get_fontsize\(\)\s*vertical_margin = self\.get_vertical_margin\(\))'

    replacement = r'''\1
        fontname = self.get_fontname()
        primary_color = self.get_primary_color()
        secondary_color = self.get_secondary_color()'''

    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # 替换Style行中的硬编码字体名和颜色
    # 查找类似: Style: Neon,Microsoft YaHei,{fontsize},&H00FFFFFF,&H00FF00FF
    # 替换为: Style: Neon,{fontname},{fontsize},&H{primary_color:08X},&H{secondary_color:08X}
    pattern = rf'(return f"Style: {style_name},)Microsoft YaHei,({{fontsize}}),&H[0-9A-F]{{8}},&H[0-9A-F]{{8}}'
    replacement = r'\1{fontname},\2,&H{primary_color:08X},&H{secondary_color:08X}'
    content = re.sub(pattern, replacement, content)

    # 5. 更新get_ssa_style()方法
    pattern = rf'({style_name}.*?def get_ssa_style\(self\) -> SSAStyle:.*?return SSAStyle\(\s*)fontname="Microsoft YaHei",\s*fontsize=self\.get_fontsize\(\),\s*primarycolor=0x[0-9A-F]{{8}},  # .*?\s*secondarycolor=0x[0-9A-F]{{8}},  # .*?'

    replacement = r'''\1fontname=self.get_fontname(),
            fontsize=self.get_fontsize(),
            primarycolor=self.get_primary_color(),
            secondarycolor=self.get_secondary_color(),'''

    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

print("开始批量更新样式类...")

# 写回文件
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ 成功更新 {len(updates)} 个样式类")
print("已更新: NeonStyle, ElegantStyle, AnimeStyle")
