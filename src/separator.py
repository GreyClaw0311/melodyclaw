"""
人声分离模块 - Voice Separation Module

使用 Demucs 将歌曲分离为人声和伴奏
"""

import os
import torch
import torchaudio
from pathlib import Path
from typing import Tuple, Optional
from demucs import separate
from demucs.pretrained import get_model
from demucs.apply import apply_model


class VoiceSeparator:
    """人声分离器"""
    
    def __init__(self, model_name: str = "htdemucs", device: str = "cuda"):
        """
        初始化人声分离器
        
        Args:
            model_name: Demucs 模型名称 (htdemucs, htdemucs_ft, mdx_extra)
            device: 计算设备 (cuda, cpu, mps)
        """
        self.model_name = model_name
        self.device = device
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """加载 Demucs 模型"""
        print(f"正在加载 {self.model_name} 模型...")
        self.model = get_model(self.model_name)
        self.model.to(self.device)
        self.model.eval()
        print(f"模型加载完成: {self.model_name}")
    
    def separate(self, input_path: str, output_dir: str) -> Tuple[str, str]:
        """
        分离人声和伴奏
        
        Args:
            input_path: 输入音频文件路径
            output_dir: 输出目录
            
        Returns:
            (vocals_path, accompaniment_path): 人声路径和伴奏路径
        """
        input_path = Path(input_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"正在分离: {input_path.name}")
        
        # 加载音频
        wav, sr = torchaudio.load(str(input_path))
        
        # 确保采样率正确
        if sr != self.model.samplerate:
            resampler = torchaudio.transforms.Resample(sr, self.model.samplerate)
            wav = resampler(wav)
        
        # 转换为模型输入格式
        if wav.dim() == 2:
            wav = wav.unsqueeze(0)  # [1, 2, samples]
        
        wav = wav.to(self.device)
        
        # 分离
        with torch.no_grad():
            sources = apply_model(self.model, wav[None], progress=True)[0]
        
        # 获取人声和伴奏
        sources = sources.cpu()
        
        # Demucs 输出顺序: drums, bass, other, vocals
        vocals_idx = self.model.sources.index("vocals")
        vocals = sources[vocals_idx]
        
        # 伴奏 = 其他所有声部混合
        accompaniment = torch.zeros_like(vocals)
        for i, source_name in enumerate(self.model.sources):
            if source_name != "vocals":
                accompaniment += sources[i]
        
        # 保存
        vocals_path = output_dir / f"{input_path.stem}_vocals.wav"
        acc_path = output_dir / f"{input_path.stem}_accompaniment.wav"
        
        torchaudio.save(str(vocals_path), vocals, self.model.samplerate)
        torchaudio.save(str(acc_path), accompaniment, self.model.samplerate)
        
        print(f"人声已保存: {vocals_path}")
        print(f"伴奏已保存: {acc_path}")
        
        return str(vocals_path), str(acc_path)


def separate_vocals(input_path: str, output_dir: str, model: str = "htdemucs", device: str = "cuda") -> Tuple[str, str]:
    """
    便捷函数：分离人声
    
    Args:
        input_path: 输入音频文件
        output_dir: 输出目录
        model: 模型名称
        device: 计算设备
        
    Returns:
        (vocals_path, accompaniment_path)
    """
    separator = VoiceSeparator(model_name=model, device=device)
    return separator.separate(input_path, output_dir)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="人声分离")
    parser.add_argument("--input", "-i", required=True, help="输入音频文件")
    parser.add_argument("--output", "-o", default="output/separator", help="输出目录")
    parser.add_argument("--model", "-m", default="htdemucs", help="模型名称")
    parser.add_argument("--device", "-d", default="cuda", help="计算设备")
    
    args = parser.parse_args()
    separate_vocals(args.input, args.output, args.model, args.device)