#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI批量处理后端服务
Batch Processing Backend Service for Subsai Karaoke

整合现有的卡拉OK生成功能，提供批量处理接口
"""

import os
import sys
import json
import asyncio
import uuid
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# 导入subsai卡拉OK功能
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from subsai import SubsAI, Tools
from subsai.karaoke_generator import create_karaoke_subtitles
from subsai.karaoke_styles import get_style_names

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="Subsai Karaoke 批量处理系统",
    description="批量为视频添加美观的动态卡拉OK歌词字幕",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置路径
BASE_DIR = Path(__file__).parent.parent.parent
WEBAPP_DIR = BASE_DIR / "webapp"
UPLOAD_DIR = WEBAPP_DIR / "uploads"
OUTPUT_DIR = WEBAPP_DIR / "outputs"
STATIC_DIR = WEBAPP_DIR / "static"
TEMPLATE_DIR = WEBAPP_DIR / "templates"

# 默认配置文件路径
DEFAULT_CONFIG_PATH = BASE_DIR / "linto-ai-whisper-timestamped_configs.json"

# 确保目录存在
for dir_path in [UPLOAD_DIR, OUTPUT_DIR, STATIC_DIR, TEMPLATE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# 挂载静态文件和输出目录
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/outputs", StaticFiles(directory=str(OUTPUT_DIR)), name="outputs")

# 全局状态管理
jobs: Dict[str, Dict[str, Any]] = {}
active_websockets: List[WebSocket] = []

# 加载默认配置
def load_default_config() -> Dict[str, Any]:
    """加载默认Whisper配置"""
    if DEFAULT_CONFIG_PATH.exists():
        with open(DEFAULT_CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

DEFAULT_WHISPER_CONFIG = load_default_config()


# Pydantic模型
class ProcessConfig(BaseModel):
    style_name: str = "classic"  # 卡拉OK样式
    words_per_line: int = 10
    aspect_ratio: Optional[str] = None  # 视频宽高比
    fontsize: Optional[int] = None  # 字体大小
    vertical_margin: Optional[int] = None  # 垂直边距
    model_name: str = "linto-ai/whisper-timestamped"
    whisper_config: Optional[Dict[str, Any]] = None  # Whisper配置
    crf: int = 18  # 视频质量 CRF 值 (0-51, 越低质量越高, 默认18高质量)
    preset: str = "medium"  # 编码速度预设 (ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow)
    whisper_model_type: Optional[str] = None  # Whisper模型类型 (base, small, medium, large-v2, large-v3, large-v3-turbo)
    custom_font: Optional[str] = None  # 自定义字体名称
    custom_colors: Optional[Dict[str, str]] = None  # 自定义颜色 {"primary": "#FFFFFF", "highlight": "#FFD700"}


class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: int
    current_file: Optional[str] = None
    total_files: int = 0
    processed_files: int = 0
    failed_files: int = 0
    output_files: List[Dict[str, Any]] = []
    error: Optional[str] = None
    created_at: str
    updated_at: str


# WebSocket连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()


def update_job_status(job_id: str, **kwargs):
    """更新任务状态"""
    if job_id in jobs:
        jobs[job_id].update(kwargs)
        jobs[job_id]['updated_at'] = datetime.now().isoformat()


async def broadcast_job_update(job_id: str):
    """广播任务更新"""
    if job_id in jobs:
        await manager.broadcast({
            'type': 'job_update',
            'job_id': job_id,
            'data': jobs[job_id]
        })


async def process_video_job(job_id: str, video_files: List[Path], config: ProcessConfig):
    """后台处理视频任务"""
    try:
        # 更新任务状态
        update_job_status(
            job_id,
            status='processing',
            total_files=len(video_files),
            progress=0
        )
        await broadcast_job_update(job_id)

        # 创建任务输出目录
        job_output_dir = OUTPUT_DIR / job_id
        job_output_dir.mkdir(exist_ok=True)

        # 初始化SubsAI
        subs_ai = SubsAI()
        tools = Tools()

        # 构建Whisper模型配置
        if config.whisper_model_type:
            # 用户指定了模型类型，动态构建配置
            model_config = DEFAULT_WHISPER_CONFIG.copy()
            model_config['model_type'] = config.whisper_model_type
            logger.info(f"使用用户指定的Whisper模型: {config.whisper_model_type}")
        elif config.whisper_config:
            # 使用用户提供的完整配置
            model_config = config.whisper_config
            logger.info(f"使用用户提供的Whisper配置")
        else:
            # 使用默认配置
            model_config = DEFAULT_WHISPER_CONFIG
            logger.info(f"使用默认Whisper配置")

        logger.info(f"Whisper配置详情: {model_config}")
        model = subs_ai.create_model(config.model_name, model_config=model_config)

        # 处理每个视频
        output_files = []
        for i, video_path in enumerate(video_files):
            try:
                update_job_status(
                    job_id,
                    current_file=video_path.name,
                    progress=int((i / len(video_files)) * 100)
                )
                await broadcast_job_update(job_id)

                logger.info(f"[{i+1}/{len(video_files)}] 处理视频: {video_path.name}")

                # 1. 生成字幕
                logger.info(f"步骤1: 生成字幕...")
                subs = subs_ai.transcribe(str(video_path), model)

                if not subs or len(subs) == 0:
                    logger.error(f"字幕生成失败: {video_path.name}")
                    update_job_status(
                        job_id,
                        failed_files=jobs[job_id]['failed_files'] + 1
                    )
                    await broadcast_job_update(job_id)
                    continue

                logger.info(f"生成了 {len(subs)} 个字幕事件")

                # 2. 转换为卡拉OK字幕
                logger.info(f"步骤2: 转换为卡拉OK字幕 (style: {config.style_name})...")

                # 提取自定义颜色参数
                primary_color = None
                secondary_color = None
                if config.custom_colors:
                    primary_color = config.custom_colors.get('primary')
                    secondary_color = config.custom_colors.get('highlight')

                karaoke_subs = create_karaoke_subtitles(
                    subs=subs,
                    style_name=config.style_name,
                    words_per_line=config.words_per_line,
                    fontsize=config.fontsize,
                    vertical_margin=config.vertical_margin,
                    fontname=config.custom_font,
                    primary_color=primary_color,
                    secondary_color=secondary_color
                )

                if not karaoke_subs or len(karaoke_subs) == 0:
                    logger.error(f"卡拉OK字幕生成失败: {video_path.name}")
                    update_job_status(
                        job_id,
                        failed_files=jobs[job_id]['failed_files'] + 1
                    )
                    await broadcast_job_update(job_id)
                    continue

                logger.info(f"生成了 {len(karaoke_subs)} 个卡拉OK字幕事件")

                # 3. 烧录到视频
                logger.info(f"步骤3: 烧录字幕到视频 (CRF={config.crf}, preset={config.preset})...")
                output_filename = f"{video_path.stem}_karaoke"
                output_path = tools.burn_karaoke_subtitles(
                    subs=karaoke_subs,
                    media_file=str(video_path),
                    output_filename=output_filename,
                    aspect_ratio=config.aspect_ratio,
                    crf=config.crf,
                    preset=config.preset
                )

                if os.path.exists(output_path):
                    # 移动到job输出目录
                    final_output = job_output_dir / os.path.basename(output_path)
                    shutil.move(output_path, str(final_output))

                    logger.info(f"✅ 处理完成: {final_output.name}")

                    # 记录输出文件
                    output_files.append({
                        'name': final_output.name,
                        'url': f'/outputs/{job_id}/{final_output.name}',
                        'size': os.path.getsize(final_output)
                    })

                    update_job_status(
                        job_id,
                        processed_files=jobs[job_id]['processed_files'] + 1,
                        output_files=output_files
                    )
                else:
                    logger.error(f"输出文件不存在: {output_path}")
                    update_job_status(
                        job_id,
                        failed_files=jobs[job_id]['failed_files'] + 1
                    )

                await broadcast_job_update(job_id)

            except Exception as e:
                logger.error(f"处理视频失败 {video_path.name}: {str(e)}")
                import traceback
                traceback.print_exc()
                update_job_status(
                    job_id,
                    failed_files=jobs[job_id]['failed_files'] + 1
                )
                await broadcast_job_update(job_id)
                continue

        # 任务完成
        update_job_status(
            job_id,
            status='completed',
            progress=100,
            current_file=None
        )
        await broadcast_job_update(job_id)

        logger.info(f"✅ 任务完成: {job_id}")
        logger.info(f"成功: {jobs[job_id]['processed_files']}, 失败: {jobs[job_id]['failed_files']}")

    except Exception as e:
        logger.error(f"任务执行失败 {job_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        update_job_status(
            job_id,
            status='failed',
            error=str(e)
        )
        await broadcast_job_update(job_id)


# API端点
@app.get("/")
async def root():
    """返回主页"""
    index_file = TEMPLATE_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "Subsai Karaoke 批量处理系统 API"}


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.post("/api/upload")
async def upload_videos(files: List[UploadFile] = File(...)):
    """上传视频文件"""
    uploaded_files = []

    for file in files:
        # 生成唯一文件名
        file_id = str(uuid.uuid4())
        file_ext = os.path.splitext(file.filename)[1]
        save_path = UPLOAD_DIR / f"{file_id}{file_ext}"

        # 保存文件
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        uploaded_files.append({
            'id': file_id,
            'name': file.filename,
            'path': str(save_path),
            'size': os.path.getsize(save_path)
        })

    logger.info(f"上传了 {len(uploaded_files)} 个文件")
    return {
        'success': True,
        'files': uploaded_files,
        'count': len(uploaded_files)
    }


@app.post("/api/process")
async def start_process(
    background_tasks: BackgroundTasks,
    file_ids: List[str],
    config: ProcessConfig
):
    """启动处理任务"""

    # 验证文件
    video_files = []
    for file_id in file_ids:
        # 查找上传的文件
        matching_files = list(UPLOAD_DIR.glob(f"{file_id}.*"))
        if matching_files:
            video_files.append(matching_files[0])

    if not video_files:
        raise HTTPException(status_code=400, detail="没有找到有效的视频文件")

    # 创建任务
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        'job_id': job_id,
        'status': 'pending',
        'progress': 0,
        'current_file': None,
        'total_files': len(video_files),
        'processed_files': 0,
        'failed_files': 0,
        'output_files': [],
        'error': None,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }

    # 添加后台任务
    background_tasks.add_task(
        process_video_job,
        job_id,
        video_files,
        config
    )

    logger.info(f"创建任务: {job_id}, 共 {len(video_files)} 个视频")
    return {
        'success': True,
        'job_id': job_id,
        'message': f'已创建处理任务，共{len(video_files)}个视频'
    }


@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    """获取任务状态"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="任务不存在")

    return jobs[job_id]


@app.get("/api/jobs")
async def list_jobs():
    """列出所有任务"""
    return {
        'jobs': list(jobs.values()),
        'count': len(jobs)
    }


@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str):
    """删除任务"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 删除输出文件
    job_output_dir = OUTPUT_DIR / job_id
    if job_output_dir.exists():
        shutil.rmtree(job_output_dir)

    # 删除任务记录
    del jobs[job_id]

    return {'success': True, 'message': '任务已删除'}


@app.get("/api/styles")
async def get_styles():
    """获取可用的卡拉OK样式"""
    style_names = get_style_names()
    styles = []

    style_descriptions = {
        'classic': {'name': '经典风格', 'description': '传统KTV黄色高亮'},
        'modern': {'name': '现代风格', 'description': '简约橙色渐变'},
        'neon': {'name': '霓虹风格', 'description': '赛博朋克紫红色'},
        'elegant': {'name': '优雅风格', 'description': '金色柔和动画'},
        'anime': {'name': '动漫风格', 'description': '青色描边效果'}
    }

    for style_id in style_names:
        info = style_descriptions.get(style_id, {'name': style_id.capitalize(), 'description': ''})
        styles.append({
            'id': style_id,
            'name': info['name'],
            'description': info['description'],
            'recommended': style_id == 'classic'
        })

    return {'styles': styles}


@app.get("/api/ratios")
async def get_ratios():
    """获取可用的视频比例"""
    return {
        'ratios': [
            {'id': '16:9', 'name': '16:9 横屏', 'resolution': '1920x1080', 'description': 'YouTube, B站'},
            {'id': '9:16', 'name': '9:16 竖屏', 'resolution': '1080x1920', 'description': '抖音, 快手'},
            {'id': '1:1', 'name': '1:1 正方形', 'resolution': '1080x1080', 'description': 'Instagram'},
            {'id': '4:3', 'name': '4:3 传统', 'resolution': '1440x1080', 'description': '传统电视'},
            {'id': '21:9', 'name': '21:9 超宽', 'resolution': '2560x1080', 'description': '电影风格'}
        ]
    }


@app.get("/api/config")
async def get_config():
    """获取默认配置"""
    return {
        'whisper_config': DEFAULT_WHISPER_CONFIG,
        'default_style': 'classic',
        'default_words_per_line': 10
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端点，用于实时推送任务进度"""
    await manager.connect(websocket)
    try:
        while True:
            # 保持连接
            data = await websocket.receive_text()
            # 可以处理客户端发来的消息
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    print("=" * 60)
    print("🎵 Subsai Karaoke 批量处理系统 - Web服务启动")
    print("=" * 60)
    print(f"📂 上传目录: {UPLOAD_DIR}")
    print(f"📂 输出目录: {OUTPUT_DIR}")
    print(f"🌐 API文档: http://localhost:8001/docs")
    print(f"🎨 Web界面: http://localhost:8001")
    print(f"📝 默认配置: {DEFAULT_CONFIG_PATH}")
    print("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理"""
    logger.info("服务正在关闭...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
