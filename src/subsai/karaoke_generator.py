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
                 max_line_duration_ms: int = 5000):
        """
        初始化卡拉OK生成器

        Args:
            style_name: 样式名称 (classic, modern, neon, elegant, anime)
            words_per_line: 每行显示的单词数 (1-20)
            max_line_duration_ms: 每行最大持续时间（毫秒）
        """
        self.style: KaraokeStyle = get_style(style_name)
        self.words_per_line = max(1, min(20, words_per_line))
        self.max_line_duration_ms = max_line_duration_ms

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

    def _create_karaoke_tags(self, words: List[Dict[str, Any]]) -> str:
        """
        为一行单词创建卡拉OK标签

        Args:
            words: 单词列表（带时间戳）

        Returns:
            带\\k标签的ASS格式文本
        """
        if not words:
            return ""

        result = []

        for word in words:
            # 计算持续时间（厘秒，1秒=100厘秒）
            duration_ms = word["end"] - word["start"]
            duration_cs = max(1, duration_ms // 10)  # 至少1厘秒

            # 生成\\k标签
            karaoke_tag = self.style.get_karaoke_tags(duration_cs)

            # 添加单词和空格
            result.append(f"{karaoke_tag}{word['word']}")

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

        # 设置样式（使用SSAStyle对象）
        style_name = STYLE_NAMES.get(self.style.name.split()[0].lower(), "Default")
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

        # 设置样式（使用SSAStyle对象）
        style_name = STYLE_NAMES.get(self.style.name.split()[0].lower(), "Default")
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
                             max_line_duration_ms: int = 5000) -> SSAFile:
    """
    便捷函数：创建卡拉OK字幕

    Args:
        subs: 输入的SSAFile对象（来自whisper-timestamped）
        style_name: 样式名称 (classic, modern, neon, elegant, anime)
        words_per_line: 每行显示的单词数 (1-20)
        max_line_duration_ms: 每行最大持续时间（毫秒）

    Returns:
        带卡拉OK效果的SSAFile对象
    """
    generator = KaraokeGenerator(
        style_name=style_name,
        words_per_line=words_per_line,
        max_line_duration_ms=max_line_duration_ms
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
