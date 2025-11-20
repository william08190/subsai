"""
视频唯一性增强模块
用于生成独特的视频指纹,避免平台批量检测
"""
import random
import hashlib
from datetime import datetime, timedelta

def generate_random_metadata():
    """
    生成随机化的视频元数据

    Returns:
        dict: 包含随机元数据的字典
    """
    # 随机创建时间 (过去30天内)
    days_ago = random.randint(1, 30)
    hours_ago = random.randint(0, 23)
    random_date = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
    creation_time = random_date.strftime("%Y-%m-%dT%H:%M:%S")

    # 随机编码器字符串变体
    encoders = [
        "Lavf60.3.100",
        "Lavf59.27.100",
        "Lavf58.76.100",
        "Lavf60.16.100",
        "Lavf59.16.100"
    ]

    return {
        'creation_time': creation_time,
        'encoder': random.choice(encoders),
        'title': '',  # 清空标题
        'comment': '',  # 清空注释
    }

def calculate_uniqueness_params(input_file: str, index: int = 0):
    """
    根据输入文件和索引计算唯一性参数

    Args:
        input_file: 输入文件路径
        index: 视频序号 (用于批量处理时的差异化)

    Returns:
        dict: 包含唯一性处理参数
    """
    # 基于文件路径和时间的种子
    seed_str = f"{input_file}_{datetime.now().timestamp()}_{index}"
    seed_hash = hashlib.md5(seed_str.encode()).hexdigest()

    # 使用哈希值作为随机种子,确保可重现但唯一
    random.seed(int(seed_hash[:8], 16))

    params = {
        # 噪声强度 (0.001-0.003, 肉眼几乎不可见但会改变指纹)
        'noise_strength': random.uniform(0.0008, 0.0025),

        # 色彩微调 (±2% 饱和度, ±1.5% 亮度)
        'saturation': random.uniform(0.98, 1.02),
        'brightness': random.uniform(0.985, 1.015),
        'contrast': random.uniform(0.99, 1.01),

        # CRF微调 (15-19, 质量都很高但编码结果不同)
        'crf': random.randint(15, 19),

        # 编码预设随机 (slow/slower/veryslow 都是高质量)
        'preset': random.choice(['slow', 'slower', 'veryslow']),

        # x264编码参数微调
        'x264_params': {
            'me': random.choice(['umh', 'hex']),  # 运动估计算法
            'subme': random.choice([7, 8, 9]),  # 子像素运动估计质量
            'ref': random.choice([3, 4, 5]),  # 参考帧数量
        },

        # 音频处理微调
        'audio_bitrate': random.choice(['192k', '224k', '256k']),
        'audio_sample_rate': random.choice([44100, 48000]),

        # 元数据
        'metadata': generate_random_metadata(),
    }

    # 重置随机种子
    random.seed()

    return params

def get_resolution_scale_params(original_width: int, original_height: int,
                                  min_resolution: int = 1080):
    """
    计算分辨率缩放参数,确保最短边至少达到指定分辨率

    Args:
        original_width: 原始宽度
        original_height: 原始高度
        min_resolution: 最短边的最小分辨率 (默认1080)

    Returns:
        dict: 包含缩放参数的字典
    """
    # 确定最短边
    min_side = min(original_width, original_height)

    if min_side >= min_resolution:
        # 最短边已经达到或超过目标分辨率
        return {
            'need_scale': False,
            'target_width': original_width,
            'target_height': original_height,
            'scale_filter': None
        }

    # 计算缩放比例（基于最短边）
    scale_ratio = min_resolution / min_side
    target_width = int(original_width * scale_ratio)
    target_height = int(original_height * scale_ratio)

    # 确保尺寸为偶数 (编码器要求)
    target_width = target_width - (target_width % 2)
    target_height = target_height - (target_height % 2)

    # 使用lanczos算法进行高质量缩放
    scale_filter = f"scale={target_width}:{target_height}:flags=lanczos"

    return {
        'need_scale': True,
        'target_width': target_width,
        'target_height': target_height,
        'scale_filter': scale_filter,
        'scale_ratio': scale_ratio
    }

def build_uniqueness_filters(uniqueness_params: dict, scale_params: dict = None,
                               crop_filter: str = None, ass_file: str = None):
    """
    构建完整的视频滤镜链,包含唯一性处理

    Args:
        uniqueness_params: 唯一性参数
        scale_params: 缩放参数 (可选)
        crop_filter: 裁剪滤镜 (可选)
        ass_file: ASS字幕文件路径 (可选)

    Returns:
        str: 完整的ffmpeg滤镜链
    """
    filters = []

    # 1. 缩放 (如果需要)
    if scale_params and scale_params.get('need_scale'):
        filters.append(scale_params['scale_filter'])

    # 2. 裁剪 (如果需要)
    if crop_filter:
        filters.append(crop_filter)

    # 3. 色彩微调 (改变视频指纹但视觉影响极小)
    sat = uniqueness_params['saturation']
    bright = uniqueness_params['brightness']
    cont = uniqueness_params['contrast']
    filters.append(f"eq=saturation={sat}:brightness={(bright-1)*0.1}:contrast={cont}")

    # 4. 添加微小噪声 (改变每一帧的像素值,完全打破视频指纹)
    noise = uniqueness_params['noise_strength']
    filters.append(f"noise=alls={int(noise*100)}:allf=t")

    # 5. ASS字幕 (最后添加)
    if ass_file:
        filters.append(f"ass={ass_file}")

    return ",".join(filters)

def build_x264_params(uniqueness_params: dict):
    """
    构建x264编码参数字符串

    Args:
        uniqueness_params: 唯一性参数

    Returns:
        str: x264参数字符串
    """
    x264 = uniqueness_params['x264_params']
    params = [
        f"me={x264['me']}",
        f"subme={x264['subme']}",
        f"ref={x264['ref']}",
        "8x8dct=1",  # 启用8x8 DCT变换
        "fast-pskip=1",  # 快速跳过
    ]
    return ":".join(params)
