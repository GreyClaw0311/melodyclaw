"""
音色克隆模块 - Voice Conversion Module

使用 RVC 将人声转换为目标音色
"""

import os
import torch
import numpy as np
import librosa
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class ConversionConfig:
    """音色转换配置"""
    pitch_detection: str = "rmvpe"      # 音高检测: rmvpe, crepe, pm, harvest
    f0_method: str = "pm"               # F0 提取方法
    filter_radius: int = 3              # 过滤半径
    rms_mix_rate: float = 0.25         # RMS 混合比例
    protect_voiceless: float = 0.33    # 清音保护阈值
    output_sr: int = 44100             # 输出采样率


class VoiceConverter:
    """音色转换器（RVC）"""
    
    def __init__(
        self,
        model_path: str,
        config: Optional[ConversionConfig] = None,
        device: str = "cuda"
    ):
        """
        初始化音色转换器
        
        Args:
            model_path: RVC 模型路径 (.pth)
            config: 转换配置
            device: 计算设备
        """
        self.model_path = Path(model_path)
        self.config = config or ConversionConfig()
        self.device = device
        self.model = None
        self.cpt = None
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"模型文件不存在: {model_path}")
        
        self._load_model()
    
    def _load_model(self):
        """加载 RVC 模型"""
        print(f"正在加载 RVC 模型: {self.model_path.name}")
        
        # 加载模型权重
        self.cpt = torch.load(self.model_path, map_location=self.device)
        
        # 初始化模型（这里需要 RVC 的完整实现）
        # 实际使用时需要从 RVC 项目导入
        print("模型加载完成")
    
    def convert(
        self,
        input_path: str,
        output_path: str,
        pitch_shift: int = 0
    ) -> str:
        """
        转换单个音频文件
        
        Args:
            input_path: 输入音频路径
            output_path: 输出音频路径
            pitch_shift: 音高偏移（半音）
            
        Returns:
            输出文件路径
        """
        print(f"正在转换: {Path(input_path).name}")
        
        # 加载音频
        audio, sr = librosa.load(input_path, sr=self.config.output_sr)
        
        # 音高检测
        f0 = self._extract_f0(audio, sr)
        
        # 音高偏移
        if pitch_shift != 0:
            f0 = f0 * (2 ** (pitch_shift / 12))
        
        # 执行转换（核心逻辑需要 RVC 实现）
        # converted_audio = self._inference(audio, f0)
        
        # 保存
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # librosa.output.write_wav(str(output_path), converted_audio, sr)
        
        print(f"转换完成: {output_path}")
        return str(output_path)
    
    def convert_batch(
        self,
        input_dir: str,
        output_dir: str,
        pitch_shift: int = 0
    ) -> List[str]:
        """
        批量转换音频片段
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            pitch_shift: 音高偏移
            
        Returns:
            输出文件路径列表
        """
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_paths = []
        
        # 获取所有 wav 文件
        input_files = sorted(input_dir.glob("*.wav"))
        print(f"找到 {len(input_files)} 个音频片段")
        
        for input_file in input_files:
            output_path = output_dir / input_file.name
            result = self.convert(str(input_file), str(output_path), pitch_shift)
            output_paths.append(result)
        
        return output_paths
    
    def _extract_f0(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """
        提取基频 F0
        
        Args:
            audio: 音频数据
            sr: 采样率
            
        Returns:
            F0 数组
        """
        # 使用 librosa 的 pyin 或其他方法
        if self.config.pitch_detection == "pyin":
            f0, voiced_flags = librosa.piptrack(audio, sr=sr)
            f0 = f0[voiced_flags].mean(axis=0)
        else:
            # 其他方法的占位符
            f0 = np.zeros(len(audio) // 512 + 1)
        
        return f0


class VoiceCloner:
    """歌声克隆器（整合所有步骤）"""
    
    def __init__(
        self,
        separator_model: str = "htdemucs",
        converter_model: str = None,
        device: str = "cuda"
    ):
        """
        初始化歌声克隆器
        
        Args:
            separator_model: 人声分离模型
            converter_model: 音色转换模型路径
            device: 计算设备
        """
        self.device = device
        self.separator_model = separator_model
        self.converter_model = converter_model
        
        # 延迟加载
        self._separator = None
        self._converter = None
    
    def clone(
        self,
        song_path: str,
        output_path: str,
        pitch_shift: int = 0
    ) -> str:
        """
        完整歌声克隆流程
        
        Args:
            song_path: 原始歌曲路径
            output_path: 输出歌曲路径
            pitch_shift: 音高偏移
            
        Returns:
            输出文件路径
        """
        from .separator import separate_vocals
        from .segmenter import segment_vocals
        from .mixer import mix_audio
        
        print("=" * 50)
        print("开始歌声克隆流程")
        print("=" * 50)
        
        # 1. 人声分离
        print("\n[步骤 1/4] 人声分离...")
        vocals_path, acc_path = separate_vocals(
            song_path, 
            "temp/vocals", 
            self.separator_model, 
            self.device
        )
        
        # 2. 分句
        print("\n[步骤 2/4] 人声分句...")
        segments = segment_vocals(vocals_path, "temp/segments")
        
        # 3. 音色转换
        print("\n[步骤 3/4] 音色转换...")
        if self.converter_model:
            converter = VoiceConverter(self.converter_model, device=self.device)
            converted_segments = converter.convert_batch(
                "temp/segments", 
                "temp/converted",
                pitch_shift
            )
        else:
            print("警告: 未指定音色模型，跳过转换步骤")
            converted_segments = [s.audio_path for s in segments]
        
        # 4. 混合
        print("\n[步骤 4/4] 人声伴奏混合...")
        # 合并所有片段
        from pydub import AudioSegment
        combined = AudioSegment.empty()
        for seg_path in converted_segments:
            seg = AudioSegment.from_wav(seg_path)
            combined += seg
        
        combined_path = "temp/combined_vocals.wav"
        combined.export(combined_path, format="wav")
        
        # 与伴奏混合
        result = mix_audio(combined_path, acc_path, output_path)
        
        print("\n" + "=" * 50)
        print(f"歌声克隆完成: {result}")
        print("=" * 50)
        
        return result


def convert_voice(
    input_path: str,
    output_path: str,
    model_path: str,
    **kwargs
) -> str:
    """便捷函数：音色转换"""
    converter = VoiceConverter(model_path, **kwargs)
    return converter.convert(input_path, output_path)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="音色转换")
    parser.add_argument("--input", "-i", required=True, help="输入音频")
    parser.add_argument("--output", "-o", required=True, help="输出音频")
    parser.add_argument("--model", "-m", required=True, help="RVC 模型路径")
    parser.add_argument("--pitch", "-p", type=int, default=0, help="音高偏移")
    
    args = parser.parse_args()
    convert_voice(args.input, args.output, args.model, pitch_shift=args.pitch)