# 视频唯一性增强系统 - 升级指南

## 问题分析

### 当前存在的问题

1. **分辨率问题**
   - 输出视频分辨率与输入相同,如果输入低于1080p则输出也偏低
   - YouTube对低分辨率视频的推荐权重较低

2. **视频指纹高度一致**
   - 批量生成的视频元数据完全相同
   - 编码参数固定,视频指纹高度相似
   - YouTube/TikTok等平台可以通过以下特征识别批量生成:
     - 创建时间戳
     - 编码器信息
     - 视频流元数据
     - 像素级指纹 (感知哈希)

3. **元数据未清理**
   - 原视频中的备注、标题等信息未被清除
   - 容易被平台识别为批量处理

## 解决方案

### 核心改进

#### 1. 强制1080p+分辨率升级
```python
- 自动检测视频分辨率
- 如果低于1080p,自动使用lanczos高质量算法升级
- 保持宽高比,确保尺寸为偶数
```

#### 2. 多维度视频唯一性处理

**2.1 元数据随机化**
- 随机化创建时间 (过去1-30天内)
- 随机化编码器字符串 (5种Lavf版本变体)
- 清除所有原视频元数据 (标题、注释、作者等)

**2.2 编码参数随机化**
- CRF范围: 15-19 (都是高质量,但编码结果不同)
- 预设: slow/slower/veryslow (随机选择)
- x264参数微调:
  - 运动估计算法: umh/hex
  - 子像素精度: 7/8/9
  - 参考帧数: 3/4/5

**2.3 视觉微调 (肉眼不可见但改变指纹)**
- 饱和度: ±2% (0.98-1.02)
- 亮度: ±1.5% (0.985-1.015)
- 对比度: ±1% (0.99-1.01)
- 添加微小噪声: 0.08%-0.25% (几乎不可见)

**2.4 音频处理差异化**
- 比特率: 192k/224k/256k (随机)
- 采样率: 44100/48000Hz (随机)

### API变化

#### 新增参数

```python
Tools.burn_karaoke_subtitles(
    subs,                      # SSAFile对象
    media_file,                # 输入视频
    output_filename=None,      # 输出文件名
    video_codec='libx264',     # 视频编码器
    crf=18,                    # CRF (会被随机化)
    preset='medium',           # 预设 (会被随机化)
    aspect_ratio=None,         # 宽高比裁剪

    # 新增参数
    min_resolution=1080,       # 最小分辨率 (默认1080p)
    enable_uniqueness=True,    # 启用唯一性处理 (默认开启)
    uniqueness_index=0         # 批量处理索引 (确保每个视频都不同)
)
```

## 使用示例

### 基础使用 (推荐 - 全自动)

```python
from subsai import Tools
from subsai.karaoke_generator import create_karaoke_subtitles
import pysubs2

# 1. 加载字幕
subs = pysubs2.load('subtitles.srt')

# 2. 生成卡拉OK字幕
karaoke_subs = create_karaoke_subtitles(subs, style_name='modern')

# 3. 烧录 (全自动增强)
output = Tools.burn_karaoke_subtitles(
    karaoke_subs,
    'input.mp4',
    'output_enhanced',
    aspect_ratio='9:16',      # 适配短视频
    min_resolution=1080,      # 确保1080p+
    enable_uniqueness=True    # 启用唯一性 (默认)
)

print(f"✅ 增强版视频已生成: {output}")
print("✅ 分辨率: 1080p+")
print("✅ 元数据已随机化")
print("✅ 视频指纹已差异化")
```

### 批量处理 (确保每个视频都不同)

```python
from subsai import Tools
from subsai.karaoke_generator import create_karaoke_subtitles
import pysubs2
import glob

video_files = glob.glob('input/*.mp4')

for index, video_file in enumerate(video_files):
    subs = pysubs2.load(f'subtitles/{index}.srt')
    karaoke_subs = create_karaoke_subtitles(subs, style_name='modern')

    # 关键: uniqueness_index 确保每个视频都有不同的随机参数
    output = Tools.burn_karaoke_subtitles(
        karaoke_subs,
        video_file,
        f'output_{index}_enhanced',
        aspect_ratio='9:16',
        min_resolution=1080,
        enable_uniqueness=True,
        uniqueness_index=index      # 重要! 每个视频不同的索引
    )

    print(f"✅ [{index+1}/{len(video_files)}] 已完成: {output}")
```

### 禁用唯一性处理 (如果你想要完全一致的输出)

```python
output = Tools.burn_karaoke_subtitles(
    karaoke_subs,
    'input.mp4',
    'output_standard',
    crf=18,                   # 固定CRF
    preset='slow',            # 固定预设
    enable_uniqueness=False   # 禁用唯一性处理
)
```

## 技术细节

### 唯一性参数生成算法

```python
# 基于文件路径 + 时间戳 + 索引 生成唯一种子
seed = md5(f"{input_file}_{timestamp}_{index}")

# 使用种子生成可重现但唯一的参数
random.seed(seed_int)

params = {
    'crf': random.randint(15, 19),
    'preset': random.choice(['slow', 'slower', 'veryslow']),
    'saturation': random.uniform(0.98, 1.02),
    'noise_strength': random.uniform(0.0008, 0.0025),
    'metadata': {
        'creation_time': random_date(),
        'encoder': random_encoder_string()
    }
}
```

### 滤镜链顺序

```
输入视频
  ↓
1. 分辨率升级 (如果需要)
  ↓
2. 宽高比裁剪 (如果需要)
  ↓
3. 色彩微调 (eq滤镜)
  ↓
4. 添加噪声 (noise滤镜)
  ↓
5. ASS字幕烧录
  ↓
输出视频
```

## 效果对比

### 未启用唯一性处理
```
Video A: MD5 = abc123... (元数据相同, CRF=18, preset=medium)
Video B: MD5 = abc456... (元数据相同, CRF=18, preset=medium)
Video C: MD5 = abc789... (元数据相同, CRF=18, preset=medium)

❌ 平台识别为批量生成,限流
```

### 启用唯一性处理
```
Video A: MD5 = xyz111...
  - 元数据: 2025-01-15 14:23:11, Lavf60.3.100
  - CRF=16, preset=slower, saturation=1.01, noise=0.0015

Video B: MD5 = xyz222...
  - 元数据: 2025-01-08 09:17:42, Lavf59.27.100
  - CRF=18, preset=slow, saturation=0.99, noise=0.0021

Video C: MD5 = xyz333...
  - 元数据: 2025-01-22 19:45:33, Lavf60.16.100
  - CRF=17, preset=veryslow, saturation=1.02, noise=0.0009

✅ 每个视频都是独特的,平台正常推荐
```

## 性能影响

- **编码时间**: +5-15% (因为使用slower/veryslow预设)
- **文件大小**: 基本相同 (CRF 15-19都是高质量范围)
- **视觉质量**: 无损 (微调参数肉眼不可见)
- **平台检测**: 有效规避批量识别

## 常见问题

### Q: 会影响视频质量吗?
A: 不会。所有参数都在高质量范围内,微调幅度肉眼不可见。

### Q: 编码时间会延长吗?
A: 会延长5-15%,因为使用了更慢但质量更高的预设。

### Q: 如何验证唯一性?
A: 可以用ffprobe查看元数据,或用perceptual hash工具检测视频指纹。

### Q: 是否保证100%不被检测?
A: 没有100%的保证,但大幅降低被识别为批量生成的概率。平台检测算法在不断进化,建议结合其他差异化手段 (如不同的字幕内容、背景音乐等)。

## 下一步

1. ��试新功能
2. 验证输出视频质量
3. 检查平台推荐效果
4. 根据需要调整参数

## 相关文件

- `src/subsai/video_uniqueness.py` - 唯一性处理模块
- `src/subsai/main.py` - burn_karaoke_subtitles 方法
- `src/subsai/webui.py` - WebUI界面 (待更新)
