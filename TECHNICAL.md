# 技术方案汇总

## 核心流程

```
原始歌曲 → 人声分离 → 分句切片 → 音色克隆 → 人声伴奏合成 → 最终歌曲
```

## 所需模型汇总

### 必需模型（自建方案，免费）

| 模型 | 用途 | 大小 | 来源 |
|------|------|------|------|
| **Demucs htdemucs** | 人声分离 | ~300MB | HuggingFace / 首次使用自动下载 |
| **Silero VAD** | 静音检测 | ~2MB | torch.hub 自动下载 |
| **RVC v2 Base** | 音色克隆基础模型 | ~500MB | HuggingFace |
| **Whisper Medium** | ASR + 时间戳（可选） | ~1.5GB | HuggingFace |

**总大小**: ~2.3GB

### 目标音色模型（二选一）

| 方案 | 数据需求 | 训练时间 | 质量 |
|------|----------|----------|------|
| 使用预训练模型 | 无 | 即用 | 取决于模型质量 |
| 自己训练 | 10-60分钟音频 | 2-4小时 | 最佳 |

## API 接口统计

### 自建方案（推荐）

| 功能 | 实现方式 | 成本 | 硬件需求 |
|------|----------|------|----------|
| 人声分离 | Demucs 本地 | 免费 | GPU (推荐) |
| 分句切片 | Silero VAD | 免费 | CPU 即可 |
| 音色克隆 | RVC 本地 | 免费 | GPU 必须 |
| 音频混合 | pydub | 免费 | CPU |

**硬件推荐**: RTX 3060 (12GB) 以上

### 云 API 方案（可选）

| 服务商 | API | 功能 | 价格参考 |
|--------|-----|------|----------|
| Lalal.ai | 分离API | 人声分离 | $15/90分钟 |
| Replicate | RVC API | 音色克隆 | $0.0002/秒 |
| ElevenLabs | Voice Lab | 音色克隆 | $5/月起 |

## 关键技术对比

### 人声分离对比

| 方案 | 精度 | 速度 | 推荐度 |
|------|------|------|--------|
| Demucs v4 | ★★★★★ | ★★★☆☆ | ⭐ 首选 |
| Spleeter | ★★★★☆ | ★★★★☆ | 备选 |
| UVR5 | ★★★★★ | ★★☆☆☆ | 高精度 |

### 音色克隆对比

| 模型 | 音质 | 自然度 | 训练需求 | 推荐度 |
|------|------|--------|----------|--------|
| **RVC v2** | ★★★★★ | ★★★★★ | 10-60分钟 | ⭐⭐⭐ 首选 |
| So-VITS-SVC | ★★★★☆ | ★★★★☆ | 30-60分钟 | ⭐⭐ 备选 |
| GPT-SoVITS | ★★★★☆ | ★★★★★ | 5-10分钟 | ⭐⭐ 新秀 |
| OpenVoice | ★★★☆☆ | ★★★★☆ | 无需训练 | ⭐ 快速验证 |

## 为什么选择 RVC？

1. **音质最佳** - 接近真人演唱效果
2. **保留旋律** - 不会改变原曲音高和节奏
3. **社区活跃** - 大量预训练模型可用
4. **开源免费** - 无 API 调用费用
5. **易于训练** - 10分钟数据即可起步

## 与传统 TTS 的本质区别

| 维度 | 传统 TTS | 歌声克隆 (RVC) |
|------|----------|----------------|
| 输入 | 文本 | 音频 |
| 输出 | 朗读语音 | 演唱歌曲 |
| 旋律 | 无 | 保留原曲 |
| 节奏 | 固定 | 跟随歌曲 |
| 情感 | 有限 | 完整保留 |
| 技术原理 | 文本→语音 | 音频→音频转换 |

## 性能预估

### 处理时间（3分钟歌曲，RTX 3060）

| 步骤 | 耗时 |
|------|------|
| 人声分离 | 45秒 |
| 分句切片 | 10秒 |
| 音色转换 | 90秒 |
| 人声混合 | 5秒 |
| **总计** | **~2.5分钟** |

### 输出质量

- 音质: 接近原曲
- 相似度: 取决于训练数据
- 自然度: 高（保留原演唱细节）

## 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/GreyClaw0311/melodyclaw.git
cd melodyclaw

# 2. 安装依赖
pip install -r requirements.txt

# 3. 下载模型
python scripts/download_models.py --all

# 4. 准备音色模型
# 方式A: 下载预训练模型到 models/rvc/
# 方式B: 自己训练 python scripts/train_rvc.py --audio your_voice.wav

# 5. 执行歌声克隆
python src/converter.py \
    --input song.mp3 \
    --output final.mp3 \
    --model models/rvc/your_voice.pth
```

## 项目文件结构

```
melodyclaw/
├── README.md           # 完整项目文档
├── TECHNICAL.md        # 本文档
├── requirements.txt    # Python 依赖
├── config/
│   └── config.yaml    # 配置文件
├── models/            # 模型目录
│   ├── demucs/
│   ├── rvc/
│   └── whisper/
├── src/               # 核心代码
│   ├── separator.py   # 人声分离
│   ├── segmenter.py   # 分句切片
│   ├── converter.py   # 音色克隆
│   ├── mixer.py       # 音频混合
│   └── utils.py       # 工具函数
├── scripts/           # 脚本
│   ├── download_models.py
│   └── train_rvc.py
└── docs/              # 文档
    ├── API.md
    ├── TRAINING.md
    └── FAQ.md
```

---

*文档版本: 2026-03-17*