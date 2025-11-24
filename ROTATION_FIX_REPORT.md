# 视频旋转元数据Bug修复报告

## 问题描述

**症状**：
- 输入视频 576x1024 → 输出视频 606x1080（错误❌）
- 输入视频 480x832 → 输出视频 1080x1872（正确✅）

**预期输出**：
- 576x1024 应该输出 1080x1920

## 根本原因

某些视频（特别是手机拍摄的竖屏视频）会在文件元数据中包含旋转信息：
- **存储尺寸**：1024x576 (横向)
- **旋转标记**：rotation=90°
- **实际显示**：576x1024 (竖向)

**旧代码问题**：
- 只读取 `metadata['width']` 和 `metadata['height']`
- 忽略了旋转元数据
- 导致使用错误的宽高进行缩放计算

## 修复方案

### 1. 添加旋转检测逻辑 (main.py:451-466)

```python
# Check for rotation metadata (common in mobile videos)
rotation = 0
if 'tags' in metadata:
    if 'rotate' in metadata['tags']:
        rotation = int(metadata['tags']['rotate'])
elif 'side_data_list' in metadata:
    for side_data in metadata['side_data_list']:
        if side_data.get('side_data_type') == 'Display Matrix' and 'rotation' in side_data:
            rotation = int(side_data['rotation'])
            break

# If video is rotated 90 or 270 degrees, swap width and height
if rotation in [90, -90, 270, -270]:
    original_width, original_height = original_height, original_width
    logger.info(f"🔄 检测到视频旋转 {rotation}°, 交换宽高")
```

### 2. 支持两种元数据格式

- **Format 1**: `metadata['tags']['rotate']` (常见于MP4)
- **Format 2**: `metadata['side_data_list'][]['rotation']` (Display Matrix)

### 3. 测试验证

**测试案例1** - 带旋转的视频：
```
输入元数据: width=1024, height=576, rotation=90
检测旋转 → 交换宽高
校正后尺寸: 576x1024
缩放输出: 1080x1920 ✅
```

**测试案例2** - 无旋转的视频：
```
输入元数据: width=576, height=1024, rotation=0
无需交换
校正后尺寸: 576x1024
缩放输出: 1080x1920 ✅
```

## 影响范围

✅ **修复的场景**：
- 手机竖屏拍摄的视频
- 带有旋转元数据的MP4/MOV文件
- iPhone/Android拍摄的短视频

✅ **不影响**：
- 正常横屏视频
- 已正确旋转的视频（rotation=0或180）
- 其他视频处理逻辑

## 提交信息

- **Commit**: b26b223
- **Message**: fix: 修复视频旋转元数据导致的宽高错误
- **Files Changed**: src/subsai/main.py

## 验证方法

```bash
# 1. 检查视频旋转信息
ffprobe -v quiet -select_streams v:0 -show_entries stream_tags=rotate -of default=noprint_wrappers=1 video.mp4

# 2. 处理测试
python -m subsai video.mp4 -o output.mp4

# 3. 检查输出尺寸
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 output.mp4
```

## 日志示例

**修复后的日志**：
```
📺 原始视频尺寸: 1024x576
🔄 检测到视频旋转 90°, 交换宽高
📺 原始视频尺寸: 576x1024
🔍 分辨率升级: 576x1024 -> 1080x1920
```

---

**修复完成时间**: 2025-11-24
**影响版本**: v1.2.0+
**状态**: ✅ 已验证并提交
