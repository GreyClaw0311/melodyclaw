"""
音频合成模块 - Audio Mixer Module

将克隆后的人声与伴奏混合
"""

import os
import numpy as np
import librosa
from pathlib import Path
from typing import Optional
from pydub import AudioSegment


def mix_audio(
    vocals_path: str,
    accompaniment_path: str,
    output_path: str,
    vocals_db: float = 0.0,
    acc_db: float = -2.0,
    normalize: bool = True,
    reverb: bool = False
) -> str:
    """
    混合人声和伴奏
    
    Args:
        vocals_path: 人声文件路径
        accompaniment_path: 伴奏文件路径
        output_path: 输出文件路径
        vocals_db: 人声音量调整 (dB)
        acc_db: 伴奏音量调整 (dB)
        normalize: 是否归一化
        reverb: 是否添加混响
        
    Returns:
        输出文件路径
    """
    print(f"正在混合: {Path(vocals_path).name} + {Path(accompaniment_path).name}")
    
    # 加载音频
    vocals = AudioSegment.from_wav(vocals_path)
    accompaniment = AudioSegment.from_wav(accompaniment_path)
    
    # 调整音量
    vocals = vocals + vocals_db
    accompaniment = accompaniment + acc_db
    
    # 确保长度一致
    min_len = min(len(vocals), len(accompaniment))
    vocals = vocals[:min_len]
    accompaniment = accompaniment[:min_len]
    
    # 混合
    mixed = vocals.overlay(accompaniment)
    
    # 归一化
    if normalize:
        mixed = mixed.normalize()
    
    # 混响（可选）
    if reverb:
        mixed = _add_reverb(mixed)
    
    # 保存
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 根据扩展名保存
    if output_path.suffix.lower() == ".mp3":
        mixed.export(str(output_path), format="mp3", bitrate="320k")
    elif output_path.suffix.lower() == ".wav":
        mixed.export(str(output_path), format="wav")
    else:
        mixed.export(str(output_path), format="mp3", bitrate="320k")
    
    print(f"混合完成: {output_path}")
    return str(output_path)


def _add_reverb(audio: AudioSegment, room_scale: float = 0.5) -> AudioSegment:
    """
    添加简单混响效果
    
    Args:
        audio: 输入音频
        room_scale: 房间大小 (0-1)
        
    Returns:
        处理后的音频
    """
    # 简单实现：延迟 + 衰减
    delay_ms = int(50 + room_scale * 100)  # 50-150ms
    decay = 0.3 + room_scale * 0.3  # 0.3-0.6
    
    # 创建延迟版本
    delayed = audio - 10  # 降低音量
    delayed = delayed.overlay(audio, position=delay_ms)
    
    # 混合
    result = audio.overlay(delayed, position=0)
    
    return result


def batch_mix(
    vocals_dir: str,
    accompaniment_path: str,
    output_dir: str,
    **kwargs
) -> list:
    """
    批量混合
    
    Args:
        vocals_dir: 人声文件目录
        accompaniment_path: 伴奏文件路径
        output_dir: 输出目录
        **kwargs: mix_audio 的其他参数
        
    Returns:
        输出文件路径列表
    """
    vocals_dir = Path(vocals_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    for vocals_file in sorted(vocals_dir.glob("*.wav")):
        output_path = output_dir / f"mixed_{vocals_file.stem}.mp3"
        result = mix_audio(str(vocals_file), accompaniment_path, str(output_path), **kwargs)
        results.append(result)
    
    return results


def concatenate_audio(
    audio_files: list,
    output_path: str,
    crossfade_ms: int = 50
) -> str:
    """
    连接多个音频文件
    
    Args:
        audio_files: 音频文件路径列表
        output_path: 输出文件路径
        crossfade_ms: 淡入淡出时间（毫秒）
        
    Returns:
        输出文件路径
    """
    print(f"正在连接 {len(audio_files)} 个音频文件...")
    
    combined = AudioSegment.empty()
    
    for i, audio_file in enumerate(audio_files):
        audio = AudioSegment.from_wav(audio_file)
        
        if i == 0:
            combined = audio
        else:
            combined = combined.append(audio, crossfade=crossfade_ms)
    
    # 保存
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    combined.export(str(output_path), format="wav")
    
    print(f"连接完成: {output_path}")
    return str(output_path)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="音频混合")
    parser.add_argument("--vocals", "-v", required=True, help="人声文件")
    parser.add_argument("--accompaniment", "-a", required=True, help="伴奏文件")
    parser.add_argument("--output", "-o", required=True, help="输出文件")
    parser.add_argument("--vocals-db", type=float, default=0.0, help="人声音量调整")
    parser.add_argument("--acc-db", type=float, default=-2.0, help="伴奏音量调整")
    
    args = parser.parse_args()
    mix_audio(args.vocals, args.accompaniment, args.output, args.vocals_db, args.acc_db)