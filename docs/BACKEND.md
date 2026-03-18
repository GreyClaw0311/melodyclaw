# 后端 API 设计文档

> MelodyClaw 后端 API 接口详细设计

## 1. API 概述

### 1.1 基础信息

| 项目 | 说明 |
|------|------|
| 基础路径 | `/api/v1` |
| 协议 | HTTP/1.1, WebSocket |
| 数据格式 | JSON |
| 编码 | UTF-8 |
| 认证 | Bearer Token (JWT) |

### 1.2 通用响应格式

**成功响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

**错误响应**:
```json
{
  "code": 400,
  "message": "错误描述",
  "errors": [
    { "field": "file", "message": "文件格式不支持" }
  ]
}
```

### 1.3 分页响应格式

```json
{
  "code": 200,
  "data": [...],
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "total": 100,
    "totalPages": 5
  }
}
```

---

## 2. API 接口列表

### 2.1 歌曲管理 API

#### GET /api/v1/songs - 获取歌曲列表

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认 1 |
| pageSize | int | 否 | 每页数量，默认 20 |
| status | string | 否 | 状态筛选: all/pending/processed |
| keyword | string | 否 | 关键词搜索 |

**响应示例**:
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "title": "歌曲名",
      "artist": "歌手",
      "duration": 225,
      "status": "processed",
      "hasLyrics": true,
      "hasVocals": true,
      "createdAt": "2026-03-18T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "total": 50
  }
}
```

**本地处理**: ✅ 数据库查询

---

#### POST /api/v1/songs - 上传歌曲

**请求**: `multipart/form-data`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| audio | file | 是 | 音频文件 (MP3/WAV/FLAC) |
| lyrics | file | 否 | 歌词文件 (LRC格式) |
| title | string | 否 | 歌曲名 |
| artist | string | 否 | 歌手名 |

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "title": "歌曲名",
    "artist": "歌手",
    "duration": 225,
    "audioPath": "/uploads/songs/1/audio.mp3",
    "lyricsPath": "/uploads/songs/1/lyrics.lrc",
    "status": "pending"
  }
}
```

**本地处理**: ✅ 文件存储、格式转换、时长提取

**实现逻辑**:
```python
async def upload_song(audio: UploadFile, lyrics: UploadFile = None):
    # 1. 验证文件格式
    validate_audio_format(audio.filename)
    
    # 2. 保存文件到本地
    song_id = generate_id()
    audio_path = save_file(audio, f"uploads/songs/{song_id}/audio.mp3")
    
    # 3. 提取音频时长 (pydub)
    duration = get_audio_duration(audio_path)
    
    # 4. 如果有歌词，解析并保存
    if lyrics:
        lyrics_content = await lyrics.read()
        lyrics_path = save_file(lyrics, f"uploads/songs/{song_id}/lyrics.lrc")
    
    # 5. 保存到数据库
    song = Song.create(id=song_id, title=title, duration=duration, ...)
    
    return song
```

---

#### GET /api/v1/songs/{id} - 获取歌曲详情

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "title": "歌曲名",
    "artist": "歌手",
    "duration": 225,
    "status": "processed",
    "audioPath": "/uploads/songs/1/audio.mp3",
    "vocalsPath": "/uploads/songs/1/vocals.wav",
    "accompanimentPath": "/uploads/songs/1/accompaniment.wav",
    "lyrics": [
      { "time": 5.0, "text": "第一句歌词" },
      { "time": 10.5, "text": "第二句歌词" }
    ],
    "createdAt": "2026-03-18T10:00:00Z"
  }
}
```

**本地处理**: ✅ 数据库查询 + 文件读取

---

#### DELETE /api/v1/songs/{id} - 删除歌曲

**响应示例**:
```json
{
  "code": 200,
  "message": "删除成功"
}
```

**本地处理**: ✅ 文件删除 + 数据库删除

---

#### POST /api/v1/songs/{id}/separate - 触发人声分离

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| provider | string | 否 | API提供商: lalalai/spleeter |
| apiKey | string | 否 | 自定义API Key (可选) |

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "taskId": "sep_123456",
    "status": "pending",
    "estimatedTime": 60
  }
}
```

**处理逻辑**:
```
1. 本地创建异步任务
2. 调用外部人声分离API
3. 接收结果，保存文件
4. 通过WebSocket推送进度
```

**外部 API 调用**: ⚠️

**实现代码**:
```python
async def separate_vocals(song_id: int, provider: str = "spleeter"):
    # 1. 获取歌曲文件
    song = Song.get(song_id)
    audio_path = song.audio_path
    
    # 2. 调用外部 API
    if provider == "lalalai":
        result = await lalalai_api.separate(audio_path)
    elif provider == "spleeter":
        result = await spleeter_api.separate(audio_path)
    
    # 3. 下载结果文件
    vocals_path = download_file(result.vocals_url, f"songs/{song_id}/vocals.wav")
    accompaniment_path = download_file(result.accompaniment_url, f"songs/{song_id}/accompaniment.wav")
    
    # 4. 更新数据库
    song.vocals_path = vocals_path
    song.accompaniment_path = accompaniment_path
    song.status = "separated"
    song.save()
    
    return {"vocals_path": vocals_path, "accompaniment_path": accompaniment_path}
```

---

### 2.2 歌词管理 API

#### GET /api/v1/lyrics/{song_id} - 获取歌词

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "songId": 1,
    "lyrics": [
      { "index": 0, "time": 5.0, "text": "第一句歌词" },
      { "index": 1, "time": 10.5, "text": "第二句歌词" },
      { "index": 2, "time": 15.0, "text": "第三句歌词" }
    ],
    "source": "upload"
  }
}
```

**本地处理**: ✅ 文件读取 + LRC解析

---

#### PUT /api/v1/lyrics/{song_id} - 更新歌词

**请求体**:
```json
{
  "lyrics": [
    { "time": 5.0, "text": "修改后的歌词" },
    { "time": 10.5, "text": "第二句歌词" }
  ]
}
```

**本地处理**: ✅ 文件写入

---

#### POST /api/v1/lyrics/{song_id}/align - 自动对齐歌词

**说明**: 使用 Silero VAD 检测语音段落，自动生成时间戳

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minSilenceMs | int | 否 | 最小静音时长，默认 300 |

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "taskId": "align_123",
    "status": "processing"
  }
}
```

**本地处理**: ✅ Silero VAD (CPU可运行)

**实现代码**:
```python
import torch

def align_lyrics(song_id: int, vocals_path: str):
    # 1. 加载 Silero VAD 模型
    model, utils = torch.hub.load(
        repo_or_dir='snakers4/silero-vad',
        model='silero_vad',
        force_reload=False
    )
    
    # 2. 加载音频
    audio = load_audio(vocals_path)
    
    # 3. 检测语音段落
    timestamps = model.get_speech_timestamps(
        audio,
        sampling_rate=16000,
        min_silence_duration_ms=300
    )
    
    # 4. 生成时间戳
    lyrics = []
    for i, ts in enumerate(timestamps):
        lyrics.append({
            "time": ts['start'] / 16000,
            "text": ""  # 用户填充
        })
    
    return lyrics
```

---

### 2.3 克隆任务 API

#### POST /api/v1/clone/tasks - 创建克隆任务

**请求体**:
```json
{
  "songId": 1,
  "voiceId": "voice_pop_male",
  "pitchShift": 0
}
```

**参数说明**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| songId | int | 是 | 源歌曲ID |
| voiceId | string | 是 | 预设音色ID (如 voice_pop_male) |
| pitchShift | int | 否 | 音高偏移（半音），默认0 |

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "status": "pending",
    "estimatedTime": 180,
    "steps": [
      { "step": "separate", "status": "pending", "progress": 0 },
      { "step": "align", "status": "pending", "progress": 0 },
      { "step": "clone", "status": "pending", "progress": 0 },
      { "step": "mix", "status": "pending", "progress": 0 }
    ]
  }
}
```

**处理流程**:
```
1. 验证歌曲已分离人声
2. 验证预设音色ID有效
3. 创建任务记录
4. 加入 Celery 队列
5. 返回任务 ID
```

**外部 API 调用**: ⚠️ (音色克隆部分)

---

#### GET /api/v1/clone/tasks - 获取任务列表

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码 |
| status | string | 否 | 状态筛选 |

**本地处理**: ✅ 数据库查询

---

#### GET /api/v1/clone/tasks/{id} - 获取任务详情

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "songId": 1,
    "voiceId": 2,
    "status": "cloning",
    "progress": 60,
    "currentStep": "clone",
    "steps": [
      { "step": "separate", "status": "completed", "progress": 100 },
      { "step": "align", "status": "completed", "progress": 100 },
      { "step": "clone", "status": "processing", "progress": 50 },
      { "step": "mix", "status": "pending", "progress": 0 }
    ],
    "estimatedTime": 90,
    "createdAt": "2026-03-18T10:00:00Z"
  }
}
```

**本地处理**: ✅ 数据库查询 + 计算进度

---

#### POST /api/v1/clone/tasks/{id}/cancel - 取消任务

**本地处理**: ✅ 更新任务状态

---

### 2.4 预设音色 API

#### GET /api/v1/voices/preset - 获取预设音色列表

**说明**: 返回系统内置的预设音色列表，用户无需上传音色模型

**响应示例**:
```json
{
  "code": 200,
  "data": [
    {
      "id": "voice_pop_male",
      "name": "流行男声",
      "description": "温暖明亮，适合流行歌曲",
      "category": "pop",
      "previewUrl": "/static/voices/pop_male_preview.mp3",
      "modelId": "rvc-pop-male-v1",
      "suitable": ["流行", "抒情"]
    },
    {
      "id": "voice_pop_female",
      "name": "流行女声",
      "description": "清澈甜美，适合流行歌曲",
      "category": "pop",
      "previewUrl": "/static/voices/pop_female_preview.mp3",
      "modelId": "rvc-pop-female-v1",
      "suitable": ["流行", "抒情"]
    },
    {
      "id": "voice_rock_male",
      "name": "摇滚男声",
      "description": "粗犷有力，适合摇滚歌曲",
      "category": "rock",
      "previewUrl": "/static/voices/rock_male_preview.mp3",
      "modelId": "rvc-rock-male-v1",
      "suitable": ["摇滚", "金属"]
    },
    {
      "id": "voice_ballad",
      "name": "民谣嗓音",
      "description": "朴实自然，适合民谣歌曲",
      "category": "ballad",
      "previewUrl": "/static/voices/ballad_preview.mp3",
      "modelId": "rvc-ballad-v1",
      "suitable": ["民谣", "乡村"]
    },
    {
      "id": "voice_child",
      "name": "童声",
      "description": "稚嫩可爱，适合儿童歌曲",
      "category": "child",
      "previewUrl": "/static/voices/child_preview.mp3",
      "modelId": "rvc-child-v1",
      "suitable": ["儿歌", "童谣"]
    },
    {
      "id": "voice_deep",
      "name": "低沉嗓音",
      "description": "浑厚磁性，适合抒情歌曲",
      "category": "deep",
      "previewUrl": "/static/voices/deep_preview.mp3",
      "modelId": "rvc-deep-v1",
      "suitable": ["抒情", "爵士"]
    }
  ]
}
```

**本地处理**: ✅ 返回静态配置

---

#### GET /api/v1/voices/{id}/preview - 获取音色试听音频

**说明**: 返回预设音色的试听音频文件

**响应**: 音频文件流 (MP3)

**本地处理**: ✅ 返回静态文件

---

### 2.5 结果管理 API

#### GET /api/v1/clone/results/{id} - 获取克隆结果

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "taskId": 1,
    "songId": 1,
    "voiceId": 2,
    "outputPath": "/results/1/output.mp3",
    "duration": 225,
    "fileSize": 5400000,
    "createdAt": "2026-03-18T10:05:00Z"
  }
}
```

**本地处理**: ✅ 数据库查询

---

#### GET /api/v1/clone/results/{id}/download - 下载结果文件

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| format | string | 否 | 格式: mp3/wav，默认 mp3 |

**本地处理**: ✅ 文件下载

---

### 2.6 系统配置 API

#### GET /api/v1/config/providers - 获取可用的API提供商

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "separation": [
      {
        "id": "lalalai",
        "name": "Lalal.ai",
        "pricing": "$0.17/分钟",
        "freeQuota": "10分钟/月"
      },
      {
        "id": "spleeter",
        "name": "Spleeter (免费)",
        "pricing": "免费",
        "freeQuota": "无限制"
      }
    ],
    "clone": [
      {
        "id": "replicate",
        "name": "Replicate RVC",
        "pricing": "$0.0002/秒",
        "freeQuota": "$5免费额度"
      },
      {
        "id": "elevenlabs",
        "name": "ElevenLabs",
        "pricing": "$5/月起",
        "freeQuota": "10,000字符/月"
      }
    ]
  }
}
```

**本地处理**: ✅ 返回配置信息

---

## 3. WebSocket 接口

### 3.1 连接

```
ws://host/ws/tasks/{task_id}
```

### 3.2 消息格式

**服务端推送**:
```json
{
  "type": "progress",
  "data": {
    "step": "clone",
    "progress": 50,
    "message": "正在转换第 5/10 个片段"
  }
}
```

**完成通知**:
```json
{
  "type": "completed",
  "data": {
    "resultId": 1,
    "outputUrl": "/results/1/output.mp3"
  }
}
```

**错误通知**:
```json
{
  "type": "error",
  "data": {
    "code": "API_ERROR",
    "message": "外部API调用失败"
  }
}
```

---

## 4. 任务处理流程

### 4.1 完整克隆流程

```python
@celery.task(bind=True)
def clone_voice_task(self, task_id: int):
    task = CloneTask.get(task_id)
    
    try:
        # Step 1: 检查人声分离
        update_progress(task_id, "separate", 0)
        if not task.song.vocals_path:
            # 调用外部API
            await separate_vocals(task.song.id)
        update_progress(task_id, "separate", 100)
        
        # Step 2: 歌词对齐 (本地CPU)
        update_progress(task_id, "align", 0)
        lyrics = await align_lyrics(task.song.id, task.song.vocals_path)
        update_progress(task_id, "align", 100)
        
        # Step 3: 音色克隆 (外部API)
        update_progress(task_id, "clone", 0)
        cloned_vocals = await clone_voice(
            vocals_path=task.song.vocals_path,
            voice_id=task.voice_id,
            provider=task.provider,
            on_progress=lambda p: update_progress(task_id, "clone", p)
        )
        update_progress(task_id, "clone", 100)
        
        # Step 4: 音频混合 (本地CPU)
        update_progress(task_id, "mix", 0)
        output_path = await mix_audio(
            vocals_path=cloned_vocals,
            accompaniment_path=task.song.accompaniment_path,
            output_dir=f"results/{task_id}"
        )
        update_progress(task_id, "mix", 100)
        
        # 完成
        task.status = "completed"
        task.output_path = output_path
        task.save()
        
        notify_completed(task_id)
        
    except Exception as e:
        task.status = "failed"
        task.error = str(e)
        task.save()
        notify_error(task_id, str(e))
```

---

## 5. 外部 API 封装

### 5.1 人声分离 API

#### Lalal.ai API

```python
import requests

class LalalAIAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.lalal.ai/api/v1"
    
    async def separate(self, audio_path: str) -> dict:
        # 1. 上传文件
        with open(audio_path, 'rb') as f:
            response = requests.post(
                f"{self.base_url}/upload/",
                headers={"Authorization": f"license {self.api_key}"},
                files={"file": f}
            )
        
        upload_id = response.json()["id"]
        
        # 2. 提交处理任务
        response = requests.post(
            f"{self.base_url}/split/",
            json={"id": upload_id, "filter_type": 1}
        )
        
        # 3. 轮询获取结果
        while True:
            response = requests.get(
                f"{self.base_url}/check/{upload_id}",
                headers={"Authorization": f"license {self.api_key}"}
            )
            data = response.json()
            
            if data["status"] == "done":
                return {
                    "vocals_url": data["vocals"],
                    "accompaniment_url": data["accompaniment"]
                }
            
            await asyncio.sleep(5)
```

#### Spleeter API (HuggingFace 免费)

```python
import requests

class SpleeterAPI:
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/spleeter"
    
    async def separate(self, audio_path: str) -> dict:
        with open(audio_path, 'rb') as f:
            response = requests.post(
                self.api_url,
                files={"file": f}
            )
        
        # 解析返回的文件
        result = response.json()
        return {
            "vocals": result["vocals"],
            "accompaniment": result["accompaniment"]
        }
```

### 5.2 音色克隆 API

#### Replicate RVC API

```python
import replicate

class ReplicateRVC:
    def __init__(self, api_key: str):
        self.client = replicate.Client(api_token=api_key)
    
    async def clone_voice(
        self,
        audio_path: str,
        voice_model: str,
        pitch_shift: int = 0,
        on_progress=None
    ):
        # 创建预测任务
        prediction = self.client.predictions.create(
            version="rvc-model-version",
            input={
                "audio": open(audio_path, "rb"),
                "voice_model": voice_model,
                "pitch_shift": pitch_shift
            }
        )
        
        # 轮询进度
        while prediction.status != "succeeded":
            prediction = self.client.predictions.get(prediction.id)
            
            if on_progress and prediction.logs:
                on_progress(prediction.logs)
            
            if prediction.status == "failed":
                raise Exception(prediction.error)
            
            await asyncio.sleep(1)
        
        return prediction.output
```

---

## 6. 本地处理模块

### 6.1 音频处理服务 (本地 CPU)

```python
from pydub import AudioSegment
import librosa
import numpy as np

class AudioProcessor:
    """本地音频处理服务 (无需GPU)"""
    
    @staticmethod
    def convert_format(input_path: str, output_path: str, format: str = "mp3"):
        """格式转换"""
        audio = AudioSegment.from_file(input_path)
        audio.export(output_path, format=format)
    
    @staticmethod
    def get_duration(audio_path: str) -> float:
        """获取时长"""
        audio = AudioSegment.from_file(audio_path)
        return len(audio) / 1000.0
    
    @staticmethod
    def split_audio(
        input_path: str,
        output_dir: str,
        timestamps: list
    ) -> list:
        """按时间戳切片"""
        audio = AudioSegment.from_file(input_path)
        chunks = []
        
        for i, ts in enumerate(timestamps):
            start_ms = ts["start"] * 1000
            end_ms = ts["end"] * 1000
            chunk = audio[start_ms:end_ms]
            
            chunk_path = f"{output_dir}/chunk_{i}.wav"
            chunk.export(chunk_path, format="wav")
            chunks.append(chunk_path)
        
        return chunks
    
    @staticmethod
    def mix_audio(
        vocals_path: str,
        accompaniment_path: str,
        output_path: str,
        vocals_db: float = 0,
        acc_db: float = -2
    ):
        """混合人声和伴奏"""
        vocals = AudioSegment.from_file(vocals_path)
        accompaniment = AudioSegment.from_file(accompaniment_path)
        
        # 调整音量
        vocals = vocals + vocals_db
        accompaniment = accompaniment + acc_db
        
        # 对齐长度
        min_len = min(len(vocals), len(accompaniment))
        vocals = vocals[:min_len]
        accompaniment = accompaniment[:min_len]
        
        # 混合
        mixed = vocals.overlay(accompaniment)
        mixed.export(output_path, format="mp3", bitrate="320k")
        
        return output_path
```

### 6.2 歌词服务 (本地 CPU)

```python
import re
import torch

class LyricsService:
    """歌词处理服务 (无需GPU)"""
    
    @staticmethod
    def parse_lrc(lrc_content: str) -> list:
        """解析 LRC 格式歌词"""
        pattern = r'\[(\d{2}):(\d{2})[.:](\d{2,3})\](.+)'
        lyrics = []
        
        for line in lrc_content.split('\n'):
            match = re.match(pattern, line)
            if match:
                minutes = int(match.group(1))
                seconds = int(match.group(2))
                milliseconds = int(match.group(3).ljust(3, '0'))
                text = match.group(4).strip()
                
                time = minutes * 60 + seconds + milliseconds / 1000
                lyrics.append({"time": time, "text": text})
        
        return sorted(lyrics, key=lambda x: x["time"])
    
    @staticmethod
    async def auto_align(audio_path: str, lyrics: list) -> list:
        """自动对齐歌词 (使用 Silero VAD)"""
        # 加载 VAD 模型
        model, utils = torch.hub.load(
            'snakers4/silero-vad',
            'silero_vad',
            force_reload=False
        )
        
        # 加载音频
        audio, sr = librosa.load(audio_path, sr=16000)
        
        # 检测语音段落
        audio_tensor = torch.from_numpy(audio)
        timestamps = model.get_speech_timestamps(
            audio_tensor,
            sampling_rate=sr,
            min_silence_duration_ms=300
        )
        
        # 匹配歌词和时间戳
        aligned_lyrics = []
        for i, ts in enumerate(timestamps):
            if i < len(lyrics):
                aligned_lyrics.append({
                    "time": ts["start"] / sr,
                    "text": lyrics[i].get("text", "")
                })
        
        return aligned_lyrics
```

---

## 7. 部署配置

### 7.1 环境变量

```bash
# .env
# API Keys
LALALAI_API_KEY=your_key
REPLICATE_API_KEY=your_key
ELEVENLABS_API_KEY=your_key

# 服务配置
REDIS_URL=redis://localhost:6379
DATABASE_URL=sqlite:///melodyclaw.db

# 文件存储
UPLOAD_DIR=/data/melodyclaw/uploads
OUTPUT_DIR=/data/melodyclaw/results
```

### 7.2 Docker Compose

```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./data:/data/melodyclaw
    depends_on:
      - redis
  
  worker:
    build: .
    command: celery -A app.worker worker -l info
    environment:
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./data:/data/melodyclaw
    depends_on:
      - redis
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./frontend/dist:/usr/share/nginx/html
    depends_on:
      - web

volumes:
  redis_data:
```

---

*文档版本: 2026-03-18*