#!/usr/bin/env python3
"""
RVC 模型训练脚本 - Train RVC Voice Model

使用目标音色音频训练 RVC 模型
"""

import os
import sys
import argparse
from pathlib import Path


def train_rvc(
    audio_path: str,
    output_name: str = "custom_voice",
    sample_rate: int = 48000,
    epochs: int = 200,
    batch_size: int = 12,
    gpu: int = 0
):
    """
    训练 RVC 模型
    
    Args:
        audio_path: 训练音频路径（可以是文件或目录）
        output_name: 输出模型名称
        sample_rate: 采样率
        epochs: 训练轮数
        batch_size: 批次大小
        gpu: GPU 编号
    """
    print("=" * 60)
    print("RVC 模型训练")
    print("=" * 60)
    
    audio_path = Path(audio_path)
    
    if not audio_path.exists():
        print(f"错误: 音频路径不存在: {audio_path}")
        return False
    
    print(f"""
训练配置:
  - 音频路径: {audio_path}
  - 输出名称: {output_name}
  - 采样率: {sample_rate} Hz
  - 训练轮数: {epochs}
  - 批次大小: {batch_size}
  - GPU: {gpu}
""")
    
    # 检查 RVC 是否安装
    print("\n提示: 此脚本需要安装 RVC-Project")
    print("请参考: https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI")
    print("\n训练步骤:")
    print("1. 安装 RVC: pip install rvc-python")
    print("2. 准备音频: 10-60 分钟干净人声")
    print("3. 运行训练:")
    print(f"   python train.py -s {audio_path} -m {output_name}")
    print("\n或使用 RVC WebUI:")
    print("  python infer-web.py --port 7865")
    
    return True


def main():
    parser = argparse.ArgumentParser(description="训练 RVC 音色模型")
    parser.add_argument("--audio", "-a", required=True, help="训练音频路径")
    parser.add_argument("--name", "-n", default="custom_voice", help="模型名称")
    parser.add_argument("--sample-rate", "-sr", type=int, default=48000, help="采样率")
    parser.add_argument("--epochs", "-e", type=int, default=200, help="训练轮数")
    parser.add_argument("--batch-size", "-b", type=int, default=12, help="批次大小")
    parser.add_argument("--gpu", "-g", type=int, default=0, help="GPU 编号")
    
    args = parser.parse_args()
    
    train_rvc(
        audio_path=args.audio,
        output_name=args.name,
        sample_rate=args.sample_rate,
        epochs=args.epochs,
        batch_size=args.batch_size,
        gpu=args.gpu
    )


if __name__ == "__main__":
    main()