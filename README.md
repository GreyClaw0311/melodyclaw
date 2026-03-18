# MelodyClaw - 歌声克隆系统

> 让 AI 用指定音色演唱任意歌曲

## 📋 项目概述

MelodyClaw 是一个完整的歌声克隆系统，**专为无GPU服务器设计**，所有 AI 推理通过外部 API 实现。

### 核心特性

- 🦞 **小龙虾动画播放器** - 根据歌词/节奏做出反应
- 🎵 **歌声克隆** - 保留原曲旋律和情感
- 📱 **响应式设计** - 自动适配手机和电脑
- 💰 **低成本** - ~$0.03/首歌曲

### 与传统 TTS 的区别

| 功能 | 传统 TTS | 歌声克隆 |
|------|----------|----------|
| 输出 | 朗读文本 | **演唱歌曲** |
| 旋律 | 无 | **保留原曲旋律** |
| 节奏 | 固定 | **跟随歌曲节奏** |
| 情感 | 有限 | **保留演唱情感** |

---

## 🏗️ 架构设计

### 整体架构

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    前端 Vue3    │────▶│  后端 FastAPI   │────▶│   外部 API      │
│  小龙虾播放器   │     │  (本地CPU处理)  │     │ 人声分离/克隆   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### 本地 vs 外部 API

| 功能 | 处理方式 | 成本 |
|------|----------|------|
| 文件上传/存储 | 本地 CPU | 免费 |
| 歌词解析/对齐 | 本地 CPU (Silero VAD) | 免费 |
| 音频切片/混合 | 本地 CPU (pydub) | 免费 |
| 人声分离 | 外部 API (HuggingFace) | 免费 |
| 音色克隆 | 外部 API (Replicate RVC) | $0.0002/秒 |

---

## 📁 项目结构

```
melodyclaw/
├── backend/               # 后端代码
│   ├── app/
│   │   ├── main.py       # FastAPI 入口
│   │   ├── api/          # API 路由
│   │   ├── services/     # 业务逻辑
│   │   └── worker.py     # Celery 任务
│   └── requirements.txt
│
├── frontend/              # 前端代码
│   ├── src/
│   │   ├── views/        # 页面组件
│   │   ├── components/   # 公共组件
│   │   └── api/          # API 封装
│   └── package.json
│
├── docs/                  # 详细文档
│   ├── QUICKSTART.md     # 快速开始 ⭐
│   ├── ARCHITECTURE.md   # 架构设计
│   ├── FRONTEND.md       # 前端设计
│   ├── BACKEND.md        # 后端 API
│   └── TECH_STACK.md     # 技术选型
│
└── docker-compose.yml     # Docker 部署
```

---

## 🚀 快速开始

### 方式 1: Docker 部署（推荐）

```bash
# 1. 克隆代码
git clone https://github.com/GreyClaw0311/melodyclaw.git
cd melodyclaw

# 2. 配置 API Key
cp .env.example .env
# 编辑 .env，填入 REPLICATE_API_KEY

# 3. 启动服务
docker-compose up -d

# 4. 访问应用
# http://localhost:80
```

### 方式 2: 手动部署

```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app &

# Celery Worker
celery -A app.worker worker &

# 前端
cd ../frontend
npm install && npm run build
npm run preview
```

详细步骤: [快速开始指南](docs/QUICKSTART.md)

---

## 📖 文档导航

| 文档 | 说明 |
|------|------|
| [快速开始](docs/QUICKSTART.md) | 5分钟部署指南 |
| [架构设计](docs/ARCHITECTURE.md) | 系统架构详解 |
| [前端设计](docs/FRONTEND.md) | 页面、功能模块、API交互 |
| [后端 API](docs/BACKEND.md) | API 接口详细设计 |
| [技术选型](docs/TECH_STACK.md) | 技术栈和成本分析 |

---

## 🖥️ 前端页面

### 页面列表

| 页面 | 功能 |
|------|------|
| 首页 | 小龙虾播放器 + 快速入口 |
| 歌曲管理 | 上传歌曲、触发人声分离 |
| 歌词编辑 | 上传歌词、自动对齐时间戳 |
| 克隆任务 | 选择预设音色、创建任务、查看进度 |
| 结果展示 | 对比播放、下载 |

### 预设音色

系统内置 6 种预设音色，用户无需上传音色模型：

| 音色 | 风格 | 适用场景 |
|------|------|----------|
| 流行男声 | 温暖明亮 | 流行、抒情 |
| 流行女声 | 清澈甜美 | 流行、抒情 |
| 摇滚男声 | 粗犷有力 | 摇滚、金属 |
| 民谣嗓音 | 朴实自然 | 民谣、乡村 |
| 童声 | 稚嫩可爱 | 儿歌、童谣 |
| 低沉嗓音 | 浑厚磁性 | 抒情、爵士 |

### 小龙虾动画功能

- 🦞 唱歌时钳子摆动、身体律动
- 📜 歌词滚动显示，当前歌词高亮
- 💨 气泡和音符飘出效果
- 🎵 根据音乐节奏做出反应
- 📱 响应式设计（手机/平板/桌面）

---

## 🔌 后端 API

### 核心 API 列表

| API | 方法 | 说明 |
|-----|------|------|
| `/api/v1/songs` | GET/POST | 歌曲列表/上传 |
| `/api/v1/songs/{id}/separate` | POST | 触发人声分离 |
| `/api/v1/lyrics/{id}/align` | POST | 自动对齐歌词 |
| `/api/v1/voices/preset` | GET | 获取预设音色列表 |
| `/api/v1/clone/tasks` | GET/POST | 克隆任务列表/创建 |
| `/api/v1/clone/results/{id}` | GET | 获取克隆结果 |

### WebSocket 实时推送

```
ws://host/ws/tasks/{task_id}
```

实时推送任务进度、状态变化。

---

## 💰 成本分析

### 处理一首 3 分钟歌曲

| 项目 | API | 成本 |
|------|-----|------|
| 人声分离 | HuggingFace Spleeter | 免费 |
| 音色克隆 | Replicate RVC | ~$0.03 |
| **合计** | | **~$0.03** |

### 免费额度

| API | 免费额度 |
|-----|----------|
| HuggingFace | 无限制 |
| Replicate | $5 新用户额度 |

---

## 🔧 技术栈

### 前端
- Vue.js 3 + Vite
- Element Plus
- Pinia + Axios

### 后端
- FastAPI
- Celery + Redis
- pydub + Silero VAD

### 外部 API
- HuggingFace (人声分离)
- Replicate RVC (音色克隆)

---

## 📝 开发计划

- [ ] 用户系统
- [ ] 批量处理
- [ ] 更多预设音色
- [ ] 分享功能
- [ ] 移动端 App
- [ ] 自定义音色上传（高级功能）

---

## 📄 License

MIT License