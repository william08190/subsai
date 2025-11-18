# WebUI卡拉OK功能使用指南

## 修复状态
✅ **卡拉OK字幕烧录功能已修复并可用**

## 访问WebUI
http://localhost:8501

## 使用步骤

### 1. 打开WebUI
在浏览器中访问 http://localhost:8501

### 2. 上传视频
在页面上传您的视频文件（支持mp4, webm, mkv等格式）

### 3. 选择转录模型
- 推荐使用 `openai/whisper`
- 模型类型选择 `tiny` 或 `base`（更快）
- 对于中文视频，选择 `medium` 或 `large`（更准确）

### 4. 生成字幕
点击 "Transcribe" 按钮生成字幕

### 5. 生成卡拉OK视频
1. 在转录结果下方找到 "Generate Karaoke Video" 按钮
2. 选择卡拉OK样式（默认: `classic`）
3. 点击生成按钮

### 6. 下载结果
生成完成后会出现下载链接，下载卡拉OK视频文件

## 技术细节

### 修复内容
1. **ffmpeg路径**: 使用系统ffmpeg (`/usr/bin/ffmpeg`) 而非conda ffmpeg
2. **支持的编码器**: libx264 (H.264视频编码)
3. **字幕滤镜**: libass subtitles滤镜 (ASS格式字幕烧录)
4. **卡拉OK效果**: ASS格式的`\k`标签用于逐字高亮效果

### 卡拉OK样式
目前支持的样式：
- `classic`: 经典样式，白色字体，黑色描边
- 更多样式可在代码中添加

### 输出格式
- **视频编码**: H.264 (libx264)
- **音频编码**: 原音频直接复制（无重新编码）
- **字幕**: 硬编码到视频画面（无法关闭）
- **质量**: CRF=23 (高质量)

## 故障排除

### 如果卡拉OK生成失败

1. **检查容器状态**
   ```bash
   docker ps
   # 应该看到 subsai-webui 容器在运行
   ```

2. **查看日志**
   ```bash
   docker logs subsai-webui --tail 100
   ```

3. **重启容器**
   ```bash
   cd D:\Downloads\Claude\subsai-karaoke
   docker compose restart
   ```

4. **验证ffmpeg**
   ```bash
   docker exec subsai-webui /usr/bin/ffmpeg -version
   # 应该显示 ffmpeg version 4.2.7 并包含 --enable-libx264
   ```

### 如果字幕不显示

检查生成的ASS文件是否包含卡拉OK标签：
```bash
docker exec subsai-webui cat /path/to/subtitle.ass
# 应该看到类似 \k166Hello\k166world 的标签
```

## 测试用例

我们提供了完整的自动化测试：
```bash
# 在容器中运行测试
docker exec subsai-webui python /tmp/test_final.py
```

测试视频: `/tmp/test_video.mp4`
测试输出: `/tmp/final_test_karaoke.mp4`

## 技术支持

- **测试报告**: 见 `KARAOKE_TEST_REPORT.md`
- **测试脚本**: 见 `test_final.py`
- **验证截图**: 见 `karaoke_frame.jpg`

## 注意事项

1. **视频时长**: 长视频处理时间较长，请耐心等待
2. **内存使用**: 转录大视频需要较多内存
3. **GPU加速**: 当前容器支持CPU模式，GPU加速需要NVIDIA显卡
4. **字幕语言**: Whisper自动检测语言，支持100+种语言

## 已知限制

1. **字幕精度**: 取决于Whisper模型大小和音频质量
2. **卡拉OK同步**: 基于字幕时间戳，逐字时间均分
3. **样式自定义**: 当前仅支持预设样式

## 更新日志

### 2025-11-18
- ✅ 修复ffmpeg编码器问题
- ✅ 添加系统ffmpeg支持
- ✅ 修复卡拉OK字幕生成
- ✅ 完成自动化测试
- ✅ 更新Docker镜像
