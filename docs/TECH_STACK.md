# 技术选型文档

> MelodyClaw 技术选型说明（本地CPU推理版本）

## 1. 硬件环境

| 资源 | 配置 | 说明 |
|------|------|------|
| CPU | 4核 | 支持中等规模模型推理 |
| 内存 | 16GB | 足够加载所有AI模型 |
| GPU | 无 | 所有推理在CPU上进行 |

---

## 2. AI 模型选型

### 2.1 人声分离模型对比

| 模型 | 内存 | CPU速度 | 质量 | 推荐 |
|------|------|---------|------|------|
| **Demucs htdemucs_ft** | ~800MB | 1分钟/分钟 | ⭐⭐⭐⭐ | ⭐ 首选 |
| Demucs htdemucs | ~1.5GB | 2分钟/分钟 | ⭐⭐⭐⭐⭐ | 质量优先 |
| Spleeter 2stems | ~500MB | 0.5分钟/分钟 | ⭐⭐⭐⭐ | 轻量级 |
| Open-Unmix | ~300MB | 0.3分钟/分钟 | ⭐⭐⭐ | 最轻量 |

**推荐**: Demucs htdemucs_ft（质量与速度平衡）

### 2.2 音色克隆模型对比

| 模型 | 内存 | CPU速度 | 音质 | 推荐 |
|------|------|---------|------|------|
| **RVC v2** | ~2.5GB | 4分钟/分钟 | ⭐⭐⭐⭐⭐ | ⭐ 首选 |
| So-VITS-SVC | ~3GB | 5分钟/分钟 | ⭐⭐⭐⭐ | 备选 |
| GPT-SoVITS | ~4GB | 6分钟/分钟 | ⭐⭐⭐⭐⭐ | 中文优化 |
| OpenVoice | ~1.5GB | 2分钟/分钟 | ⭐⭐⭐ | 快速验证 |

**推荐**: RVC v2（音质最佳）

### 2.3 歌词对齐模型对比

| 模型 | 内存 | CPU速度 | 推荐 |
|------|------|---------|------|
| **Silero VAD** | ~500MB | 实时10x+ | ⭐ 首选 |
| Whisper Tiny | ~400MB | 实时5x | 备选 |

**推荐**: Silero VAD（极快、极轻量）

---

## 3. 本地处理技术

### 3.1 AI 模型推理（CPU）

| 任务 | 模型 | 技术 | 内存 |
|------|------|------|------|
| 人声分离 | Demucs | PyTorch CPU | ~800MB |
| 歌词对齐 | Silero VAD | TorchScript | ~500MB |
| 音色克隆 | RVC v2 | PyTorch CPU | ~2.5GB |

### 3.2 音频处理（CPU）

| 任务 | 技术 | 内存 |
|------|------|------|
| 格式转换 | pydub + ffmpeg | ~100MB |
| 音频切片 | pydub | ~100MB |
| 音频混合 | pydub | ~100MB |

### 3.3 服务端

| 任务 | 技术 | 内存 |
|------|------|------|
| Web服务 | FastAPI | ~100MB |
| 任务队列 | Celery + Redis | ~200MB |
| WebSocket | python-socketio | ~50MB |

---

## 4. 技术栈

### 4.1 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue.js 3 | ^3.4.0 | 前端框架 |
| Vite | ^5.0.0 | 构建工具 |
| Element Plus | ^2.5.0 | UI组件库 |
| Axios | ^1.6.0 | HTTP客户端 |
| Socket.io-client | ^4.7.0 | WebSocket |
| Pinia | ^2.1.0 | 状态管理 |

### 4.2 后端

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.10+ | 开发语言 |
| FastAPI | ^0.109.0 | Web框架 |
| Celery | ^5.3.0 | 任务队列 |
| Redis | ^7.2.0 | 缓存/队列 |
| PyTorch | ^2.0.0 | 模型推理 |
| pydub | ^0.25.0 | 音频处理 |

### 4.3 AI 模型

| 模型 | 版本 | 大小 |
|------|------|------|
| Demucs | htdemucs_ft | ~300MB |
| Silero VAD | 4.1 | ~2MB |
| RVC v2 | base | ~500MB |
| Hubert | base | ~190MB |

---

## 5. 成本分析

### 5.1 完全本地化（推荐）

| 项目 | 成本 |
|------|------|
| 人声分离 | 免费 |
| 歌词对齐 | 免费 |
| 音色克隆 | 免费 |
| **合计** | **免费** |

### 5.2 硬件成本

| 项目 | 配置 | 月租参考 |
|------|------|----------|
| 云服务器 | 4C16G | ¥100-200/月 |

### 5.3 处理时间

| 歌曲 | 时间 |
|------|------|
| 1分钟歌曲 | ~4分钟 |
| 3分钟歌曲 | ~13分钟 |
| 5分钟歌曲 | ~22分钟 |

---

## 6. 优化建议

### 6.1 内存优化

```python
# 分步加载模型
class ModelManager:
    def load_demucs(self):
        # 只在需要时加载
        self.demucs = torch.load('demucs.pt', map_location='cpu')
    
    def unload_demucs(self):
        # 用完释放
        del self.demucs
        torch.cuda.empty_cache()  # GPU时
        gc.collect()  # CPU时
```

### 6.2 速度优化

```yaml
# 使用快速版模型
separator:
  model: htdemucs_ft  # 比标准版快 2x

converter:
  sample_rate: 32000  # 降低采样率
  f0_method: rmvpe    # 快速音高检测
```

---

## 7. 部署要求

### 7.1 系统要求

| 项目 | 最低 | 推荐 |
|------|------|------|
| CPU | 4核 | 8核 |
| 内存 | 8GB | 16GB |
| 存储 | 20GB | 50GB SSD |
| Python | 3.9+ | 3.11+ |

### 7.2 依赖安装

```bash
# 系统依赖
apt install ffmpeg redis

# Python依赖
pip install torch torchaudio
pip install demucs
pip install fastapi celery redis
pip install pydub soundfile
```

### 7.3 模型下载

```bash
# Demucs (首次使用自动下载)
demucs --help

# Silero VAD (首次使用自动下载)
python -c "import torch; torch.hub.load('snakers4/silero-vad', 'silero_vad')"

# RVC (手动下载)
wget https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/hubert_base.pt
wget https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/rvc_base.pt
```

---

## 8. 总结

### 推荐配置

| 功能 | 模型 | 内存 | 成本 |
|------|------|------|------|
| 人声分离 | Demucs htdemucs_ft | ~800MB | 免费 |
| 歌词对齐 | Silero VAD | ~500MB | 免费 |
| 音色克隆 | RVC v2 | ~2.5GB | 免费 |
| **总计** | | **~4GB** | **免费** |

### 性能指标

- **处理速度**: 3分钟歌曲约 13分钟
- **内存占用**: 峰值 ~4GB
- **成本**: 完全免费
- **隐私**: 数据完全本地

---

*文档版本: 2026-03-18*