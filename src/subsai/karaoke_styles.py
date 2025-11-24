#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
卡拉OK样式定义 - 5种可选样式
Karaoke Styles Definition - 5 Style Options

This module defines ASS subtitle styles for karaoke effects with word-level highlighting.
"""

from typing import Dict, Any, Optional
from pysubs2 import SSAStyle

__author__ = "Claude Code Assistant"
__copyright__ = "Copyright 2025"
__license__ = "GPLv3"

# ASS字幕文件头部模板
ASS_HEADER_TEMPLATE = """[Script Info]
Title: Karaoke Subtitle
ScriptType: v4.00+
WrapStyle: 0
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{style_line}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


class KaraokeStyle:
    """卡拉OK样式基类"""

    def __init__(self, style_id: int, name: str, description: str, style_key: str = "",
                 fontsize: Optional[int] = None, vertical_margin: Optional[int] = None,
                 fontname: Optional[str] = None, primary_color: Optional[str] = None,
                 secondary_color: Optional[str] = None):
        self.style_id = style_id
        self.name = name
        self.description = description
        self.style_key = style_key  # ASS样式名称（如 "Classic", "Modern"）
        self.custom_fontsize = fontsize  # 自定义字体大小
        self.custom_vertical_margin = vertical_margin  # 自定义垂直边距（距底部像素）
        self.custom_fontname = fontname  # 自定义字体名称
        self.custom_primary_color = primary_color  # 自定义基础颜色（Hex格式如 "#FFFFFF"）
        self.custom_secondary_color = secondary_color  # 自定义高亮颜色（Hex格式如 "#FFD700"）

    def get_default_fontsize(self) -> int:
        """返回默认字体大小"""
        raise NotImplementedError

    def get_fontsize(self) -> int:
        """获取实际使用的字体大小"""
        return self.custom_fontsize if self.custom_fontsize is not None else self.get_default_fontsize()

    def get_default_vertical_margin(self) -> int:
        """返回默认垂直边距（距底部像素）"""
        raise NotImplementedError

    def get_vertical_margin(self) -> int:
        """获取实际使用的垂直边距"""
        return self.custom_vertical_margin if self.custom_vertical_margin is not None else self.get_default_vertical_margin()

    def get_default_fontname(self) -> str:
        """返回默认字体名称"""
        return "Microsoft YaHei"

    def get_fontname(self) -> str:
        """获取实际使用的字体名称"""
        return self.custom_fontname if self.custom_fontname else self.get_default_fontname()

    def get_default_primary_color(self) -> int:
        """返回默认基础颜色（ASS格式）"""
        raise NotImplementedError

    def get_primary_color(self) -> int:
        """获取实际使用的基础颜色（ASS格式）"""
        if self.custom_primary_color:
            return self._hex_to_ass_color(self.custom_primary_color)
        return self.get_default_primary_color()

    def get_default_secondary_color(self) -> int:
        """返回默认高亮颜色（ASS格式）"""
        raise NotImplementedError

    def get_secondary_color(self) -> int:
        """获取实际使用的高亮颜色（ASS格式）"""
        if self.custom_secondary_color:
            return self._hex_to_ass_color(self.custom_secondary_color)
        return self.get_default_secondary_color()

    @staticmethod
    def _hex_to_ass_color(hex_color: str) -> int:
        """
        将Hex颜色转换为ASS颜色格式

        Args:
            hex_color: Hex颜色字符串（如 "#FFFFFF" 或 "#FFD700"）

        Returns:
            ASS颜色整数（BGR格式）
        """
        # 移除#号
        hex_color = hex_color.lstrip('#')

        # 解析RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        # ASS颜色格式是 &H00BBGGRR (BGR顺序)
        return (b << 16) | (g << 8) | r

    def get_ass_style_line(self) -> str:
        """返回ASS样式定义行"""
        raise NotImplementedError

    def get_ssa_style(self) -> SSAStyle:
        """返回pysubs2的SSAStyle对象"""
        raise NotImplementedError

    def get_karaoke_tags(self, duration_cs: int) -> str:
        """
        生成卡拉OK效果的ASS标签

        Args:
            duration_cs: 持续时间（厘秒，1秒=100厘秒）

        Returns:
            卡拉OK标签字符串 (例如: {\\kf50})
        """
        return f"{{\\kf{duration_cs}}}"  # 使用 \kf 填充效果（从左到右平滑填充）


class ClassicStyle(KaraokeStyle):
    """经典风格 - 传统KTV样式，黄色高亮，下方居中"""

    def __init__(self, fontsize: Optional[int] = None, vertical_margin: Optional[int] = None,
                 fontname: Optional[str] = None, primary_color: Optional[str] = None,
                 secondary_color: Optional[str] = None):
        super().__init__(
            style_id=1,
            name="经典风格 Classic",
            description="传统KTV卡拉OK样式，黄色高亮，下方居中显示",
            style_key="Classic",
            fontsize=fontsize,
            vertical_margin=vertical_margin,
            fontname=fontname,
            primary_color=primary_color,
            secondary_color=secondary_color
        )

    def get_default_fontsize(self) -> int:
        return 48

    def get_default_vertical_margin(self) -> int:
        return 120

    def get_default_primary_color(self) -> int:
        return 0x00FFFFFF  # 白色

    def get_default_secondary_color(self) -> int:
        return 0x0000FFFF  # 黄色

    def get_ass_style_line(self) -> str:
        # Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
        # PrimaryColour: 白色 &H00FFFFFF
        # SecondaryColour: 黄色 &H0000FFFF (卡拉OK高亮色)
        # OutlineColour: 黑色边框 &H00000000
        # Alignment: 2 = 底部居中
        fontname = self.get_fontname()
        fontsize = self.get_fontsize()
        vertical_margin = self.get_vertical_margin()
        primary_color = self.get_primary_color()
        secondary_color = self.get_secondary_color()
        return f"Style: Classic,{fontname},{fontsize},&H{primary_color:08X},&H{secondary_color:08X},&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,2,2,30,30,{vertical_margin},1"

    def get_ssa_style(self) -> SSAStyle:
        return SSAStyle(
            fontname=self.get_fontname(),
            fontsize=self.get_fontsize(),
            primarycolor=self.get_primary_color(),
            secondarycolor=self.get_secondary_color(),
            outlinecolor=0x00000000,  # 黑色边框
            backcolor=0x80000000,
            bold=True,
            italic=False,
            underline=False,
            strikeout=False,
            scalex=100.0,
            scaley=100.0,
            spacing=0.0,
            angle=0.0,
            borderstyle=1,
            outline=3.0,
            shadow=2.0,
            alignment=2,  # 底部居中
            marginl=30,
            marginr=30,
            marginv=self.get_vertical_margin()
        )


class ModernStyle(KaraokeStyle):
    """现代风格 - 简约设计，橙色渐变，顶部居中"""

    def __init__(self, fontsize: Optional[int] = None, vertical_margin: Optional[int] = None,
                 fontname: Optional[str] = None, primary_color: Optional[str] = None,
                 secondary_color: Optional[str] = None):
        super().__init__(
            style_id=2,
            name="现代风格 Modern",
            description="现代简约设计，橙色渐变高亮，顶部居中显示",
            style_key="Modern",
            fontsize=fontsize,
            vertical_margin=vertical_margin,
            fontname=fontname,
            primary_color=primary_color,
            secondary_color=secondary_color
        )

    def get_default_fontsize(self) -> int:
        return 52

    def get_default_vertical_margin(self) -> int:
        return 30

    def get_default_primary_color(self) -> int:
        return 0x00FFFFFF  # 白色

    def get_default_secondary_color(self) -> int:
        return 0x00FF8C00  # 橙色

    def get_ass_style_line(self) -> str:
        # PrimaryColour: 白色 &H00FFFFFF
        # SecondaryColour: 橙色 &H00FF8C00
        # Alignment: 8 = 顶部居中
        fontname = self.get_fontname()
        fontsize = self.get_fontsize()
        vertical_margin = self.get_vertical_margin()
        primary_color = self.get_primary_color()
        secondary_color = self.get_secondary_color()
        return f"Style: Modern,{fontname},{fontsize},&H{primary_color:08X},&H{secondary_color:08X},&H00000000,&H80000000,-1,0,0,0,100,100,2,0,1,2,1,8,30,30,{vertical_margin},1"

    def get_ssa_style(self) -> SSAStyle:
        return SSAStyle(
            fontname=self.get_fontname(),
            fontsize=self.get_fontsize(),
            primarycolor=self.get_primary_color(),
            secondarycolor=self.get_secondary_color(),
            outlinecolor=0x00000000,
            backcolor=0x80000000,
            bold=True,
            italic=False,
            underline=False,
            strikeout=False,
            scalex=100.0,
            scaley=100.0,
            spacing=2.0,
            angle=0.0,
            borderstyle=1,
            outline=2.0,
            shadow=1.0,
            alignment=8,  # 顶部居中
            marginl=30,
            marginr=30,
            marginv=self.get_vertical_margin()
        )


class NeonStyle(KaraokeStyle):
    """霓虹风格 - 赛博朋克效果，紫红色光晕"""

    def __init__(self, fontsize: Optional[int] = None, vertical_margin: Optional[int] = None,
                 fontname: Optional[str] = None, primary_color: Optional[str] = None,
                 secondary_color: Optional[str] = None):
        super().__init__(
            style_id=3,
            name="霓虹风格 Neon",
            description="赛博朋克霓虹效果，紫红色光晕，中部居中",
            style_key="Neon",
            fontsize=fontsize,
            vertical_margin=vertical_margin,
            fontname=fontname,
            primary_color=primary_color,
            secondary_color=secondary_color
        )

    def get_default_fontsize(self) -> int:
        return 50

    def get_default_vertical_margin(self) -> int:
        return 80

    def get_default_primary_color(self) -> int:
        return 0x00FFFFFF  # 默认基础颜色

    def get_default_secondary_color(self) -> int:
        return 0x00FF00FF  # 默认高亮颜色

    def get_ass_style_line(self) -> str:
        # PrimaryColour: 白色 &H00FFFFFF
        # SecondaryColour: 紫红色 &H00FF00FF
        # OutlineColour: 紫红色边框 &H00FF00FF
        # Alignment: 5 = 中部居中
        fontsize = self.get_fontsize()
        vertical_margin = self.get_vertical_margin()
        fontname = self.get_fontname()
        primary_color = self.get_primary_color()
        secondary_color = self.get_secondary_color()
        return f"Style: Neon,{fontname},{fontsize},&H{primary_color:08X},&H{secondary_color:08X},&H{secondary_color:08X},&H80{secondary_color:06X},-1,0,0,0,100,100,1,0,1,4,4,5,30,30,{vertical_margin},1"

    def get_ssa_style(self) -> SSAStyle:
        return SSAStyle(
            fontname=self.get_fontname(),
            fontsize=self.get_fontsize(),
            primarycolor=self.get_primary_color(),  # 白色
            secondarycolor=self.get_secondary_color(),  # 紫红色
            outlinecolor=0x00FF00FF,  # 紫红色边框
            backcolor=0x80FF00FF,
            bold=True,
            italic=False,
            underline=False,
            strikeout=False,
            scalex=100.0,
            scaley=100.0,
            spacing=1.0,
            angle=0.0,
            borderstyle=1,
            outline=4.0,
            shadow=4.0,
            alignment=5,  # 中部居中
            marginl=30,
            marginr=30,
            marginv=self.get_vertical_margin()
        )


class ElegantStyle(KaraokeStyle):
    """优雅风格 - 金色柔和动画"""

    def __init__(self, fontsize: Optional[int] = None, vertical_margin: Optional[int] = None,
                 fontname: Optional[str] = None, primary_color: Optional[str] = None,
                 secondary_color: Optional[str] = None):
        super().__init__(
            style_id=4,
            name="优雅风格 Elegant",
            description="优雅字体，金色柔和动画，下方居中",
            style_key="Elegant",
            fontsize=fontsize,
            vertical_margin=vertical_margin,
            fontname=fontname,
            primary_color=primary_color,
            secondary_color=secondary_color
        )

    def get_default_fontsize(self) -> int:
        return 46

    def get_default_vertical_margin(self) -> int:
        return 100

    def get_default_primary_color(self) -> int:
        return 0x00FFFFFF  # 默认基础颜色

    def get_default_secondary_color(self) -> int:
        return 0x00FFD700  # 默认高亮颜色

    def get_ass_style_line(self) -> str:
        # PrimaryColour: 白色 &H00FFFFFF
        # SecondaryColour: 金色 &H00FFD700
        # ScaleX: 105 (稍微拉宽)
        # Alignment: 2 = 底部居中
        fontsize = self.get_fontsize()
        vertical_margin = self.get_vertical_margin()
        fontname = self.get_fontname()
        primary_color = self.get_primary_color()
        secondary_color = self.get_secondary_color()
        return f"Style: Elegant,{fontname},{fontsize},&H{primary_color:08X},&H{secondary_color:08X},&H00000000,&H80000000,-1,0,0,0,105,100,1,0,1,2,2,2,30,30,{vertical_margin},1"

    def get_ssa_style(self) -> SSAStyle:
        return SSAStyle(
            fontname=self.get_fontname(),
            fontsize=self.get_fontsize(),
            primarycolor=self.get_primary_color(),  # 白色
            secondarycolor=self.get_secondary_color(),  # 金色
            outlinecolor=0x00000000,
            backcolor=0x80000000,
            bold=True,
            italic=False,
            underline=False,
            strikeout=False,
            scalex=105.0,
            scaley=100.0,
            spacing=1.0,
            angle=0.0,
            borderstyle=1,
            outline=2.0,
            shadow=2.0,
            alignment=2,  # 底部居中
            marginl=30,
            marginr=30,
            marginv=self.get_vertical_margin()
        )


class AnimeStyle(KaraokeStyle):
    """动漫风格 - 青色描边效果"""

    def __init__(self, fontsize: Optional[int] = None, vertical_margin: Optional[int] = None,
                 fontname: Optional[str] = None, primary_color: Optional[str] = None,
                 secondary_color: Optional[str] = None):
        super().__init__(
            style_id=5,
            name="动漫风格 Anime",
            description="动漫字幕风格，青色描边效果，下方居中",
            style_key="Anime",
            fontsize=fontsize,
            vertical_margin=vertical_margin,
            fontname=fontname,
            primary_color=primary_color,
            secondary_color=secondary_color
        )

    def get_default_fontsize(self) -> int:
        return 44

    def get_default_vertical_margin(self) -> int:
        return 110

    def get_default_primary_color(self) -> int:
        return 0x00FFFFFF  # 默认基础颜色

    def get_default_secondary_color(self) -> int:
        return 0x0000FFFF  # 默认高亮颜色

    def get_ass_style_line(self) -> str:
        # PrimaryColour: 白色 &H00FFFFFF
        # SecondaryColour: 青色 &H0000FFFF
        # Outline: 4 (粗边框)
        # Alignment: 2 = 底部居中
        fontsize = self.get_fontsize()
        vertical_margin = self.get_vertical_margin()
        fontname = self.get_fontname()
        primary_color = self.get_primary_color()
        secondary_color = self.get_secondary_color()
        return f"Style: Anime,{fontname},{fontsize},&H{primary_color:08X},&H{secondary_color:08X},&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,3,2,30,30,{vertical_margin},1"

    def get_ssa_style(self) -> SSAStyle:
        return SSAStyle(
            fontname=self.get_fontname(),
            fontsize=self.get_fontsize(),
            primarycolor=self.get_primary_color(),  # 白色
            secondarycolor=self.get_secondary_color(),  # 青色
            outlinecolor=0x00000000,
            backcolor=0x80000000,
            bold=True,
            italic=False,
            underline=False,
            strikeout=False,
            scalex=100.0,
            scaley=100.0,
            spacing=0.0,
            angle=0.0,
            borderstyle=1,
            outline=4.0,
            shadow=3.0,
            alignment=2,  # 底部居中
            marginl=30,
            marginr=30,
            marginv=self.get_vertical_margin()
        )


# 样式映射表
STYLE_CLASSES: Dict[str, type] = {
    "classic": ClassicStyle,
    "modern": ModernStyle,
    "neon": NeonStyle,
    "elegant": ElegantStyle,
    "anime": AnimeStyle
}

STYLE_NAMES: Dict[str, str] = {
    "classic": "Classic",
    "modern": "Modern",
    "neon": "Neon",
    "elegant": "Elegant",
    "anime": "Anime"
}


def get_style(style_name: str,
               fontsize: Optional[int] = None,
               vertical_margin: Optional[int] = None,
               fontname: Optional[str] = None,
               primary_color: Optional[str] = None,
               secondary_color: Optional[str] = None) -> KaraokeStyle:
    """
    获取指定样式实例

    Args:
        style_name: 样式名称 (classic, modern, neon, elegant, anime)
        fontsize: 自定义字体大小 (可选)
        vertical_margin: 自定义垂直边距/距底部像素 (可选)
        fontname: 自定义字体名称 (可选)
        primary_color: 自定义基础颜色 Hex格式如"#FFFFFF" (可选)
        secondary_color: 自定义高亮颜色 Hex格式如"#FFD700" (可选)

    Returns:
        KaraokeStyle实例
    """
    style_class = STYLE_CLASSES.get(style_name.lower(), ClassicStyle)
    return style_class(
        fontsize=fontsize,
        vertical_margin=vertical_margin,
        fontname=fontname,
        primary_color=primary_color,
        secondary_color=secondary_color
    )


def get_all_styles(fontsize: Optional[int] = None) -> Dict[str, KaraokeStyle]:
    """获取所有可用样式"""
    return {name: cls(fontsize=fontsize) for name, cls in STYLE_CLASSES.items()}


def get_style_names() -> list:
    """获取所有样式名称列表（用于WebUI选择）"""
    return list(STYLE_CLASSES.keys())


def generate_ass_header(style: KaraokeStyle) -> str:
    """
    生成ASS字幕文件头部

    Args:
        style: 卡拉OK样式实例

    Returns:
        完整的ASS文件头部
    """
    return ASS_HEADER_TEMPLATE.format(style_line=style.get_ass_style_line())


if __name__ == '__main__':
    # 测试代码
    print("=== 可用的卡拉OK样式 ===")
    for name, style_obj in get_all_styles().items():
        print(f"\n{style_obj.name}")
        print(f"  描述: {style_obj.description}")
        print(f"  默认字体大小: {style_obj.get_default_fontsize()}")
        print(f"  ASS样式: {style_obj.get_ass_style_line()}")
        print(f"  卡拉OK标签示例: {style_obj.get_karaoke_tags(50)}")

    # 测试自定义字体大小
    print("\n=== 测试自定义字体大小 ===")
    custom_style = get_style("classic", fontsize=32)
    print(f"Classic样式，自定义字体大小32: {custom_style.get_ssa_style().fontsize}")
