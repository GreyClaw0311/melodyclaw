# MelodyClaw - 歌声克隆系统

> 让 AI 用指定音色演唱任意歌曲

## 📋 项目概述

MelodyClaw 是一个完整的歌声克隆系统，核心功能是将任意歌曲中的人声替换为目标音色，保留原曲的旋律、节奏和情感表达。

### 与传统 TTS 的区别

| 功能 | 传统 TTS | 歌声克隆 |
|------|----------|----------|
| 输出 | 朗读文本 | 演唱歌曲 |
| 旋律 | 无 | 保留原曲旋律 |
| 节奏 | 固定 | 跟随歌曲节奏 |
| 情感 | 有限 | 保留演唱情感 |
| 适用场景 | 语音播报 | 音乐创作、翻唱 |

## 🔄 处理流程

```
原始歌曲 (song.mp3)
    │
    ▼
┌─────────────────┐
│  人声分离 (Spleeter/Demucs)  │
└─────────────────┘
    │
    ├──► 伴奏 (accompaniment.wav) ──► 保留备用
    │
    └──► 人声 (vocals.wav)
              │
              ▼
         ┌─────────────────┐
         │  人声分句切片    │
         │  (VAD + 歌词对齐) │
         └─────────────────┘
              │
              ▼
         人声片段 (vocal_chunks/)
              │
              ▼
         ┌─────────────────┐
         │  音色克隆       │
         │  (So-VITS/RVC)  │
         └─────────────────┘
              │
              ▼
         克隆人声 (cloned_vocals/)
              │
              ▼
         ┌─────────────────┐
         │  人声伴奏合成    │
         └─────────────────┘
              │
              ▼
         最终歌曲 (output.mp3)
```

## 🛠️ 技术方案

### 阶段 1: 人声分离 (Source Separation)

**目标**: 将歌曲分离为人声和伴奏

**推荐方案**:

| 方案 | 模型 | 精度 | 速度 | 推荐度 |
|------|------|------|------|--------|
| Demucs v4 | htdemucs | ★★★★★ | ★★★☆☆ | ⭐ 首选 |
| Spleeter | 2stems-16k | ★★★★☆ | ★★★★☆ | 备选 |
| UVR5 | MDX-Net | ★★★★★ | ★★☆☆☆ | 高精度需求 |

**API 替代方案**:
- Lalal.ai API (付费，高质量)
- AudioSeparation API

### 阶段 2: 人声分句切片 (Vocal Segmentation)

**目标**: 将连续人声按歌词句子切分成片段

**技术要点**:

```
人声波形 + 歌词时间戳
         │
         ├── VAD (语音活动检测) 检测静音段落
         │
         ├── 歌词对齐 (歌词时间戳 / ASR识别)
         │
         └── 能量分析 (识别句子边界)
```

**工具选择**:

| 功能 | 推荐工具 | 说明 |
|------|----------|------|
| VAD | Silero VAD | 高精度静音检测 |
| 歌词对齐 | WhisperX | 自动语音识别 + 时间戳 |
| 能量分析 | librosa | 音频能量分析 |
| 手动对齐 | Audacity | 人工校准 |

### 阶段 3: 音色克隆 (Voice Conversion)

**目标**: 将人声片段转换为目标音色，保留旋律

**核心模型对比**:

| 模型 | 音质 | 自然度 | 训练需求 | 推荐度 |
|------|------|--------|----------|--------|
| **RVC v2** | ★★★★★ | ★★★★★ | 10-60分钟音频 | ⭐⭐⭐ 首选 |
| **So-VITS-SVC** | ★★★★☆ | ★★★★☆ | 30-60分钟音频 | ⭐⭐ 备选 |
| **OpenVoice** | ★★★☆☆ | ★★★★☆ | 无需训练 | ⭐ 快速验证 |
| **GPT-SoVITS** | ★★★★☆ | ★★★★★ | 5-10分钟音频 | ⭐⭐ 新秀 |

**RVC v2 优势**:
- 音质最佳，接近真人
- 支持实时变声
- 社区活跃，模型丰富
- 支持音高修正（保留原曲旋律）

### 阶段 4: 人声伴奏合成 (Mixing)

**目标**: 将克隆人声与原伴奏混合为最终歌曲

**处理步骤**:

```
克隆人声 + 原伴奏
     │
     ├── 时间对齐
     ├── 音量平衡
     ├── 混响处理 (可选)
     ├── 均衡器调整
     └── 导出最终音频
```

**工具**: 
- Python: pydub, librosa
- 专业: Reaper, FL Studio

## 📦 所需模型与资源

### 必需模型

| 模型 | 用途 | 大小 | 下载源 |
|------|------|------|--------|
| Demucs htdemucs | 人声分离 | ~300MB | HuggingFace |
| Silero VAD | 静音检测 | ~2MB | torch.hub |
| RVC v2 Base | 音色克隆基础模型 | ~500MB | HuggingFace |
| Whisper Medium | ASR + 时间戳 | ~1.5GB | HuggingFace |

### 目标音色模型

| 方案 | 训练数据 | 训练时间 | 质量 |
|------|----------|----------|------|
| 预训练模型 | 无需训练 | 即用 | 取决于模型 |
| 自己训练 | 10-60分钟 | 1-4小时 | 最佳 |

## 🔌 API 接口统计

### 自建方案（推荐）

| 功能 | 实现方式 | 成本 |
|------|----------|------|
| 人声分离 | Demucs 本地部署 | 免费 |
| 分句切片 | WhisperX + Silero | 免费 |
| 音色克隆 | RVC 本地部署 | 免费 |
| 音频处理 | pydub + librosa | 免费 |

**硬件需求**: GPU (推荐 RTX 3060 以上，显存 ≥8GB)

### 云 API 方案（可选）

| 服务商 | API | 功能 | 价格 |
|--------|-----|------|------|
| Lalal.ai | 分离API | 人声分离 | $15/90分钟 |
| Replicate | RVC API | 音色克隆 | $0.0002/s |
| ElevenLabs | Voice Design | 音色克隆 | $5/月起 |
| 讯飞 | 歌声合成 | 中文歌曲 | 联系销售 |

## 📁 项目结构

```
melodyclaw/
├── README.md                   # 项目文档
├── requirements.txt            # Python 依赖
├── config/
│   └── config.yaml            # 配置文件
├── models/
│   ├── demucs/                # 人声分离模型
│   ├── rvc/                   # RVC 模型
│   └── whisper/               # Whisper 模型
├── src/
│   ├── __init__.py
│   ├── separator.py           # 人声分离模块
│   ├── segmenter.py           # 人声分句模块
│   ├── converter.py           # 音色克隆模块
│   ├── mixer.py               # 音频合成模块
│   └── utils.py               # 工具函数
├── scripts/
│   ├── download_models.py     # 模型下载脚本
│   └── train_rvc.py          # RVC 训练脚本
├── examples/
│   ├── input/                 # 示例输入
│   └── output/                # 示例输出
└── docs/
    ├── API.md                 # API 文档
    ├── TRAINING.md            # 训练指南
    └── FAQ.md                 # 常见问题
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 下载模型

```bash
python scripts/download_models.py
```

### 3. 准备目标音色

方式 A: 使用预训练模型
```bash
# 从社区下载 .pth 模型文件放入 models/rvc/
```

方式 B: 自己训练
```bash
# 准备 10-60 分钟目标音色音频
python scripts/train_rvc.py --audio target_voice.wav
```

### 4. 运行歌声克隆

```bash
python src/converter.py \
    --input song.mp3 \
    --voice_model models/rvc/target.pth \
    --output output.mp3
```

## ⚙️ 配置说明

```yaml
# config/config.yaml
separator:
  model: htdemucs        # demucs 模型
  device: cuda           # cuda / cpu
  
segmenter:
  vad_model: silero      # VAD 模型
  min_silence_ms: 300    # 最小静音长度
  
converter:
  model: rvc_v2          # 音色克隆模型
  pitch_detection: rmvpe # 音高检测算法
  f0_method: pm          # F0 提取方法
  
mixer:
  output_format: mp3
  bitrate: 320k
```

## 📊 性能参考

| GPU | 人声分离 | 分句 | 音色克隆(总) | 总耗时 |
|-----|----------|------|--------------|--------|
| RTX 4090 | 15s | 5s | 30s | ~1min |
| RTX 3060 | 45s | 10s | 90s | ~2.5min |
| CPU only | 5min | 30s | 10min | ~16min |

*(以 3 分钟歌曲为例)*

## 🔗 相关资源

- [RVC 项目](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI)
- [Demucs](https://github.com/facebookresearch/demucs)
- [WhisperX](https://github.com/m-bain/whisperX)
- [Silero VAD](https://github.com/snakers4/silero-vad)

## 📝 更新日志

### 2026-03-17
- 初始版本发布
- 完整技术方案设计
- RVC v2 作为核心音色克隆方案

## 📄 License

MIT License