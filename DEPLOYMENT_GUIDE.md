# 🚀 subsai-karaoke v1.1.0 部署指南

[![版本](https://img.shields.io/badge/版本-v1.1.0-blue.svg)](https://github.com/william08190/subsai/releases/tag/v1.1.0)
[![许可证](https://img.shields.io/badge/许可证-GPLv3-green.svg)](./LICENSE)
[![平台](https://img.shields.io/badge/平台-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/william08190/subsai)

完整的跨平台部署指南，支持 Ubuntu、Windows 和 macOS。

---

## 📑 目录

- [快速开始](#快速开始)
- [部署方式对比](#部署方式对比)
- [方式一：Docker 部署（推荐）](#方式一docker-部署推荐)
- [方式二：本地安装](#方式二本地安装)
- [系统要求](#系统要求)
- [性能优化](#性能优化)
- [常见问题](#常见问题)
- [更新维护](#更新维护)

---

## 🎯 快速开始

### 最快部署方式（Docker）

```bash
# 1. 克隆仓库
git clone https://github.com/william08190/subsai.git
cd subsai

# 2. 一键启动（包含构建）
docker compose up -d

# 3. 访问 Web UI
# 打开浏览器访问 http://localhost:8501
```

**首次启动约需 5-10 分钟构建镜像，后续启动仅需几秒钟。**

---

## 🔄 部署方式对比

| 特性 | Docker 部署 | 本地安装 |
|-----|------------|---------|
| **跨平台兼容** | ✅ 完全一致 | ⚠️ 需平台适配 |
| **环境隔离** | ✅ 完全隔离 | ❌ 可能冲突 |
| **安装难度** | ⭐ 简单 | ⭐⭐⭐ 复杂 |
| **首次启动** | ⚠️ 需构建（5-10分钟） | ✅ 安装后即可 |
| **后续启动** | ✅ 秒级启动 | ✅ 秒级启动 |
| **更新维护** | ✅ 简单重构建 | ⚠️ 需手动更新 |
| **开发调试** | ⚠️ 需挂载卷 | ✅ 直接修改 |
| **GPU 支持** | ✅ 支持 | ✅ 支持 |
| **推荐场景** | 生产使用、快速部署 | 开发调试、深度定制 |

**推荐选择**：
- 🎯 **普通用户**：选择 Docker 部署
- 🛠️ **开发者**：选择本地安装
- 🚀 **生产环境**：选择 Docker + GPU

---

## 🐳 方式一：Docker 部署（推荐）

### 为什么选择 Docker？

- ✅ **一键部署**：无需手动配置环境
- ✅ **环境隔离**：不影响系统其他软件
- ✅ **跨平台**：Windows、Linux、macOS 完全一致
- ✅ **国内优化**：已配置阿里云镜像源和清华 pip 源
- ✅ **易于维护**：版本回滚、更新升级都很简单

### 1. 安装 Docker

#### Windows

1. **下载 Docker Desktop**
   https://www.docker.com/products/docker-desktop/

2. **安装并启动**
   - 双击安装包完成安装
   - 首次启动可能需要重启电脑
   - 建议启用 WSL2 后端（更快更稳定）

3. **验证安装**
   ```powershell
   docker --version
   docker compose version
   ```

#### Ubuntu/Debian Linux

```bash
# 更新软件包索引
sudo apt update

# 安装 Docker
sudo apt install -y docker.io docker-compose

# 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker

# 添加当前用户到 docker 组（避免每次 sudo）
sudo usermod -aG docker $USER

# 重新登录后验证
docker --version
docker compose version
```

#### macOS

1. **下载 Docker Desktop for Mac**
   https://www.docker.com/products/docker-desktop/

2. **安装并启动**
   - 拖拽到 Applications 文件夹
   - 启动 Docker Desktop
   - 等待 Docker 图标显示为运行状态

3. **验证安装**
   ```bash
   docker --version
   docker compose version
   ```

### 2. 部署应用

#### 2.1 克隆仓库

```bash
# 使用 HTTPS（推荐）
git clone https://github.com/william08190/subsai.git
cd subsai

# 或使用 SSH（需配置密钥）
git clone git@github.com:william08190/subsai.git
cd subsai
```

#### 2.2 配置目录映射（可选）

编辑 `docker-compose.yml` 修改输入/输出目录：

```yaml
volumes:
  # 输入视频目录（只读）
  - /your/input/path:/input:ro

  # 输出目录（读写）
  - /your/output/path:/output
```

**Windows 路径格式示例**：
```yaml
volumes:
  - C:/Users/YourName/Videos/Input:/input:ro
  - C:/Users/YourName/Videos/Output:/output
```

**Linux/macOS 路径格式示例**：
```yaml
volumes:
  - /home/username/videos/input:/input:ro
  - /home/username/videos/output:/output
```

#### 2.3 构建并启动

```bash
# 构建 Docker 镜像（首次需要 5-10 分钟）
docker compose build

# 启动服务（后台运行）
docker compose up -d

# 查看运行状态
docker compose ps

# 查看日志（可选）
docker compose logs -f
```

#### 2.4 访问应用

**Web UI 访问地址**：
- 本地：http://localhost:8501
- 局域网：http://YOUR_IP:8501

**查看本机 IP**：
```bash
# Windows
ipconfig

# Linux/macOS
ip addr show   # Linux
ifconfig       # macOS
```

### 3. 常用 Docker 命令

```bash
# 启动服务
docker compose up -d

# 停止服务
docker compose down

# 重启服务
docker compose restart

# 查看日志
docker compose logs -f

# 查看运行状态
docker compose ps

# 进入容器（调试用）
docker exec -it subsai-webui bash

# 更新到最新版本
git pull origin main
docker compose down
docker compose build --no-cache
docker compose up -d

# 清理旧镜像（节省空间）
docker system prune -a
```

### 4. GPU 加速（可选）

如果您有 NVIDIA GPU，可以启用 GPU 加速：

#### 4.1 安装 NVIDIA Container Toolkit

**Ubuntu/Linux**：
```bash
# 添加 NVIDIA 仓库
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# 安装
sudo apt update
sudo apt install -y nvidia-container-toolkit

# 重启 Docker
sudo systemctl restart docker
```

**Windows (Docker Desktop)**：
Docker Desktop 会自动检测 NVIDIA GPU，无需额外配置。

#### 4.2 使用 GPU 启动

修改 `docker-compose.yml`：
```yaml
services:
  subsai-webui-cpu:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

或使用 GPU 配置文件：
```bash
docker compose --profile gpu up -d
```

---

## 💻 方式二：本地安装

适合需要深度定制或开发调试的用户。

### 1. 系统要求

| 组件 | 要求 |
|-----|------|
| **操作系统** | Ubuntu 20.04+, Windows 10+, macOS 10.15+ |
| **Python** | 3.10 或 3.11（**不支持 3.12+**）|
| **内存** | 至少 8GB RAM（推荐 16GB）|
| **硬盘** | 至少 10GB 可用空间 |
| **GPU** | 可选（NVIDIA CUDA 11.7+ 或 AMD ROCm）|

### 2. 安装步骤

#### Ubuntu/Debian Linux

```bash
# 1. 安装系统依赖
sudo apt update
sudo apt install -y python3.10 python3-pip python3-venv \
  ffmpeg git gcc g++ make

# 2. 克隆仓库
git clone https://github.com/william08190/subsai.git
cd subsai

# 3. 创建虚拟环境（推荐）
python3.10 -m venv venv
source venv/bin/activate

# 4. 升级 pip
pip install --upgrade pip setuptools wheel

# 5. 安装依赖
pip install -r requirements.txt

# 6. 安装项目
pip install -e .

# 7. 启动 Web UI
python src/subsai/webui.py
```

#### Windows

```powershell
# 1. 安装 Python 3.10
# 下载：https://www.python.org/downloads/release/python-31011/
# 安装时勾选 "Add Python to PATH"

# 2. 安装 ffmpeg
# 方式 A: 使用 Chocolatey（推荐）
choco install ffmpeg

# 方式 B: 使用 Scoop
scoop install ffmpeg

# 方式 C: 手动安装
# 1. 下载：https://ffmpeg.org/download.html#build-windows
# 2. 解压到 C:\ffmpeg
# 3. 添加 C:\ffmpeg\bin 到系统 PATH

# 3. 克隆仓库
git clone https://github.com/william08190/subsai.git
cd subsai

# 4. 创建虚拟环境
python -m venv venv
.\venv\Scripts\activate

# 5. 升级 pip
python -m pip install --upgrade pip setuptools wheel

# 6. 安装依赖
pip install -r requirements.txt

# 7. 安装项目
pip install -e .

# 8. 启动 Web UI
python src\subsai\webui.py
```

#### macOS

```bash
# 1. 安装 Homebrew（如果未安装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. 安装依赖
brew install python@3.10 ffmpeg git

# 3. 克隆仓库
git clone https://github.com/william08190/subsai.git
cd subsai

# 4. 创建虚拟环境
python3.10 -m venv venv
source venv/bin/activate

# 5. 升级 pip
pip install --upgrade pip setuptools wheel

# 6. 安装依赖
pip install -r requirements.txt

# 7. 安装项目
pip install -e .

# 8. 启动 Web UI
python src/subsai/webui.py
```

### 3. 验证安装

```bash
# 检查 Python 版本
python --version  # 应显示 Python 3.10.x 或 3.11.x

# 检查 ffmpeg
ffmpeg -version

# 检查 PyTorch GPU 支持（如果有 GPU）
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# 启动 Web UI
python src/subsai/webui.py
```

成功后，浏览器会自动打开 http://localhost:8501

---

## 📊 系统要求详解

### 最低配置

| 组件 | 最低要求 | 备注 |
|-----|---------|------|
| CPU | 双核 2.0GHz | 推荐四核以上 |
| 内存 | 8GB RAM | 使用大模型需要更多 |
| 硬盘 | 10GB 可用空间 | 模型缓存会占用空间 |
| 网络 | 稳定互联网连接 | 首次下载模型需要 |

### 推荐配置

| 组件 | 推荐配置 | 性能提升 |
|-----|---------|---------|
| CPU | 八核 3.0GHz+ | 2-3倍 |
| 内存 | 16GB RAM | 可运行大模型 |
| GPU | NVIDIA RTX 3060+ (6GB) | 10-20倍 |
| 硬盘 | SSD 50GB+ | I/O 性能提升 |

### GPU 加速支持

#### NVIDIA GPU

**支持的 GPU**：
- RTX 系列：RTX 4090/4080/4070/3090/3080/3070/3060
- GTX 系列：GTX 1660 及以上
- 专业卡：A100/A6000/V100/T4

**CUDA 要求**：CUDA 11.7 或更高

**安装 CUDA**：
```bash
# Ubuntu
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600
sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/3bf863cc.pub
sudo add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/ /"
sudo apt update
sudo apt install cuda-11-7

# 验证
nvidia-smi
```

#### AMD GPU

**支持的 GPU**：RX 6000/7000 系列，部分 Vega 系列

**ROCm 支持**：需要安装 ROCm 5.0+

详情参考：https://rocm.docs.amd.com/

---

## ⚡ 性能优化

### 1. 模型选择

根据需求选择合适的模型大小：

| 模型 | 大小 | 速度 | 准确度 | 推荐场景 |
|-----|-----|------|--------|---------|
| tiny | 39MB | 最快 | 较低 | 快速预览 |
| base | 74MB | 快 | 中等 | 日常使用 |
| small | 244MB | 中等 | 良好 | 平衡选择 |
| medium | 769MB | 慢 | 很好 | 高质量需求 |
| large-v2 | 1.5GB | 最慢 | 最好 | 专业使用 |

**使用示例**：
```python
# Web UI: 在 Model Type 下拉框中选择

# CLI:
subsai video.mp4 --model openai/whisper \
  --model-configs '{"model_type": "small"}'
```

### 2. GPU 优化

```python
# 检查 GPU 可用性
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU count: {torch.cuda.device_count()}")

# 使用 GPU
# 在 Web UI 中会自动检测并使用 GPU
```

### 3. 批处理优化

对于多个视频文件：

```bash
# 创建文件列表 videos.txt
/path/to/video1.mp4
/path/to/video2.mp4
/path/to/video3.mp4

# 批量处理
subsai videos.txt --model openai/whisper --format ass
```

### 4. 内存优化

如果遇到内存不足：

```python
# 使用较小的模型
--model-configs '{"model_type": "tiny"}'

# 或减少 batch size
--model-configs '{"batch_size": 8}'
```

---

## 🐛 常见问题

### 1. ffmpeg 未找到

**症状**：`ffmpeg: command not found` 或 `FileNotFoundError: ffmpeg not found`

**解决方案**：

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# Windows (Chocolatey)
choco install ffmpeg

# Windows (Scoop)
scoop install ffmpeg

# macOS
brew install ffmpeg
```

### 2. Python 版本不兼容

**症状**：安装失败或运行时错误

**解决方案**：

```bash
# 检查 Python 版本
python --version

# 必须使用 Python 3.10 或 3.11
# Ubuntu 安装 Python 3.10
sudo apt install python3.10 python3.10-venv

# 创建虚拟环境时指定版本
python3.10 -m venv venv
```

### 3. Docker 权限问题（Linux）

**症状**：`permission denied while trying to connect to the Docker daemon`

**解决方案**：

```bash
# 添加用户到 docker 组
sudo usermod -aG docker $USER

# 重新登录或执行
newgrp docker

# 验证
docker ps
```

### 4. GPU 未被识别

**症状**：`CUDA not available` 或运行在 CPU 上

**解决方案**：

```bash
# 检查 NVIDIA 驱动
nvidia-smi

# 检查 CUDA
nvcc --version

# 重新安装 PyTorch（带 CUDA）
pip install torch==2.2.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117
```

### 5. 模型下载失败

**症状**：下载超时或网络错误

**解决方案**：

```bash
# 使用国内镜像（项目已配置）
export HF_ENDPOINT=https://hf-mirror.com

# 或手动下载模型到缓存目录
# Linux/macOS: ~/.cache/huggingface/
# Windows: C:\Users\YourName\.cache\huggingface\
```

### 6. 端口被占用

**症状**：`Address already in use` 或 `Port 8501 is already in use`

**解决方案**：

```bash
# 查看占用端口的进程
# Linux/macOS
lsof -i :8501

# Windows
netstat -ano | findstr :8501

# 结束进程或更改端口
python src/subsai/webui.py --server.port 8502
```

### 7. 内存不足

**症状**：`Out of memory` 或系统卡顿

**解决方案**：

```bash
# 使用较小的模型
--model-configs '{"model_type": "tiny"}'

# 或增加系统交换空间
# Linux
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 🔄 更新维护

### Docker 部署更新

```bash
# 1. 停止服务
docker compose down

# 2. 更新代码
git pull origin main

# 3. 重新构建（如有更新）
docker compose build --no-cache

# 4. 启动服务
docker compose up -d
```

### 本地安装更新

```bash
# 1. 激活虚拟环境
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows

# 2. 更新代码
git pull origin main

# 3. 更新依赖
pip install --upgrade -r requirements.txt

# 4. 重新安装
pip install -e .
```

### 版本回滚

```bash
# 查看可用版本
git tag

# 切换到特定版本
git checkout v1.1.0

# Docker 重新构建
docker compose build --no-cache
docker compose up -d

# 或本地重新安装
pip install -e .
```

---

## 📞 获取帮助

### 文档资源

- **GitHub 仓库**：https://github.com/william08190/subsai
- **问题反馈**：https://github.com/william08190/subsai/issues
- **更新日志**：查看 `BUG_FIX_REPORT_v1.1.0.md`

### 诊断信息

提交问题时，请提供以下信息：

```bash
# 系统信息
uname -a  # Linux/macOS
systeminfo  # Windows

# Python 版本
python --version

# 依赖版本
pip list | grep -E "torch|whisper|streamlit"

# Docker 版本（如适用）
docker --version
docker compose version

# GPU 信息（如适用）
nvidia-smi
```

---

## 📄 许可证

本项目采用 GNU General Public License v3.0 许可证。详见 [LICENSE](./LICENSE) 文件。

---

## 🙏 致谢

- 感谢 OpenAI 的 Whisper 模型
- 感谢所有贡献者和用户的反馈

---

**文档版本**：v1.1.0
**更新日期**：2025-11-19
**维护者**：william08190
