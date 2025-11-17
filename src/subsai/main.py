#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SubsAI: Subtitles AI
Subtitles generation tool powered by OpenAI's Whisper and its variants.

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <https://www.gnu.org/licenses/>.
"""

import os
import pathlib
import tempfile
from typing import Union, Dict

import ffmpeg
import pysubs2
from dl_translate import TranslationModel
from pysubs2 import SSAFile
from subsai.configs import AVAILABLE_MODELS
from subsai.models.abstract_model import AbstractModel
from ffsubsync.ffsubsync import run, make_parser
from subsai.utils import available_translation_models

__author__ = "abdeladim-s"
__contact__ = "https://github.com/abdeladim-s"
__copyright__ = "Copyright 2023,"
__license__ = "GPLv3"
__github__ = "https://github.com/abdeladim/subsai"


class SubsAI:
    """
    Subs AI class

    Example usage:
    ```python
    file = './assets/test1.mp4'
    subs_ai = SubsAI()
    model = subs_ai.create_model('openai/whisper', {'model_type': 'base'})
    subs = subs_ai.transcribe(file, model)
    subs.save('test1.srt')
    ```
    """

    @staticmethod
    def available_models() -> list:
        """
        Returns the supported models

        :return: list of available models
        """
        return list(AVAILABLE_MODELS.keys())

    @staticmethod
    def model_info(model: str) -> dict:
        """
        Returns general infos about the model (brief description and url)

        :param model: model name

        :return: dict of infos
        """
        return {'description': AVAILABLE_MODELS[model]['description'],
                'url': AVAILABLE_MODELS[model]['url']}

    @staticmethod
    def config_schema(model: str) -> dict:
        """
        Returns the configs associated with a model

        :param model: model name

        :return: dict of configs
        """
        return AVAILABLE_MODELS[model]['config_schema']

    @staticmethod
    def create_model(model_name: str, model_config: dict = {}) -> AbstractModel:
        """
        Returns a model instance

        :param model_name: the name of the model
        :param model_config: the configuration dict

        :return: the model instance
        """
        return AVAILABLE_MODELS[model_name]['class'](model_config)

    @staticmethod
    def transcribe(media_file: str, model: Union[AbstractModel, str], model_config: dict = {}) -> SSAFile:
        """
        Takes the model instance (created by :func:`create_model`) or the model name.
        Returns a :class:`pysubs2.SSAFile` <https://pysubs2.readthedocs.io/en/latest/api-reference.html#ssafile-a-subtitle-file>`_

        :param media_file: path of the media file (video/audio)
        :param model: model instance or model name
        :param model_config: model configs' dict

        :return: SSAFile: list of subtitles
        """
        if type(model) == str:
            stt_model = SubsAI.create_model(model, model_config)
        else:
            stt_model = model
        media_file = str(pathlib.Path(media_file).resolve())
        return stt_model.transcribe(media_file)


class Tools:
    """
    Some tools related to subtitles processing (ex: translation)
    """

    def __init__(self):
        pass

    @staticmethod
    def available_translation_models() -> list:
        """
        Returns available translation models
        A simple link to :func:`utils.available_translation_models` for easy access

        :return: list of available models
        """

        return available_translation_models()

    @staticmethod
    def available_translation_languages(model: Union[str, TranslationModel]) -> list:
        """
        Returns the languages supported by the translation model

        :param model: the name of the model
        :return: list of available languages
        """
        if type(model) == str:
            langs = Tools.create_translation_model(model).available_languages()
        else:
            langs = model.available_languages()
        return langs

    @staticmethod
    def create_translation_model(model_name: str = "m2m100", model_family: str = None) -> TranslationModel:
        """
        Creates and returns a translation model instance.

        :param model_name: name of the model. To get available models use :func:`available_translation_models`
        :param model_family: Either "mbart50" or "m2m100". By default, See `dl-translate` docs
        :return: A translation model instance
        """
        mt = TranslationModel(model_or_path=model_name, model_family=model_family)
        return mt

    @staticmethod
    def translate(subs: SSAFile,
                  source_language: str,
                  target_language: str,
                  model: Union[str, TranslationModel] = "m2m100",
                  model_family: str = None,
                  translation_configs: dict = {}) -> SSAFile:
        """
        Translates a subtitles `SSAFile` object, what :func:`SubsAI.transcribe` is returning

        :param subs: `SSAFile` object
        :param source_language: the language of the subtitles
        :param target_language: the target language
        :param model: the translation model, either an `str` or the model instance created by
                        :func:`create_translation_model`
        :param model_family: Either "mbart50" or "m2m100". By default, See `dl-translate` docs
        :param translation_configs: dict of translation configs (see :attr:`configs.ADVANCED_TOOLS_CONFIGS`)

        :return: returns an `SSAFile` subtitles translated to the target language
        """
        if type(model) == str:
            translation_model = Tools.create_translation_model(model_name=model, model_family=model_family)
        else:
            translation_model = model

        translated_subs = SSAFile()
        for sub in subs:
            translated_sub = sub.copy()
            translated_sub.text = translation_model.translate(text=sub.text,
                                                              source=source_language,
                                                              target=target_language,
                                                              batch_size=translation_configs[
                                                                  'batch_size'] if 'batch_size' in translation_configs else 32,
                                                              verbose=translation_configs[
                                                                  'verbose'] if 'verbose' in translation_configs else False)
            translated_subs.append(translated_sub)
        return translated_subs

    @staticmethod
    def auto_sync(subs: SSAFile,
                  media_file: str,
                  **kwargs
                  ) -> SSAFile:
        """
        Uses (ffsubsync)[https://github.com/smacke/ffsubsync] to auto-sync subtitles to the media file

        :param subs: `SSAFile` file
        :param media_file: path of the media_file
        :param kwargs: configs to pass to ffsubsync (see :attr:`configs.ADVANCED_TOOLS_CONFIGS`)

        :return: `SSAFile` auto-synced
        """
        parser = make_parser()
        srtin_file = tempfile.NamedTemporaryFile(delete=False)
        srtout_file = tempfile.NamedTemporaryFile(delete=False)
        try:
            srtin = srtin_file.name + '.ass'
            srtout = srtout_file.name + '.srt'
            subs.save(srtin)
            cmd = [media_file,
                   '-i', srtin,
                   '-o', srtout]
            for config_name in kwargs:
                value = kwargs[config_name]
                if value is None or value is False:
                    continue
                elif type(value) == bool and value is True:
                    cmd.append(f'--{config_name}')
                else:
                    cmd.append(f'--{config_name}')
                    cmd.append(f'{value}')
            parsed_args = parser.parse_args(cmd)
            retval = run(parsed_args)["retval"]
            synced_subs = pysubs2.load(srtout)
            return synced_subs
        finally:
            srtin_file.close()
            os.unlink(srtin_file.name)
            srtout_file.close()
            os.unlink(srtout_file.name)
    @staticmethod
    def merge_subs_with_video(subs: Dict[str, SSAFile],
                  media_file: str,
                  output_filename: str = None,
                  **kwargs
                  ) -> str:
        """
        Uses ffmpeg to merge subtitles into a video media file.
        You cna merge multiple subs at the same time providing a dict with (lang,`SSAFile` object) key,value pairs
        Example:
        ```python
            file = '../../assets/video/test1.webm'
            subs_ai = SubsAI()
            model = subs_ai.create_model('openai/whisper', {'model_type': 'tiny'})
            en_subs = subs_ai.transcribe(file, model)
            ar_subs = pysubs2.load('../../assets/video/test0-ar.srt')
            Tools.merge_subs_with_video({'English': subs, "Arabic": subs2}, file)
        ```

        :param subs: dict with (lang,`SSAFile` object) key,value pairs
        :param media_file: path of the video media_file
        :param output_filename: Output file name (without the extension as it will be inferred from the media file)

        :return: Absolute path of the output file
        """
        import logging
        logger = logging.getLogger(__name__)

        metadata = ffmpeg.probe(media_file, select_streams="v")['streams'][0]
        assert metadata['codec_type'] == 'video', f'File {media_file} is not a video'

        logger.info(f"🎬 开始合并字幕到视频: {media_file}")
        logger.info(f"📝 字幕语言数量: {len(subs)}")

        # 创建临时文件字典，存储文件路径而不是文件句柄
        srtin_files = {}
        for key in subs:
            # 创建临时文件并立即关闭，只保留路径
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False, encoding='utf-8')
            temp_file.close()
            srtin_files[key] = temp_file.name
            logger.info(f"📄 创建临时文件: {key} -> {temp_file.name}")

        try:
            in_file = pathlib.Path(media_file)
            if output_filename is not None:
                # 保持输入文件的扩展名
                out_file = in_file.parent / f"{output_filename}{in_file.suffix}"
            else:
                out_file = in_file.parent / f"{in_file.stem}-subs-merged{in_file.suffix}"

            video = str(in_file.resolve())

            # 检测视频编码器和容器格式
            video_codec = metadata['codec_name']
            logger.info(f"🎥 检测到视频编码器: {video_codec}")

            # 根据输入格式选择合适的字幕编码器
            # WebM使用webvtt,MP4使用mov_text
            if in_file.suffix.lower() in ['.webm', '.mkv']:
                # WebM/MKV容器使用webvtt字幕
                metadata_subs = {'scodec': 'webvtt'}
                logger.info(f"📦 WebM/MKV容器 -> 使用webvtt字幕")
            elif metadata['codec_name'] == 'h264':
                # H264视频使用mov_text字幕
                metadata_subs = {'scodec': 'mov_text'}
                logger.info(f"📦 H264视频 -> 使用mov_text字幕")
            else:
                # 其他格式，尝试使用srt
                metadata_subs = {}
                logger.info(f"📦 其他格式 -> 使用默认字幕编码")

            ffmpeg_subs_inputs = []

            for i, lang in enumerate(srtin_files):
                srtin = srtin_files[lang]

                # 保存字幕到临时文件
                logger.info(f"💾 保存字幕 '{lang}' 到: {srtin}")
                subs[lang].save(srtin)

                # 检查文件是否真的被写入
                if os.path.exists(srtin):
                    file_size = os.path.getsize(srtin)
                    logger.info(f"✅ 字幕文件已创建，大小: {file_size} 字节")

                    # 读取前100个字符用于调试
                    with open(srtin, 'r', encoding='utf-8') as f:
                        preview = f.read(100)
                        logger.info(f"📖 文件内容预览: {preview[:50]}...")
                else:
                    logger.error(f"❌ 字幕文件不存在: {srtin}")

                ffmpeg_subs_inputs.append(ffmpeg.input(srtin)['s'])
                metadata_subs[f'metadata:s:s:{i}'] = "title=" + lang

            output_file = str(out_file.resolve())
            input_ffmpeg = ffmpeg.input(video)
            input_video = input_ffmpeg['v']
            input_audio = input_ffmpeg['a']

            # 使用copy模式，不重新编码，保持原格式
            logger.info(f"✅ 使用copy模式，保持原视频音频格式")
            output_ffmpeg = ffmpeg.output(
                input_video, input_audio, *ffmpeg_subs_inputs, output_file,
                vcodec='copy',
                acodec='copy',
                **metadata_subs
            )
            output_ffmpeg = ffmpeg.overwrite_output(output_ffmpeg)

            # 打印ffmpeg命令用于调试
            cmd = ffmpeg.compile(output_ffmpeg)
            logger.info(f"🎬 执行ffmpeg命令: {' '.join(cmd)}")

            # 捕获ffmpeg输出
            try:
                stdout, stderr = ffmpeg.run(output_ffmpeg, capture_stdout=True, capture_stderr=True)
                logger.info(f"✅ ffmpeg执行成功")
                if stderr:
                    logger.debug(f"ffmpeg stderr: {stderr.decode('utf-8', errors='ignore')[-500:]}")
            except ffmpeg.Error as e:
                logger.error(f"❌ ffmpeg执行失败: {e.stderr.decode('utf-8', errors='ignore')}")
                raise

        finally:
            # 清理临时字幕文件
            for srtin_path in srtin_files.values():
                if os.path.exists(srtin_path):
                    logger.info(f"🗑️ 删除临时文件: {srtin_path}")
                    os.unlink(srtin_path)

        logger.info(f"🎉 字幕合并完成: {out_file.resolve()}")
        return str(out_file.resolve())

    @staticmethod
    def burn_karaoke_subtitles(subs: SSAFile,
                               media_file: str,
                               output_filename: str = None,
                               video_codec: str = 'libx264',
                               crf: int = 23) -> str:
        """
        Uses ffmpeg to burn ASS karaoke subtitles into video as hardcoded subtitles.
        This method preserves ASS karaoke effects (\k tags) by using the subtitles filter.

        Example:
        ```python
            from subsai import Tools
            from subsai.karaoke_generator import create_karaoke_subtitles

            # Generate karaoke subtitles
            karaoke_subs = create_karaoke_subtitles(original_subs, style_name='classic')

            # Burn to video
            output = Tools.burn_karaoke_subtitles(karaoke_subs, 'input.mp4', 'output_karaoke')
        ```

        :param subs: SSAFile object with ASS karaoke subtitles
        :param media_file: path of the video file
        :param output_filename: Output file name (without extension)
        :param video_codec: Video codec for encoding (default: libx264)
        :param crf: Constant Rate Factor for quality (default: 23, lower = better quality)

        :return: Absolute path of the output file
        """
        import logging
        logger = logging.getLogger(__name__)

        logger.info(f"🎤 开始烧录卡拉OK字幕: {media_file}")

        metadata = ffmpeg.probe(media_file, select_streams="v")['streams'][0]
        assert metadata['codec_type'] == 'video', f'File {media_file} is not a video'

        # Create temporary ASS file
        ass_temp = tempfile.NamedTemporaryFile(mode='w', suffix='.ass', delete=False, encoding='utf-8')

        try:
            # Save subtitles as ASS format to preserve karaoke effects
            logger.info(f"📄 创建临时ASS文件: {ass_temp.name}")
            subs.save(ass_temp.name)
            ass_temp.close()

            # 检查ASS文件
            if os.path.exists(ass_temp.name):
                file_size = os.path.getsize(ass_temp.name)
                logger.info(f"✅ ASS文件已创建，大小: {file_size} 字节")

                # 读取前200个字符用于调试
                with open(ass_temp.name, 'r', encoding='utf-8') as f:
                    preview = f.read(200)
                    logger.info(f"📖 ASS文件内容预览:\n{preview[:150]}...")
            else:
                logger.error(f"❌ ASS文件不存在: {ass_temp.name}")

            in_file = pathlib.Path(media_file)
            if output_filename is not None:
                out_file = in_file.parent / f"{output_filename}{in_file.suffix}"
            else:
                out_file = in_file.parent / f"{in_file.stem}-karaoke{in_file.suffix}"

            # Escape the ASS file path for ffmpeg (Windows paths need special handling)
            ass_path = ass_temp.name.replace('\\', '/').replace(':', '\\:')
            logger.info(f"🔧 转义后的ASS路径: {ass_path}")

            # Build ffmpeg command with subtitles filter
            input_video = ffmpeg.input(media_file)

            # Apply subtitles filter to burn ASS into video
            video_with_subs = input_video.video.filter('subtitles', ass_path)

            output_file = str(out_file.resolve())

            # Output with re-encoded video and copied audio
            output_ffmpeg = ffmpeg.output(
                video_with_subs,
                input_video.audio,
                output_file,
                vcodec=video_codec,
                crf=crf,
                acodec='copy',
                preset='medium'
            )

            output_ffmpeg = ffmpeg.overwrite_output(output_ffmpeg)

            # 打印ffmpeg命令
            cmd = ffmpeg.compile(output_ffmpeg)
            logger.info(f"🎬 执行ffmpeg命令: {' '.join(cmd)}")

            # 捕获ffmpeg输出
            try:
                stdout, stderr = ffmpeg.run(output_ffmpeg, capture_stdout=True, capture_stderr=True)
                logger.info(f"✅ ffmpeg执行成功")
                if stderr:
                    stderr_text = stderr.decode('utf-8', errors='ignore')
                    logger.debug(f"ffmpeg stderr (last 500 chars): {stderr_text[-500:]}")
            except ffmpeg.Error as e:
                error_text = e.stderr.decode('utf-8', errors='ignore')
                logger.error(f"❌ ffmpeg执行失败:\n{error_text}")
                raise

        finally:
            # Clean up temporary ASS file
            if os.path.exists(ass_temp.name):
                logger.info(f"🗑️ 删除临时ASS文件: {ass_temp.name}")
                os.unlink(ass_temp.name)

        logger.info(f"🎉 卡拉OK字幕烧录完成: {out_file.resolve()}")
        return str(out_file.resolve())

if __name__ == '__main__':
    file = '../../assets/video/test1.webm'
    subs_ai = SubsAI()
    model = subs_ai.create_model('openai/whisper', {'model_type': 'tiny'})
    subs = subs_ai.transcribe(file, model)
    subs.save('../../assets/video/test1.srt')
    subs2 = pysubs2.load('../../assets/video/test0-ar.srt')
    Tools.merge_subs_with_video({'English': subs, "Arabic": subs2}, file)
    # subs.save('test1.srt')
