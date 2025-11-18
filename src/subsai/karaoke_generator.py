#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
卡拉OK字幕生成器 - 将词级时间戳转换为ASS卡拉OK格式
Karaoke Subtitle Generator - Convert word-level timestamps to ASS karaoke format

This module converts word-level transcription results into ASS format with karaoke effects.
"""

import re
from typing import List, Dict, Any, Optional
from pysubs2 import SSAFile, SSAEvent
from subsai.karaoke_styles import KaraokeStyle, get_style, STYLE_NAMES

__author__ = "Claude Code Assistant"
__copyright__ = "Copyright 2025"
__license__ = "GPLv3"


class KaraokeGenerator:
    """
    卡拉OK字幕生成器

    将词级时间戳转换为带\\k标签的ASS格式卡拉OK字幕
    """

    def __init__(self,
                 style_name: str = "classic",
                 words_per_line: int = 10,
                 max_line_duration_ms: int = 5000,
                 fontsize: Optional[int] = None,
                 vertical_margin: Optional[int] = None,
                 fontname: Optional[str] = None,
                 primary_color: Optional[str] = None,
                 secondary_color: Optional[str] = None,
                 max_line_width_px: Optional[int] = None):
        """
        初始化卡拉OK生成器

        Args:
            style_name: 样式名称 (classic, modern, neon, elegant, anime)
            words_per_line: 每行显示的单词数 (1-20)
            max_line_duration_ms: 每行最大持续时间（毫秒）
            fontsize: 自定义字体大小（可选，None则使用默认大小）
            vertical_margin: 自定义垂直边距/距底部像素（可选，None则使用默认值）
            fontname: 自定义字体名称（可选，None则使用默认字体）
            primary_color: 自定义基础颜色 Hex格式如"#FFFFFF"（可选）
            secondary_color: 自定义高亮颜色 Hex格式如"#FFD700"（可选）
            max_line_width_px: 单行最大宽度（像素），用于自动换行（可选，None则不限制）
        """
        self.style: KaraokeStyle = get_style(
            style_name,
            fontsize=fontsize,
            vertical_margin=vertical_margin,
            fontname=fontname,
            primary_color=primary_color,
            secondary_color=secondary_color
        )
        self.words_per_line = max(1, min(20, words_per_line))
        self.max_line_duration_ms = max_line_duration_ms
        self.max_line_width_px = max_line_width_px

    def _extract_word_timings(self, subs: SSAFile) -> List[Dict[str, Any]]:
        """
        从SSAFile中提取词级时间戳信息

        Args:
            subs: pysubs2 SSAFile对象（来自whisper-timestamped）

        Returns:
            词级时间戳列表: [{"word": str, "start": int, "end": int}, ...]
        """
        words = []

        for event in subs:
            # whisper-timestamped生成的字幕通常每行一句话
            # 我们需要分割成单词
            text = event.text.strip()
            if not text:
                continue

            # 简单按空格分割单词（后续可优化为更智能的分词）
            word_list = text.split()
            if not word_list:
                continue

            # 计算每个单词的时长（均分）
            total_duration = event.end - event.start
            word_duration = total_duration / len(word_list)

            for i, word in enumerate(word_list):
                word_start = event.start + int(i * word_duration)
                word_end = event.start + int((i + 1) * word_duration)

                words.append({
                    "word": word,
                    "start": word_start,
                    "end": word_end
                })

        return words

    def _group_words_by_lines(self, words: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        将单词按行分组

        Args:
            words: 词级时间戳列表

        Returns:
            分组后的单词列表（每个元素是一行的单词列表）
        """
        if not words:
            return []

        lines = []
        current_line = []
        current_line_start = words[0]["start"]

        for word in words:
            # 检查是否需要换行
            should_break = False

            # 条件1: 当前行单词数达到上限
            if len(current_line) >= self.words_per_line:
                should_break = True

            # 条件2: 当前行持续时间超过上限
            if current_line and (word["end"] - current_line_start) > self.max_line_duration_ms:
                should_break = True

            if should_break and current_line:
                lines.append(current_line)
                current_line = [word]
                current_line_start = word["start"]
            else:
                current_line.append(word)

        # 添加最后一行
        if current_line:
            lines.append(current_line)

        return lines

    def _estimate_text_width(self, text: str) -> float:
        """
        估算文本宽度（像素）

        Args:
            text: 文本内容

        Returns:
            估算的宽度（像素）
        """
        fontsize = self.style.get_fontsize()
        width = 0.0

        for char in text:
            if '\u4e00' <= char <= '\u9fff':  # 中文字符
                width += fontsize * 1.0
            elif char == ' ':  # 空格
                width += fontsize * 0.3
            else:  # 英文和其他字符
                width += fontsize * 0.6

        return width

    def _create_karaoke_tags(self, words: List[Dict[str, Any]]) -> str:
        """
        为一行单词创建卡拉OK标签（支持自动换行）

        Args:
            words: 单词列表（带时间戳）

        Returns:
            带\\k标签的ASS格式文本（可能包含\\N换行符）
        """
        if not words:
            return ""

        # 如果启用了自动换行，使用智能换行逻辑
        if self.max_line_width_px and self.max_line_width_px > 0:
            return self._create_karaoke_tags_with_wrap(words)

        # 原有逻辑：不换行
        result = []

        for i, word in enumerate(words):
            # 计算持续时间（厘秒，1秒=100厘秒）
            duration_ms = word["end"] - word["start"]
            duration_cs = max(1, duration_ms // 10)  # 至少1厘秒

            # 生成\\k标签
            karaoke_tag = self.style.get_karaoke_tags(duration_cs)

            # 添加单词
            result.append(f"{karaoke_tag}{word['word']}")

            # 在单词之间添加空格（最后一个单词除外）
            if i < len(words) - 1:
                result.append(" ")

        return "".join(result)

    def _create_karaoke_tags_with_wrap(self, words: List[Dict[str, Any]]) -> str:
        """
        为一行单词创建卡拉OK标签（带自动换行和居中对齐）

        Args:
            words: 单词列表（带时间戳）

        Returns:
            带\\k标签和\\N换行符的ASS格式文本，居中对齐
        """
        if not words:
            return ""

        # 添加底部居中对齐标签（左右居中，上下保持用户自定义距离）
        result = ["{\\an2}"]  # \an2 = 底部居中（水平居中，垂直位置保持距底部的距离）

        current_line_width = 0.0
        # 保留20%的边距（左右各10%）
        max_width = self.max_line_width_px * 0.8

        for i, word in enumerate(words):
            # 计算持续时间（厘秒，1秒=100厘秒）
            duration_ms = word["end"] - word["start"]
            duration_cs = max(1, duration_ms // 10)

            # 生成\\k标签
            karaoke_tag = self.style.get_karaoke_tags(duration_cs)

            # 计算单词宽度（包括前面的空格）
            word_text = word['word']
            word_width = self._estimate_text_width(word_text)

            # 如果不是第一个单词，需要加上空格的宽度
            space_width = self._estimate_text_width(" ") if i > 0 else 0

            # 检查是否需要换行（不是第一个单词，且加上新单词会超宽）
            if i > 0 and current_line_width + space_width + word_width > max_width:
                # 换行
                result.append("\\N")
                current_line_width = 0

            # 添加空格（除了第一个单词和换行后的第一个单词）
            if i > 0 and current_line_width > 0:
                result.append(" ")
                current_line_width += space_width

            # 添加单词
            result.append(f"{karaoke_tag}{word_text}")
            current_line_width += word_width

        return "".join(result)

    def generate(self, subs: SSAFile) -> SSAFile:
        """
        生成卡拉OK字幕

        Args:
            subs: 输入的SSAFile对象（来自whisper-timestamped）

        Returns:
            带卡拉OK效果的SSAFile对象
        """
        # 提取词级时间戳
        words = self._extract_word_timings(subs)

        if not words:
            return SSAFile()

        # 按行分组
        lines = self._group_words_by_lines(words)

        # 创建新的SSAFile
        karaoke_subs = SSAFile()

        # 设置样式（使用样式的style_key）
        style_name = self.style.style_key if self.style.style_key else "Default"
        karaoke_subs.styles[style_name] = self.style.get_ssa_style()

        # 为每行创建事件
        for line_words in lines:
            if not line_words:
                continue

            start_time = line_words[0]["start"]
            end_time = line_words[-1]["end"]

            # 生成带\\k标签的文本
            karaoke_text = self._create_karaoke_tags(line_words)

            event = SSAEvent(
                start=start_time,
                end=end_time,
                text=karaoke_text,
                style=style_name
            )

            karaoke_subs.append(event)

        return karaoke_subs

    def generate_from_word_list(self,
                                words: List[Dict[str, Any]],
                                merge_consecutive: bool = True) -> SSAFile:
        """
        直接从词级时间戳列表生成卡拉OK字幕

        Args:
            words: 词级时间戳列表 [{"word": str, "start": int, "end": int}, ...]
            merge_consecutive: 是否合并连续的短单词

        Returns:
            带卡拉OK效果的SSAFile对象
        """
        if not words:
            return SSAFile()

        # 按行分组
        lines = self._group_words_by_lines(words)

        # 创建新的SSAFile
        karaoke_subs = SSAFile()

        # 设置样式（使用样式的style_key）
        style_name = self.style.style_key if self.style.style_key else "Default"
        karaoke_subs.styles[style_name] = self.style.get_ssa_style()

        # 为每行创建事件
        for line_words in lines:
            if not line_words:
                continue

            start_time = line_words[0]["start"]
            end_time = line_words[-1]["end"]

            # 生成带\\k标签的文本
            karaoke_text = self._create_karaoke_tags(line_words)

            event = SSAEvent(
                start=start_time,
                end=end_time,
                text=karaoke_text,
                style=style_name
            )

            karaoke_subs.append(event)

        return karaoke_subs


def create_karaoke_subtitles(subs: SSAFile,
                             style_name: str = "classic",
                             words_per_line: int = 10,
                             max_line_duration_ms: int = 5000,
                             fontsize: Optional[int] = None,
                             vertical_margin: Optional[int] = None,
                             fontname: Optional[str] = None,
                             primary_color: Optional[str] = None,
                             secondary_color: Optional[str] = None,
                             max_line_width_px: Optional[int] = None) -> SSAFile:
    """
    便捷函数：创建卡拉OK字幕

    Args:
        subs: 输入的SSAFile对象（来自whisper-timestamped）
        style_name: 样式名称 (classic, modern, neon, elegant, anime)
        words_per_line: 每行显示的单词数 (1-20)
        max_line_duration_ms: 每行最大持续时间（毫秒）
        fontsize: 自定义字体大小（可选，None则使用默认大小）
        vertical_margin: 自定义垂直边距/距底部像素（可选，None则使用默认值）
        fontname: 自定义字体名称（可选，None则使用默认字体）
        primary_color: 自定义基础颜色 Hex格式如"#FFFFFF"（可选）
        secondary_color: 自定义高亮颜色 Hex格式如"#FFD700"（可选）
        max_line_width_px: 单行最大宽度（像素），用于自动换行和居中（可选，None则不换行）

    Returns:
        带卡拉OK效果的SSAFile对象
    """
    generator = KaraokeGenerator(
        style_name=style_name,
        words_per_line=words_per_line,
        max_line_duration_ms=max_line_duration_ms,
        fontsize=fontsize,
        vertical_margin=vertical_margin,
        fontname=fontname,
        primary_color=primary_color,
        secondary_color=secondary_color,
        max_line_width_px=max_line_width_px
    )
    return generator.generate(subs)


if __name__ == '__main__':
    # 测试代码
    print("=== 卡拉OK字幕生成器测试 ===")

    # 创建测试数据
    test_subs = SSAFile()
    test_subs.append(SSAEvent(start=0, end=3000, text="Hello world this is a test"))
    test_subs.append(SSAEvent(start=3000, end=6000, text="Karaoke subtitle generator"))

    # 测试生成
    generator = KaraokeGenerator(style_name="classic", words_per_line=5)
    karaoke = generator.generate(test_subs)

    print(f"\n生成了 {len(karaoke)} 个卡拉OK字幕事件:")
    for i, event in enumerate(karaoke):
        print(f"  [{i+1}] {event.start}ms - {event.end}ms: {event.text[:50]}...")
