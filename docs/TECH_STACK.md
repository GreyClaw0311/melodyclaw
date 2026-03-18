# 技术选型文档

> MelodyClaw 技术选型说明及成本分析

## 1. 硬件限制与应对策略

### 1.1 当前硬件

| 资源 | 配置 | 影响 |
|------|------|------|
| CPU | 4核 | 可处理轻量任务 |
| 内存 | 4GB | 限制本地模型加载 |
| GPU | 无 | AI推理必须外部调用 |

### 1.2 应对策略

| 原本需要GPU的任务 | 解决方案 | 成本 |
|------------------|----------|------|
| 人声分离 (Demucs/Spleeter) | 调用云API | 免费 ~ $0.17/分钟 |
| 音色克隆 (RVC) | 调用云API | $0.0002/秒 |
| 歌词对齐 | Silero VAD (CPU可用) | 免费 |
| 音频混合 | pydub (CPU可用) | 免费 |

---

## 2. 外部 API 选型

### 2.1 人声分离 API 对比

| API | 质量 | 速度 | 价格 | 免费额度 | 推荐 |
|-----|------|------|------|----------|------|
| **Lalal.ai** | ⭐⭐⭐⭐⭐ | 快 | $0.17/分钟 | 10分钟/月 | 生产环境 |
| **HuggingFace Spleeter** | ⭐⭐⭐⭐ | 中 | 免费 | 无限制 | ⭐开发/测试 |
| **AudioSeparator API** | ⭐⭐⭐⭐ | 快 | $0.05/分钟 | 新用户试用 | 备选 |

**推荐方案**: 
- **开发阶段**: HuggingFace Spleeter API (免费)
- **生产环境**: Lalal.ai (高质量)

### 2.2 音色克隆 API 对比

| API | 质量 | 特点 | 价格 | 免费额度 | 推荐 |
|-----|------|------|------|----------|------|
| **Replicate RVC** | ⭐⭐⭐⭐⭐ | 开源模型，灵活 | $0.0002/秒 | $5额度 | ⭐首选 |
| **ElevenLabs** | ⭐⭐⭐⭐⭐ | 商业级，稳定 | $5/月起 | 10,000字符/月 | 商业项目 |
| **GPT-SoVITS API** | ⭐⭐⭐⭐ | 中文优化 | 按量计费 | 有试用 | 中文场景 |
| **OpenVoice** | ⭐⭐⭐ | 快速验证 | $0.001/秒 | 有试用 | 测试 |

**推荐方案**: 
- **首选**: Replicate RVC (性价比高，灵活)
- **备选**: ElevenLabs (稳定，适合商业)

### 2.3 成本估算

处理一首 3 分钟歌曲的成本：

| API方案 | 人声分离 | 音色克隆 | 合计 |
|---------|----------|----------|------|
| Spleeter + Replicate | 免费 | ~$0.03 | **~$0.03** |
| Lalal.ai + Replicate | ~$0.51 | ~$0.03 | ~$0.54 |
| Lalal.ai + ElevenLabs | ~$0.51 | 包含 | ~$5/月起 |

---

## 3. 本地处理技术

### 3.1 可在本地 CPU 运行的任务

| 任务 | 技术 | CPU占用 | 内存占用 |
|------|------|---------|----------|
| 文件上传/存储 | FastAPI | 低 | 低 |
| 音频格式转换 | pydub + ffmpeg | 低 | 低 |
| 时长提取 | pydub | 低 | 低 |
| 音频切片 | pydub | 低 | 低 |
| 音频混合 | pydub | 低 | 低 |
| 歌词解析 | Python re | 极低 | 极低 |
| 语音活动检测 | Silero VAD | 中 | ~500MB |
| 任务调度 | Celery + Redis | 低 | 低 |

### 3.2 Silero VAD 说明

**为什么可以用 CPU？**
- 模型大小仅 ~2MB
- 推理速度：实时 10x+ (CPU)
- 内存占用：~500MB
- 无需 GPU 加速

**使用场景**:
- 歌词自动对齐
- 静音段落检测
- 音频切片定位

---

## 4. 技术栈选择

### 4.1 前端

| 技术 | 选择理由 |
|------|----------|
| **Vue.js 3** | 轻量、易上手、响应式 |
| **Vite** | 快速开发、热更新 |
| **Element Plus** | 成熟组件库、文档完善 |
| **Pinia** | Vue 3 官方状态管理 |

**为什么选 Vue 而非 React？**
- 学习曲线平缓
- 模板语法直观
- 适合中小型项目
- 国内生态更好

### 4.2 后端

| 技术 | 选择理由 |
|------|----------|
| **FastAPI** | 异步、自动文档、高性能 |
| **Celery** | 成熟的任务队列 |
| **Redis** | 缓存 + 队列，轻量 |
| **SQLite** | 开发阶段无需额外部署 |
| **pydub** | 简单易用的音频处理 |

**为什么选 FastAPI 而非 Django？**
- 异步支持好
- 自动生成 API 文档
- 性能更高
- 更适合 API 服务

### 4.3 数据库

| 阶段 | 选择 | 理由 |
|------|------|------|
| 开发 | SQLite | 无需安装，文件存储 |
| 生产 | PostgreSQL | 稳定、功能完善 |

### 4.4 任务队列

| 选择 | 说明 |
|------|------|
| **Celery + Redis** | 成熟方案，适合异步任务 |

---

## 5. 部署方案

### 5.1 开发环境

```bash
# 前端
cd frontend && npm run dev

# 后端
uvicorn app.main:app --reload

# Celery Worker
celery -A app.worker worker -l info

# Redis
redis-server
```

### 5.2 生产环境

```bash
# Docker Compose 一键部署
docker-compose up -d
```

**服务组成**:
- Nginx (反向代理 + 静态文件)
- FastAPI (API 服务)
- Celery Worker (异步任务)
- Redis (队列 + 缓存)

---

## 6. 文件存储

### 6.1 目录结构

```
/data/melodyclaw/
├── uploads/           # 上传文件
│   └── songs/{id}/
│       ├── audio.mp3
│       ├── lyrics.lrc
│       ├── vocals.wav
│       └── accompaniment.wav
├── voices/            # 音色模型
│   └── {id}/
│       └── model.pth
├── results/           # 克隆结果
│   └── {id}/
│       └── output.mp3
└── temp/              # 临时文件
```

### 6.2 存储估算

| 文件类型 | 单文件大小 | 100首歌曲 |
|----------|-----------|----------|
| 原始音频 | ~5MB | ~500MB |
| 人声分离结果 | ~30MB | ~3GB |
| 克隆结果 | ~5MB | ~500MB |
| **合计** | ~40MB | **~4GB** |

---

## 7. 安全考虑

### 7.1 API Key 管理

```python
# 加密存储用户的自定义 API Key
from cryptography.fernet import Fernet

class APIKeyManager:
    def __init__(self, encryption_key):
        self.cipher = Fernet(encryption_key)
    
    def encrypt(self, api_key: str) -> str:
        return self.cipher.encrypt(api_key.encode()).decode()
    
    def decrypt(self, encrypted: str) -> str:
        return self.cipher.decrypt(encrypted.encode()).decode()
```

### 7.2 文件上传限制

```python
ALLOWED_EXTENSIONS = {'.mp3', '.wav', '.flac', '.lrc'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

def validate_upload(file):
    # 检查扩展名
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"不支持的文件格式: {ext}")
    
    # 检查文件大小
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    
    if size > MAX_FILE_SIZE:
        raise ValueError(f"文件过大: {size / 1024 / 1024:.1f}MB")
```

### 7.3 请求频率限制

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/songs")
@limiter.limit("10/minute")  # 每分钟最多10次上传
async def upload_song(request: Request, file: UploadFile):
    ...
```

---

## 8. 监控与日志

### 8.1 日志配置

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
```

### 8.2 任务监控

```python
# Celery Flower (可选)
# pip install flower
# celery -A app.worker flower --port=5555
```

---

## 9. 扩展性考虑

### 9.1 未来可扩展方向

1. **分布式部署** - 多 Worker 并行处理
2. **CDN 加速** - 静态文件和音频分发
3. **数据库升级** - SQLite → PostgreSQL
4. **GPU 支持** - 服务器添加 GPU 后本地处理
5. **多租户** - 用户系统、权限管理

### 9.2 成本优化

1. **缓存机制** - 相同文件不重复处理
2. **批量处理** - 多首歌曲批量处理
3. **用户自带 API Key** - 用户承担 API 费用

---

## 10. 总结

### 推荐技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | Vue 3 + Vite + Element Plus | 现代化、易维护 |
| 后端 | FastAPI + Celery + Redis | 异步、高性能 |
| 数据库 | SQLite → PostgreSQL | 开发到生产平滑迁移 |
| 存储 | 本地文件系统 | 简单可靠 |
| 部署 | Docker Compose | 一键部署 |

### 推荐外部 API

| 功能 | API | 成本 |
|------|-----|------|
| 人声分离 | HuggingFace Spleeter | 免费 |
| 音色克隆 | Replicate RVC | $0.0002/秒 |

### 预估成本

- **开发阶段**: 完全免费
- **生产环境**: ~$0.03/首歌曲

---

*文档版本: 2026-03-18*