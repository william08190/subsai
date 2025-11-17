#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
卡拉OK批量视频处理器
Karaoke Batch Video Processor

This module provides batch processing capabilities for generating karaoke videos.
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from subsai import SubsAI, Tools
from subsai.karaoke_generator import KaraokeGenerator
from subsai.karaoke_styles import get_all_styles

__author__ = "Claude Code Assistant"
__copyright__ = "Copyright 2025"
__license__ = "GPLv3"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class KaraokeBatchProcessor:
    """
    卡拉OK批量视频处理器

    支持批量处理视频文件，生成卡拉OK字幕并烧录到视频中
    """

    # 支持的视频格式
    SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm']

    def __init__(self,
                 model_name: str = "linto-ai/whisper-timestamped",
                 model_config: Optional[Dict[str, Any]] = None,
                 style_name: str = "classic",
                 words_per_line: int = 10,
                 max_workers: int = 1):
        """
        初始化批量处理器

        Args:
            model_name: Whisper模型名称
            model_config: 模型配置（如果为None，使用默认配置）
            style_name: 卡拉OK样式名称
            words_per_line: 每行单词数
            max_workers: 最大并行处理数（建议设为1，避免显存不足）
        """
        self.model_name = model_name
        self.model_config = model_config or self._get_default_config()
        self.style_name = style_name
        self.words_per_line = words_per_line
        self.max_workers = max_workers

        self.subs_ai = SubsAI()
        self.tools = Tools()

        logger.info(f"初始化批量处理器: 模型={model_name}, 样式={style_name}")

    def _get_default_config(self) -> Dict[str, Any]:
        """
        获取默认的whisper-timestamped配置

        Returns:
            默认配置字典
        """
        return {
            "model_type": "large-v3-turbo",
            "segment_type": "word",
            "device": None,
            "download_root": None,
            "in_memory": False,
            "verbose": False,
            "compression_ratio_threshold": 2.4,
            "logprob_threshold": -1.0,
            "no_speech_threshold": 0.6,
            "condition_on_previous_text": True,
            "task": "transcribe",
            "language": None,
            "sample_len": None,
            "best_of": None,
            "beam_size": None,
            "patience": None,
            "length_penalty": None,
            "suppress_tokens": "-1",
            "fp16": True,
            "remove_punctuation_from_words": True,
            "refine_whisper_precision": 0.5,
            "min_word_duration": 0.04,
            "plot_word_alignment": False,
            "seed": 1234,
            "vad": False,
            "detect_disfluencies": False,
            "trust_whisper_timestamps": True,
            "naive_approach": False
        }

    def scan_videos(self, input_dir: str) -> List[Path]:
        """
        扫描输入目录中的视频文件

        Args:
            input_dir: 输入目录路径

        Returns:
            视频文件路径列表
        """
        input_path = Path(input_dir)

        if not input_path.exists():
            logger.error(f"输入目录不存在: {input_dir}")
            return []

        video_files = []

        for ext in self.SUPPORTED_VIDEO_FORMATS:
            video_files.extend(input_path.glob(f"*{ext}"))
            video_files.extend(input_path.glob(f"*{ext.upper()}"))

        logger.info(f"扫描到 {len(video_files)} 个视频文件")
        return sorted(video_files)

    def process_single_video(self,
                            video_path: Path,
                            output_dir: str,
                            progress_callback: Optional[Callable[[str, float], None]] = None) -> Dict[str, Any]:
        """
        处理单个视频文件

        Args:
            video_path: 视频文件路径
            output_dir: 输出目录路径
            progress_callback: 进度回调函数 callback(message, progress_percent)

        Returns:
            处理结果字典 {"success": bool, "output_file": str, "error": str}
        """
        result = {
            "success": False,
            "video_file": str(video_path),
            "output_file": None,
            "error": None
        }

        try:
            logger.info(f"开始处理: {video_path.name}")

            # 1. 转录生成词级字幕
            if progress_callback:
                progress_callback(f"正在转录: {video_path.name}", 10)

            logger.info(f"  [1/3] 转录视频...")
            model = self.subs_ai.create_model(self.model_name, model_config=self.model_config)
            subs = self.subs_ai.transcribe(media_file=str(video_path), model=model)

            if not subs or len(subs) == 0:
                raise Exception("转录失败，未生成字幕")

            logger.info(f"  转录完成，生成 {len(subs)} 个字幕事件")

            # 2. 转换为卡拉OK格式
            if progress_callback:
                progress_callback(f"生成卡拉OK字幕: {video_path.name}", 40)

            logger.info(f"  [2/3] 生成卡拉OK字幕...")
            generator = KaraokeGenerator(
                style_name=self.style_name,
                words_per_line=self.words_per_line
            )
            karaoke_subs = generator.generate(subs)

            if not karaoke_subs or len(karaoke_subs) == 0:
                raise Exception("卡拉OK字幕生成失败")

            logger.info(f"  生成 {len(karaoke_subs)} 个卡拉OK字幕事件")

            # 3. 保存ASS字幕文件
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            ass_file = output_path / f"{video_path.stem}_karaoke.ass"
            karaoke_subs.save(str(ass_file))
            logger.info(f"  ASS字幕保存至: {ass_file}")

            # 4. 烧录字幕到视频（使用专用卡拉OK烧录方法）
            if progress_callback:
                progress_callback(f"烧录字幕到视频: {video_path.name}", 70)

            logger.info(f"  [3/3] 烧录字幕到视频...")
            output_video = str(output_path / f"{video_path.stem}_karaoke{video_path.suffix}")

            merged_video = self.tools.burn_karaoke_subtitles(
                subs=karaoke_subs,
                media_file=str(video_path),
                output_filename=output_video.replace(video_path.suffix, '')
            )

            if progress_callback:
                progress_callback(f"完成: {video_path.name}", 100)

            result["success"] = True
            result["output_file"] = merged_video
            logger.info(f"✅ 处理完成: {merged_video}")

        except Exception as e:
            error_msg = f"处理失败: {str(e)}"
            logger.error(f"❌ {video_path.name} - {error_msg}")
            result["error"] = error_msg

            if progress_callback:
                progress_callback(f"失败: {video_path.name}", -1)

        return result

    def process_batch(self,
                     input_dir: str,
                     output_dir: str,
                     progress_callback: Optional[Callable[[str, int, int], None]] = None) -> List[Dict[str, Any]]:
        """
        批量处理视频

        Args:
            input_dir: 输入目录路径
            output_dir: 输出目录路径
            progress_callback: 进度回调函数 callback(message, current, total)

        Returns:
            处理结果列表
        """
        # 扫描视频文件
        video_files = self.scan_videos(input_dir)

        if not video_files:
            logger.warning("未找到视频文件")
            return []

        total_videos = len(video_files)
        results = []

        logger.info(f"开始批量处理 {total_videos} 个视频文件")
        start_time = time.time()

        # 串行处理（避免显存不足）
        if self.max_workers == 1:
            for idx, video_path in enumerate(video_files, 1):
                if progress_callback:
                    progress_callback(f"处理 {video_path.name}", idx, total_videos)

                result = self.process_single_video(video_path, output_dir)
                results.append(result)

        # 并行处理（谨慎使用）
        else:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {
                    executor.submit(self.process_single_video, video_path, output_dir): video_path
                    for video_path in video_files
                }

                for idx, future in enumerate(as_completed(futures), 1):
                    video_path = futures[future]

                    if progress_callback:
                        progress_callback(f"处理 {video_path.name}", idx, total_videos)

                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        logger.error(f"处理异常: {video_path.name} - {e}")
                        results.append({
                            "success": False,
                            "video_file": str(video_path),
                            "output_file": None,
                            "error": str(e)
                        })

        # 统计结果
        elapsed_time = time.time() - start_time
        success_count = sum(1 for r in results if r["success"])
        fail_count = total_videos - success_count

        logger.info(f"\n{'='*60}")
        logger.info(f"批量处理完成!")
        logger.info(f"  总计: {total_videos} 个视频")
        logger.info(f"  成功: {success_count} 个")
        logger.info(f"  失败: {fail_count} 个")
        logger.info(f"  耗时: {elapsed_time:.2f} 秒")
        logger.info(f"{'='*60}\n")

        return results

    def generate_report(self, results: List[Dict[str, Any]], output_dir: str) -> str:
        """
        生成处理报告

        Args:
            results: 处理结果列表
            output_dir: 输出目录路径

        Returns:
            报告文件路径
        """
        report_file = Path(output_dir) / "karaoke_batch_report.json"

        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_videos": len(results),
            "success_count": sum(1 for r in results if r["success"]),
            "fail_count": sum(1 for r in results if not r["success"]),
            "model_name": self.model_name,
            "style_name": self.style_name,
            "results": results
        }

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        logger.info(f"处理报告已保存: {report_file}")
        return str(report_file)


def batch_process_videos(input_dir: str,
                         output_dir: str,
                         config_file: Optional[str] = None,
                         style_name: str = "classic",
                         words_per_line: int = 10) -> List[Dict[str, Any]]:
    """
    便捷函数：批量处理视频

    Args:
        input_dir: 输入目录路径
        output_dir: 输出目录路径
        config_file: 配置文件路径（JSON格式）
        style_name: 卡拉OK样式名称
        words_per_line: 每行单词数

    Returns:
        处理结果列表
    """
    # 加载配置
    model_config = None
    if config_file and Path(config_file).exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            model_config = json.load(f)
        logger.info(f"已加载配置文件: {config_file}")

    # 创建处理器
    processor = KaraokeBatchProcessor(
        model_name="linto-ai/whisper-timestamped",
        model_config=model_config,
        style_name=style_name,
        words_per_line=words_per_line,
        max_workers=1
    )

    # 批量处理
    results = processor.process_batch(input_dir, output_dir)

    # 生成报告
    processor.generate_report(results, output_dir)

    return results


if __name__ == '__main__':
    # 测试代码
    import sys

    if len(sys.argv) < 3:
        print("用法: python karaoke_batch.py <输入目录> <输出目录> [配置文件]")
        sys.exit(1)

    input_directory = sys.argv[1]
    output_directory = sys.argv[2]
    config_path = sys.argv[3] if len(sys.argv) > 3 else None

    print(f"\n🎵 卡拉OK批量视频处理器 🎵")
    print(f"输入目录: {input_directory}")
    print(f"输出目录: {output_directory}")
    print(f"配置文件: {config_path or '使用默认配置'}\n")

    batch_process_videos(
        input_dir=input_directory,
        output_dir=output_directory,
        config_file=config_path,
        style_name="classic",
        words_per_line=10
    )

    print("\n✅ 批量处理完成!")
