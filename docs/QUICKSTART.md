# MelodyClaw 快速开始指南

> 在 4C4G 无GPU服务器上部署歌声克隆系统

## 架构概览

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    前端 Vue3    │────▶│  后端 FastAPI   │────▶│   外部 API      │
│  小龙虾播放器   │     │  (本地CPU处理)  │     │ 人声分离/克隆   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

**本地处理** (无需GPU):
- 文件上传/存储
- 歌词解析/对齐 (Silero VAD)
- 音频切片/混合 (pydub)
- 任务调度 (Celery)

**外部 API**:
- 人声分离: HuggingFace Spleeter (免费)
- 音色克隆: Replicate RVC ($0.0002/秒)

---

## 5分钟快速部署

### 1. 克隆代码

```bash
git clone https://github.com/GreyClaw0311/melodyclaw.git
cd melodyclaw
```

### 2. 安装依赖

**后端**:
```bash
cd backend
pip install -r requirements.txt
```

**前端**:
```bash
cd ../frontend
npm install
npm run build
```

### 3. 配置 API Key

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置
nano .env
```

```bash
# .env 文件内容
REPLICATE_API_KEY=your_replicate_key_here
```

### 4. 启动服务

```bash
# 启动 Redis
redis-server &

# 启动后端
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# 启动 Celery Worker
celery -A app.worker worker -l info &

# 启动前端 (或用 Nginx)
cd ../frontend
npm run preview
```

### 5. 访问应用

打开浏览器访问: `http://localhost:4173`

---

## Docker 一键部署

```bash
# 安装 Docker 和 Docker Compose
sudo apt install docker.io docker-compose

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

---

## 获取 API Key

### Replicate (音色克隆)

1. 访问 https://replicate.com
2. 注册账号
3. 获取 API Key: https://replicate.com/account/api-tokens
4. 充值 $5 获得免费额度

**成本**: ~$0.03/首歌曲

### HuggingFace (人声分离，免费)

1. 访问 https://huggingface.co
2. 注册账号
3. 获取 Access Token: https://huggingface.co/settings/tokens

**成本**: 免费

---

## 使用流程

### 1. 上传歌曲

- 进入「歌曲管理」页面
- 上传 MP3/WAV 音频文件
- (可选) 上传 LRC 歌词文件

### 2. 触发人声分离

- 点击歌曲的「分离人声」按钮
- 等待处理完成 (约1分钟)

### 3. 创建克隆任务

- 进入「克隆任务」页面
- 选择源歌曲
- 选择目标音色
- 点击「创建任务」

### 4. 查看结果

- 任务完成后自动跳转
- 可对比播放原始和克隆版本
- 下载 MP3 文件

---

## 目录结构

```
melodyclaw/
├── backend/               # 后端代码
│   ├── app/
│   │   ├── main.py       # FastAPI 入口
│   │   ├── api/          # API 路由
│   │   ├── services/     # 业务逻辑
│   │   ├── models/       # 数据模型
│   │   └── worker.py     # Celery 任务
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/              # 前端代码
│   ├── src/
│   │   ├── views/        # 页面组件
│   │   ├── components/   # 公共组件
│   │   ├── api/          # API 封装
│   │   └── stores/       # 状态管理
│   ├── package.json
│   └── vite.config.js
│
├── docs/                  # 文档
│   ├── ARCHITECTURE.md   # 架构设计
│   ├── FRONTEND.md       # 前端设计
│   ├── BACKEND.md        # 后端设计
│   └── TECH_STACK.md     # 技术选型
│
├── docker-compose.yml
└── README.md
```

---

## 常见问题

### Q: 没有 GPU 怎么办？

A: 所有需要 GPU 的任务都通过外部 API 处理。本地只运行轻量级任务，普通 CPU 即可。

### Q: API 调用成本多少？

A: 
- 人声分离: 使用 HuggingFace 免费
- 音色克隆: Replicate ~$0.03/首歌曲
- 每月处理 100 首歌曲约 $3

### Q: 可以用自己的 API Key 吗？

A: 可以。前端支持用户输入自己的 API Key，费用由用户承担。

### Q: 支持哪些音频格式？

A: 
- 输入: MP3, WAV, FLAC
- 输出: MP3, WAV

### Q: 最大支持多大的文件？

A: 单文件最大 50MB，约 5-10 分钟歌曲。

---

## 下一步

- 📖 阅读 [架构设计文档](docs/ARCHITECTURE.md)
- 📖 阅读 [前端设计文档](docs/FRONTEND.md)
- 📖 阅读 [后端 API 文档](docs/BACKEND.md)
- 📖 阅读 [技术选型文档](docs/TECH_STACK.md)

---

*文档版本: 2026-03-18*