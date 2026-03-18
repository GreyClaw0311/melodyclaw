"""
工具函数 - Utility Functions
"""

import os
import hashlib
import json
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    config_path = Path(config_path)
    
    if not config_path.exists():
        return {}
    
    with open(config_path, "r", encoding="utf-8") as f:
        if config_path.suffix in [".yaml", ".yml"]:
            return yaml.safe_load(f)
        elif config_path.suffix == ".json":
            return json.load(f)
    
    return {}


def save_config(config: Dict[str, Any], config_path: str = "config/config.yaml"):
    """
    保存配置文件
    
    Args:
        config: 配置字典
        config_path: 配置文件路径
    """
    config_path = Path(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, "w", encoding="utf-8") as f:
        if config_path.suffix in [".yaml", ".yml"]:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        else:
            json.dump(config, f, indent=2, ensure_ascii=False)


def get_file_hash(file_path: str, algorithm: str = "md5") -> str:
    """
    计算文件哈希值
    
    Args:
        file_path: 文件路径
        algorithm: 哈希算法 (md5, sha256)
        
    Returns:
        哈希值字符串
    """
    if algorithm == "md5":
        hasher = hashlib.md5()
    elif algorithm == "sha256":
        hasher = hashlib.sha256()
    else:
        raise ValueError(f"不支持的哈希算法: {algorithm}")
    
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    
    return hasher.hexdigest()


def format_duration(seconds: float) -> str:
    """
    格式化时长
    
    Args:
        seconds: 秒数
        
    Returns:
        格式化字符串 (HH:MM:SS)
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def format_filesize(size_bytes: int) -> str:
    """
    格式化文件大小
    
    Args:
        size_bytes: 字节数
        
    Returns:
        格式化字符串
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"


def get_audio_info(audio_path: str) -> Dict[str, Any]:
    """
    获取音频文件信息
    
    Args:
        audio_path: 音频文件路径
        
    Returns:
        音频信息字典
    """
    import librosa
    
    duration = librosa.get_duration(filename=audio_path)
    y, sr = librosa.load(audio_path, sr=None)
    
    return {
        "path": audio_path,
        "duration": duration,
        "duration_formatted": format_duration(duration),
        "sample_rate": sr,
        "channels": 1 if y.ndim == 1 else 2,
        "samples": len(y),
        "filesize": os.path.getsize(audio_path),
        "filesize_formatted": format_filesize(os.path.getsize(audio_path))
    }


def setup_logging(log_file: Optional[str] = None, level: str = "INFO"):
    """
    设置日志
    
    Args:
        log_file: 日志文件路径
        level: 日志级别
    """
    import logging
    
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    handlers = [logging.StreamHandler()]
    
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        handlers=handlers
    )


def ensure_dir(path: str) -> Path:
    """
    确保目录存在
    
    Args:
        path: 目录路径
        
    Returns:
        Path 对象
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def cleanup_temp(temp_dir: str = "temp"):
    """
    清理临时文件
    
    Args:
        temp_dir: 临时目录
    """
    import shutil
    
    temp_path = Path(temp_dir)
    if temp_path.exists():
        shutil.rmtree(temp_path)
        print(f"已清理临时目录: {temp_dir}")


class Timer:
    """计时器"""
    
    def __init__(self, name: str = ""):
        self.name = name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, *args):
        self.end_time = datetime.now()
        elapsed = (self.end_time - self.start_time).total_seconds()
        if self.name:
            print(f"[{self.name}] 耗时: {elapsed:.2f} 秒")
    
    @property
    def elapsed(self) -> float:
        """已耗时（秒）"""
        if self.start_time is None:
            return 0
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()