# 卡拉OK字体大小调节功能使用指南

## 功能概述

现在您可以自由调节卡拉OK字幕的字体大小，解决字幕过大超出视频范围的问题！

## 使用方法

### WebUI界面操作

1. **打开WebUI**: 访问 http://localhost:8501

2. **转录视频**: 先使用Whisper转录功能生成字幕

3. **展开卡拉OK功能**: 点击 "🎤 Generate Karaoke Video (NEW)"

4. **启用自定义字体大小**:
   - 勾选 "**Custom Font Size**" 复选框
   - 如果不勾选，将使用样式的���认字体大小

5. **调节字体大小**:
   - 使用滑块选择字体大小（20-100像素）
   - 推荐值：
     - **小字幕**: 20-30像素
     - **中等字幕**: 30-40像素（推荐）
     - **默认字幕**: 44-52像素（各样式默认值）
     - **大字幕**: 60-80像素

6. **选择其他参数**:
   - 卡拉OK样式
   - 每行单词数

7. **生成视频**: 点击 "🎤 Generate Karaoke Video"

## 各样式默认字体大小

| 样式 | 默认字体大小 | 特点 |
|------|--------------|------|
| Classic | 48px | 传统KTV黄色高亮 |
| Modern | 52px | 现代简约橙色渐变 |
| Neon | 50px | 赛博朋克紫红色 |
| Elegant | 46px | 优雅金色柔和 |
| Anime | 44px | 动漫青色描边 |

## 推荐设置

### 竖屏视频 (手机视频)
- 分辨率: 480x832, 720x1280
- 推荐字体大小: **28-36像素**
- 每行单词数: 6-8

### 横屏视频 (标准视频)
- 分辨率: 1920x1080
- 推荐字体大小: **40-50像素**（或使用默认）
- 每行单词数: 10-12

### 方形视频 (Instagram/抖音)
- 分辨率: 1080x1080
- 推荐字体大小: **32-40像素**
- 每行单词数: 8-10

## 程序化使用（Python API）

```python
from subsai import SubsAI, Tools
from subsai.karaoke_generator import create_karaoke_subtitles

# 1. 转录视频
subs_ai = SubsAI()
model = subs_ai.create_model('openai/whisper', {'model_type': 'base'})
subs = subs_ai.transcribe('video.mp4', model)

# 2. 生成卡拉OK字幕（自定义字体大小）
karaoke_subs = create_karaoke_subtitles(
    subs=subs,
    style_name='classic',
    words_per_line=10,
    fontsize=32  # 自定义字体大小（像素）
)

# 3. 烧录到视频
tools = Tools()
output = tools.burn_karaoke_subtitles(
    subs=karaoke_subs,
    media_file='video.mp4',
    output_filename='video-karaoke'
)

print(f"输出: {output}")
```

## 故障排除

### 字幕仍然太大
- 尝试将字体大小减小到 24-28像素
- 减少每行单词数（例如 6-8）

### 字幕太小看不清
- 增加字体大小到 50-60像素
- 选择粗边框样式（Neon, Anime）

### 字幕超出视频底部
- 减小字体大小
- 或选择顶部/中部对齐的样式（Modern顶部，Neon中部）

### 字幕换行过多
- 增加每行单词数
- 减小字体大小

## 技术细节

### 代码实现

**样式类**支持自定义字体大小:
```python
style = ClassicStyle(fontsize=36)  # 自定义36像素
style = ClassicStyle()  # 使用默认48像素
```

**生成器**接受字体大小参数:
```python
generator = KaraokeGenerator(
    style_name='classic',
    words_per_line=10,
    fontsize=36  # 可选参数
)
```

### ASS字幕格式

字体大小直接影响ASS样式定义:
```
Style: Classic,Microsoft YaHei,36,&H00FFFFFF,&H0000FFFF,...
                               ^^
                          字体大小（像素）
```

## 更新日志

### 2025-11-18
- ✅ 添加字体大小调节功能
- ✅ WebUI支持自定义字体大小
- ✅ 所有5种样式支持动态字体大小
- ✅ Python API支持fontsize参数
- ✅ 提供推荐设置指南

## 常见问题

**Q: 为什么不勾选"Custom Font Size"时没有滑块？**
A: 这是设计行为。不勾选时使用样式默认值，勾选后才显示滑块。

**Q: 字体大小范围为什么是20-100？**
A: 这是合理范围。小于20难以阅读，大于100在大多数视频中会超出范围。

**Q: 能否针对不同行设置不同字体大小？**
A: 当前版本不支持。整个卡拉OK视频使用统一字体大小。

**Q: 修改字体大小是否影响卡拉OK效果？**
A: 不影响。`\k`标签效果独立于字体大小，只是字体显示更大或更小。

## 联系支持

如有问题，请查看:
- **测试报告**: `KARAOKE_TEST_REPORT.md`
- **使用指南**: `WEBUI_KARAOKE_GUIDE.md`
- **GitHub Issues**: https://github.com/abdeladim-s/subsai/issues
