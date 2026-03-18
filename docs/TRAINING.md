# RVC 训练指南

## 概述

RVC (Retrieval-based Voice Conversion) 是目前最好的开源音色克隆方案之一。本指南帮助你训练自己的音色模型。

## 准备工作

### 1. 硬件要求

| 配置 | 最低 | 推荐 |
|------|------|------|
| GPU | GTX 1060 6GB | RTX 3060 12GB |
| 显存 | 6GB | 8GB+ |
| 内存 | 16GB | 32GB |
| 硬盘 | 20GB | 50GB SSD |

### 2. 软件要求

```bash
# Python 环境
Python >= 3.9

# CUDA
CUDA >= 11.7

# 依赖
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 训练数据

### 数据质量

- **时长**: 10-60 分钟（推荐 30 分钟以上）
- **格式**: WAV, MP3, FLAC
- **采样率**: 44100Hz 或 48000Hz
- **声道**: 单声道或立体声
- **内容**: 干净人声，无背景音乐

### 数据来源

1. **歌曲人声**: 使用 Demucs 分离
2. **语音录音**: 清晰朗读
3. **播客/访谈**: 提取说话人声音
4. **公开数据集**: VCTK, LibriSpeech

### 数据处理

```python
# 使用 MelodyClaw 处理训练数据
from src.separator import separate_vocals
from src.segmenter import segment_vocals

# 1. 分离人声
vocals_path, _ = separate_vocals("raw_audio.mp3", "train_data/vocals")

# 2. 分句切分（可选）
segments = segment_vocals(vocals_path, "train_data/chunks")
```

## 训练步骤

### 方式 1: 使用 RVC WebUI

1. **克隆仓库**
```bash
git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git
cd Retrieval-based-Voice-Conversion-WebUI
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **启动 WebUI**
```bash
python infer-web.py --port 7865
```

4. **训练流程**
   - 打开浏览器访问 `http://localhost:7865`
   - 进入 "Train" 标签
   - 上传训练音频
   - 设置参数（见下方推荐配置）
   - 点击 "Start Training"

### 方式 2: 命令行训练

```bash
# 1. 预处理音频
python preprocess.py \
    --input train_data/ \
    --output processed/ \
    --sr 48000

# 2. 提取特征
python extract_f0.py \
    --input processed/ \
    --method rmvpe

# 3. 训练模型
python train.py \
    --input processed/ \
    --model_name my_voice \
    --epochs 200 \
    --batch_size 12 \
    --gpu 0

# 4. 导出模型
python export.py \
    --model_name my_voice \
    --output models/rvc/my_voice.pth
```

## 推荐配置

### 通用配置

| 参数 | 值 | 说明 |
|------|-----|------|
| sample_rate | 48000 | 采样率 |
| epochs | 200-400 | 训练轮数 |
| batch_size | 12-16 | 批次大小 |
| save_every | 50 | 每N轮保存一次 |

### 根据数据量调整

| 数据时长 | epochs | batch_size | 预计时间 |
|----------|---------|------------|----------|
| 10-15分钟 | 400 | 8 | 2-3小时 |
| 15-30分钟 | 300 | 12 | 2-3小时 |
| 30-60分钟 | 200 | 16 | 2-4小时 |
| 60+分钟 | 150 | 16 | 3-5小时 |

### 音高检测方法

| 方法 | 速度 | 精度 | 推荐场景 |
|------|------|------|----------|
| rmvpe | 中 | 高 | ⭐ 通用推荐 |
| crepe | 慢 | 最高 | 高质量需求 |
| pm | 快 | 中 | 快速训练 |
| harvest | 中 | 高 | 中文语音 |

## 训练技巧

### 1. 数据清洗

- 去除静音片段
- 过滤低质量音频
- 去除背景噪音
- 保持一致的音量

### 2. 数据增强（可选）

```python
import librosa
import soundfile as sf

def augment_audio(input_path, output_dir):
    """数据增强"""
    y, sr = librosa.load(input_path, sr=None)
    
    # 原始
    sf.write(f"{output_dir}/original.wav", y, sr)
    
    # 速度变化
    y_fast = librosa.effects.time_stretch(y, rate=1.1)
    sf.write(f"{output_dir}/fast.wav", y_fast, sr)
    
    # 音调变化
    y_high = librosa.effects.pitch_shift(y, sr=sr, n_steps=2)
    sf.write(f"{output_dir}/high.wav", y_high, sr)
```

### 3. 避免过拟合

- 监控验证集损失
- 使用早停（early stopping）
- 不要过度训练

### 4. 模型评估

```python
from src.converter import VoiceConverter

# 测试不同 epoch 的模型
for epoch in [50, 100, 150, 200]:
    model_path = f"checkpoints/model_e{epoch}.pth"
    converter = VoiceConverter(model_path)
    
    # 转换测试音频
    converter.convert("test.wav", f"test_e{epoch}.wav")
    
    # 人工评估音质和相似度
```

## 常见问题

### Q: 训练时间太长？

A: 
- 减小数据量
- 降低 epochs
- 增大 batch_size
- 使用 GPU

### Q: 音质不好？

A: 
- 增加训练数据
- 提高数据质量
- 调整音高检测方法
- 尝试不同的 epoch

### Q: 相似度不够？

A: 
- 增加训练时长
- 使用更多训练数据
- 确保训练数据干净
- 尝试不同的采样率

### Q: 显存不足？

A: 
- 减小 batch_size
- 使用梯度累积
- 降低采样率
- 使用 CPU（慢）

## 进阶技巧

### 多说话人模型

```bash
python train.py \
    --input train_data/speaker1 train_data/speaker2 \
    --multi_speaker \
    --epochs 400
```

### 微调预训练模型

```bash
python train.py \
    --base_model models/rvc/base.pth \
    --input new_voice/ \
    --epochs 100
```

### 模型融合

```python
# 融合两个模型
from src.utils import merge_models

merged = merge_models(
    model_a="models/rvc/voice1.pth",
    model_b="models/rvc/voice2.pth",
    alpha=0.5  # 权重
)
```

## 资源链接

- [RVC 官方仓库](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI)
- [RVC 教程](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI/blob/main/docs/cn/README.cn.md)
- [模型下载](https://huggingface.co/lj1995/VoiceConversionWebUI)
- [社区论坛](https://discord.gg/voiceconversion)