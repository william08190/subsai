# 视频唯一性增强系统 - 快速开始

## 🎯 功能概述

解决的核心问题：
- ✅ 输出视频分辨率低 → 自动升级到1080p+
- ✅ 视频元数据高度一致 → 元数据随机化和清理
- ✅ 视频指纹相似 → 多维度差异化处理
- ✅ 平台批量检测 → 有效规避YouTube/TikTok限流

## 📦 基础使用

### 单个视频处理

```python
from subsai import Tools
from subsai.karaoke_generator import create_karaoke_subtitles
import pysubs2

# 1. 加载字幕
subs = pysubs2.load('your_subtitles.srt')

# 2. 生成卡拉OK字幕
karaoke_subs = create_karaoke_subtitles(subs, style_name='modern')

# 3. 烧录到视频（全自动增强）
output = Tools.burn_karaoke_subtitles(
    karaoke_subs,
    'input.mp4',
    'output_enhanced',
    aspect_ratio='9:16',      # 适配短视频
    min_resolution=1080,      # 确保1080p+
    enable_uniqueness=True    # 启用唯一性（默认）
)

print(f"✅ 完成: {output}")
```

### 批量处理（确保每个视频都不同）

```python
import glob

video_files = glob.glob('input/*.mp4')

for index, video_file in enumerate(video_files):
    subs = pysubs2.load(f'subtitles/{index}.srt')
    karaoke_subs = create_karaoke_subtitles(subs, style_name='modern')

    # 关键：uniqueness_index 确保每个视频唯一
    output = Tools.burn_karaoke_subtitles(
        karaoke_subs,
        video_file,
        f'output_{index}',
        aspect_ratio='9:16',
        min_resolution=1080,
        enable_uniqueness=True,
        uniqueness_index=index  # 不同索引 = 不同指纹
    )

    print(f"✅ [{index+1}/{len(video_files)}] {output}")
```

## 🔧 参数说明

### 新增参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `min_resolution` | int | 1080 | 最小输出高度（像素），自动升级 |
| `enable_uniqueness` | bool | True | 启用视频唯一性处理 |
| `uniqueness_index` | int | 0 | 批量处理索引，确保差异化 |

### 原有参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `aspect_ratio` | str | None | 目标宽高比 (如 '9:16', '16:9') |
| `video_codec` | str | 'libx264' | 视频编码器 |
| `crf` | int | 18 | 质量控制（启用唯一性时会被覆盖） |
| `preset` | str | 'medium' | 编码预设（启用唯一性时会被覆盖） |

## 🎲 唯一性处理细节

### 自动随机化的参数

当 `enable_uniqueness=True` 时，系统会自动：

1. **编码参数随机化**
   - CRF: 15-19 (随机选择，都是高质量)
   - 预设: slow/slower/veryslow (随机)
   - x264参数: me/subme/ref (微调)

2. **视觉微调**（肉眼不可见但改变指纹）
   - 饱和度: ±2%
   - 亮度: ±1.5%
   - 对比度: ±1%
   - 噪声: 0.08%-0.25%

3. **音频差异化**
   - 比特率: 192k/224k/256k (随机)
   - 采样率: 44.1kHz/48kHz (随机)

4. **元数据随机化**
   - 创建时间: 过去1-30天内随机
   - 编码器版本: 5种Lavf版本随机
   - 清空: 标题、注释等原始信息

## 📊 效果对比

### 禁用唯一性（传统方式）

```
Video 1: MD5=abc123... (元数据相同, CRF=18, preset=medium)
Video 2: MD5=abc456... (元数据相同, CRF=18, preset=medium)
Video 3: MD5=abc789... (元数据相同, CRF=18, preset=medium)

❌ 平台识别为批量生成，限流
```

### 启用唯一性（新方式）

```
Video 1: MD5=xyz111...
  - 2025-01-15 14:23, Lavf60.3.100
  - CRF=16, slower, sat=1.01, noise=0.0015

Video 2: MD5=xyz222...
  - 2025-01-08 09:17, Lavf59.27.100
  - CRF=18, slow, sat=0.99, noise=0.0021

Video 3: MD5=xyz333...
  - 2025-01-22 19:45, Lavf60.16.100
  - CRF=17, veryslow, sat=1.02, noise=0.0009

✅ 每个视频独特，平台正常推荐
```

## 🔍 验证输出

### 检查分辨率

```bash
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height output.mp4
```

### 检查元数据

```bash
ffprobe -v error -show_entries format_tags output.mp4
```

### 检查编码参数

```bash
ffprobe -v error -select_streams v:0 \
  -show_entries stream=codec_name,profile output.mp4
```

## ⚙️ 高级用法

### 禁用唯一性处理

如果你想要完全一致的输出：

```python
output = Tools.burn_karaoke_subtitles(
    karaoke_subs,
    'input.mp4',
    'output',
    crf=18,                   # 固定CRF
    preset='slow',            # 固定预设
    enable_uniqueness=False   # 禁用唯一性
)
```

### 自定义最小分辨率

```python
output = Tools.burn_karaoke_subtitles(
    karaoke_subs,
    'input.mp4',
    'output',
    min_resolution=1440,  # 2K分辨率
    enable_uniqueness=True
)
```

## 📝 性能影响

- **编码时间**: +5-15% (因slower/veryslow预设)
- **文件大小**: 基本相同 (CRF 15-19都是高质量)
- **视觉质量**: 无损 (微调肉眼不可见)
- **平台效果**: 显著降低批量检测概率

## ❓ 常见问题

**Q: 会影响视频质量吗？**
A: 不会。所有参数都在高质量范围内，微调幅度肉眼不可见。

**Q: 编码时间会延长吗？**
A: 会延长5-15%，因为使用了更慢但质量更高的预设。

**Q: 如何验证唯一性？**
A: 使用ffprobe查看元数据，或用perceptual hash工具检测指纹。

**Q: 保证100%不被检测吗？**
A: 无法100%保证，但大幅降低被识别概率。建议结合其他差异化手段（如不同内容、音乐等）。

## 📚 相关文档

- 完整文档: `VIDEO_UNIQUENESS_UPGRADE.md`
- 实现指南: `IMPLEMENTATION_GUIDE.md`
- 核心模块: `src/subsai/video_uniqueness.py`
- 测试脚本: `test_uniqueness.py`

## 🚀 开始使用

1. 确保已安装项目依赖
2. 准备你的视频和字幕文件
3. 参考上面的代码示例
4. 运行并验证输出

祝使用愉快！🎉
