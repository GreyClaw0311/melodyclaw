"""
人声分句模块 - Vocal Segmentation Module

将连续人声按歌词句子切分成片段
"""

import os
import torch
import torchaudio
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass
import librosa


@dataclass
class VocalSegment:
    """人声片段"""
    index: int           # 片段序号
    start_time: float    # 开始时间（秒）
    end_time: float      # 结束时间（秒）
    duration: float      # 时长（秒）
    audio_path: str      # 音频文件路径
    text: Optional[str] = None  # 歌词文本（可选）


class VocalSegmenter:
    """人声分句器"""
    
    def __init__(
        self,
        vad_model: str = "silero",
        min_silence_ms: int = 300,
        min_speech_ms: int = 500,
        padding_ms: int = 50,
        device: str = "cuda"
    ):
        """
        初始化分句器
        
        Args:
            vad_model: VAD 模型 (silero, webrtc)
            min_silence_ms: 最小静音时长
            min_speech_ms: 最小语音时长
            padding_ms: 切片前后填充
            device: 计算设备
        """
        self.vad_model_name = vad_model
        self.min_silence_ms = min_silence_ms
        self.min_speech_ms = min_speech_ms
        self.padding_ms = padding_ms
        self.device = device
        self.vad_model = None
        self._load_vad()
    
    def _load_vad(self):
        """加载 VAD 模型"""
        if self.vad_model_name == "silero":
            print("正在加载 Silero VAD 模型...")
            self.vad_model, utils = torch.hub.load(
                repo_or_dir="snakers4/silero-vad",
                model="silero_vad",
                force_reload=False
            )
            self.vad_model.to(self.device)
            self.vad_model.eval()
            print("VAD 模型加载完成")
    
    def _detect_speech_segments(self, audio: np.ndarray, sr: int) -> List[Tuple[float, float]]:
        """
        检测语音段落
        
        Args:
            audio: 音频数据
            sr: 采样率
            
        Returns:
            [(start, end), ...] 语音段落的起止时间（秒）
        """
        if self.vad_model_name == "silero":
            # 转换为 tensor
            audio_tensor = torch.from_numpy(audio).float().to(self.device)
            if audio_tensor.dim() == 2:
                audio_tensor = audio_tensor.mean(dim=0)
            
            # 获取语音时间戳
            speech_timestamps = self.vad_model.get_speech_timestamps(
                audio_tensor,
                sampling_rate=sr,
                min_silence_duration_ms=self.min_silence_ms,
                min_speech_duration_ms=self.min_speech_ms
            )
            
            # 转换为秒
            segments = []
            for ts in speech_timestamps:
                start = ts["start"] / sr
                end = ts["end"] / sr
                segments.append((start, end))
            
            return segments
        
        return []
    
    def segment(
        self,
        vocals_path: str,
        output_dir: str,
        lyrics_path: Optional[str] = None
    ) -> List[VocalSegment]:
        """
        分句切分人声
        
        Args:
            vocals_path: 人声文件路径
            output_dir: 输出目录
            lyrics_path: 歌词文件路径（可选，LRC 格式）
            
        Returns:
            分句片段列表
        """
        vocals_path = Path(vocals_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"正在分句: {vocals_path.name}")
        
        # 加载音频
        audio, sr = librosa.load(str(vocals_path), sr=None)
        
        # 检测语音段落
        speech_segments = self._detect_speech_segments(audio, sr)
        print(f"检测到 {len(speech_segments)} 个语音段落")
        
        # 加载歌词（如果有）
        lyrics = None
        if lyrics_path:
            lyrics = self._load_lyrics(lyrics_path)
        
        # 切分并保存
        segments = []
        padding_samples = int(self.padding_ms * sr / 1000)
        
        for i, (start, end) in enumerate(speech_segments):
            # 添加 padding
            start_sample = max(0, int(start * sr) - padding_samples)
            end_sample = min(len(audio), int(end * sr) + padding_samples)
            
            # 提取片段
            chunk = audio[start_sample:end_sample]
            
            # 保存
            chunk_path = output_dir / f"chunk_{i:03d}.wav"
            librosa.output.write_wav(str(chunk_path), chunk, sr)
            
            # 创建片段对象
            segment = VocalSegment(
                index=i,
                start_time=start,
                end_time=end,
                duration=end - start,
                audio_path=str(chunk_path),
                text=lyrics[i] if lyrics and i < len(lyrics) else None
            )
            segments.append(segment)
        
        print(f"分句完成: {len(segments)} 个片段")
        return segments
    
    def _load_lyrics(self, lyrics_path: str) -> List[str]:
        """加载 LRC 格式歌词"""
        lyrics = []
        with open(lyrics_path, "r", encoding="utf-8") as f:
            for line in f:
                # 解析 LRC 格式: [mm:ss.xx]歌词文本
                line = line.strip()
                if line and line.startswith("["):
                    parts = line.split("]", 1)
                    if len(parts) == 2 and parts[1].strip():
                        lyrics.append(parts[1].strip())
        return lyrics


def segment_vocals(
    vocals_path: str,
    output_dir: str,
    **kwargs
) -> List[VocalSegment]:
    """便捷函数：分句切分人声"""
    segmenter = VocalSegmenter(**kwargs)
    return segmenter.segment(vocals_path, output_dir)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="人声分句")
    parser.add_argument("--input", "-i", required=True, help="人声文件")
    parser.add_argument("--output", "-o", default="output/segments", help="输出目录")
    parser.add_argument("--lyrics", "-l", help="歌词文件 (LRC)")
    
    args = parser.parse_args()
    segments = segment_vocals(args.input, args.output)
    
    for seg in segments:
        print(f"片段 {seg.index}: {seg.start_time:.2f}s - {seg.end_time:.2f}s ({seg.duration:.2f}s)")