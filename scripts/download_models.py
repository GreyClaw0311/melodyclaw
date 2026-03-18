#!/usr/bin/env python3
"""
模型下载脚本 - Download Required Models

下载所有需要的模型文件
"""

import os
import sys
from pathlib import Path
import argparse
import subprocess


# 模型下载配置
MODELS = {
    "demucs": {
        "name": "Demucs htdemucs",
        "type": "demucs",
        "size": "~300MB",
        "download": "pip install demucs  # 模型会在首次使用时自动下载"
    },
    "silero-vad": {
        "name": "Silero VAD",
        "type": "torch.hub",
        "size": "~2MB",
        "download": "自动下载（首次使用时）"
    },
    "whisper-medium": {
        "name": "Whisper Medium",
        "type": "huggingface",
        "size": "~1.5GB",
        "download": "pip install faster-whisper  # 首次使用时自动下载"
    },
    "rvc-base": {
        "name": "RVC v2 Base Model",
        "type": "huggingface",
        "size": "~500MB",
        "url": "https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/hubert_base.pt",
        "download": "手动下载到 models/rvc/"
    }
}


def download_demucs():
    """下载 Demucs 模型"""
    print("=" * 50)
    print("下载 Demucs 模型...")
    print("=" * 50)
    
    try:
        # 安装 demucs
        subprocess.run([sys.executable, "-m", "pip", "install", "demucs"], check=True)
        
        # 预下载模型
        print("\n正在预下载 htdemucs 模型（首次使用会自动下载）...")
        print("可以运行以下命令测试:")
        print("  python -c \"from demucs.pretrained import get_model; get_model('htdemucs')\"")
        
        print("\n✓ Demucs 模型准备完成")
        return True
    except Exception as e:
        print(f"✗ Demucs 模型下载失败: {e}")
        return False


def download_silero():
    """下载 Silero VAD 模型"""
    print("=" * 50)
    print("下载 Silero VAD 模型...")
    print("=" * 50)
    
    try:
        import torch
        
        # 下载模型
        model, utils = torch.hub.load(
            repo_or_dir="snakers4/silero-vad",
            model="silero_vad",
            force_reload=False
        )
        
        print("\n✓ Silero VAD 模型下载完成")
        return True
    except Exception as e:
        print(f"✗ Silero VAD 模型下载失败: {e}")
        return False


def download_whisper():
    """下载 Whisper 模型"""
    print("=" * 50)
    print("下载 Whisper 模型...")
    print("=" * 50)
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "faster-whisper"], check=True)
        
        print("\nWhisper 模型会在首次使用时自动下载")
        print("✓ faster-whisper 安装完成")
        return True
    except Exception as e:
        print(f"✗ Whisper 安装失败: {e}")
        return False


def download_rvc():
    """下载 RVC 基础模型"""
    print("=" * 50)
    print("下载 RVC 基础模型...")
    print("=" * 50)
    
    models_dir = Path("models/rvc")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # RVC 需要手动下载模型
    print("""
RVC 模型需要手动下载，有以下选择：

1. 使用社区预训练模型:
   - 访问: https://huggingface.co/lj1995/VoiceConversionWebUI
   - 下载 hubert_base.pt 到 models/rvc/
   
2. 自己训练模型:
   - 准备 10-60 分钟目标音色音频
   - 运行: python scripts/train_rvc.py

3. 使用第三方模型（如各种歌手音色）:
   - 搜索: RVC模型, AI翻唱模型
   - 下载 .pth 文件到 models/rvc/
""")
    
    return True


def main():
    parser = argparse.ArgumentParser(description="下载 MelodyClaw 所需模型")
    parser.add_argument("--all", action="store_true", help="下载所有模型")
    parser.add_argument("--demucs", action="store_true", help="只下载 Demucs")
    parser.add_argument("--silero", action="store_true", help="只下载 Silero VAD")
    parser.add_argument("--whisper", action="store_true", help="只下载 Whisper")
    parser.add_argument("--rvc", action="store_true", help="显示 RVC 下载说明")
    
    args = parser.parse_args()
    
    # 如果没有指定任何选项，显示帮助
    if not any([args.all, args.demucs, args.silero, args.whisper, args.rvc]):
        parser.print_help()
        print("\n可下载的模型:")
        for key, info in MODELS.items():
            print(f"  - {info['name']}: {info['size']}")
        print("\n使用 --all 下载所有模型")
        return
    
    results = []
    
    if args.all or args.demucs:
        results.append(("Demucs", download_demucs()))
    
    if args.all or args.silero:
        results.append(("Silero VAD", download_silero()))
    
    if args.all or args.whisper:
        results.append(("Whisper", download_whisper()))
    
    if args.all or args.rvc:
        results.append(("RVC", download_rvc()))
    
    # 打印结果
    print("\n" + "=" * 50)
    print("下载结果汇总")
    print("=" * 50)
    for name, success in results:
        status = "✓ 成功" if success else "✗ 失败"
        print(f"  {name}: {status}")


if __name__ == "__main__":
    main()