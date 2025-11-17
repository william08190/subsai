#FROM python:3.10.6
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

WORKDIR /subsai

COPY requirements.txt .

ENV DEBIAN_FRONTEND noninteractive

# 使用阿里云Ubuntu镜像源（解决国内网络问题）
RUN sed -i 's@http://.*archive.ubuntu.com@https://mirrors.aliyun.com@g' /etc/apt/sources.list && \
    sed -i 's@http://.*security.ubuntu.com@https://mirrors.aliyun.com@g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git gcc mono-mcs ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# 配置pip使用清华镜像源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

RUN pip install --no-cache-dir -r requirements.txt

COPY pyproject.toml .
COPY ./src ./src
COPY ./assets ./assets

RUN pip install .

EXPOSE 8501

ENTRYPOINT ["python", "src/subsai/webui.py", "--server.fileWatcherType", "none", "--browser.gatherUsageStats", "false"]
