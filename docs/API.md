# API 文档

## 概述

MelodyClaw 提供两种使用方式：

1. **命令行工具** - 适合批量处理
2. **Python API** - 适合集成到其他项目

## 命令行工具

### 1. 人声分离

```bash
python src/separator.py \
    --input song.mp3 \
    --output output/separator \
    --model htdemucs \
    --device cuda
```

**参数说明**:
- `--input, -i`: 输入音频文件（必需）
- `--output, -o`: 输出目录（默认: `output/separator`）
- `--model, -m`: 模型名称（默认: `htdemucs`）
- `--device, -d`: 计算设备（默认: `cuda`）

### 2. 人声分句

```bash
python src/segmenter.py \
    --input vocals.wav \
    --output output/segments \
    --lyrics song.lrc
```

**参数说明**:
- `--input, -i`: 人声文件（必需）
- `--output, -o`: 输出目录（默认: `output/segments`）
- `--lyrics, -l`: 歌词文件（LRC 格式，可选）

### 3. 音色转换

```bash
python src/converter.py \
    --input vocals.wav \
    --output converted.wav \
    --model models/rvc/voice.pth \
    --pitch 0
```

**参数说明**:
- `--input, -i`: 输入音频（必需）
- `--output, -o`: 输出音频（必需）
- `--model, -m`: RVC 模型路径（必需）
- `--pitch, -p`: 音高偏移，半音（默认: 0）

### 4. 音频混合

```bash
python src/mixer.py \
    --vocals converted.wav \
    --accompaniment accompaniment.wav \
    --output final.mp3 \
    --vocals-db 0 \
    --acc-db -2
```

**参数说明**:
- `--vocals, -v`: 人声文件（必需）
- `--accompaniment, -a`: 伴奏文件（必需）
- `--output, -o`: 输出文件（必需）
- `--vocals-db`: 人声音量调整（默认: 0）
- `--acc-db`: 伴奏音量调整（默认: -2）

---

## Python API

### 完整流程

```python
from src import VoiceCloner

# 创建克隆器
cloner = VoiceCloner(
    separator_model="htdemucs",
    converter_model="models/rvc/target_voice.pth",
    device="cuda"
)

# 执行克隆
result = cloner.clone(
    song_path="input/song.mp3",
    output_path="output/final.mp3",
    pitch_shift=0  # 音高偏移（半音）
)

print(f"输出文件: {result}")
```

### 单独模块

#### 人声分离

```python
from src.separator import separate_vocals

# 分离人声和伴奏
vocals_path, acc_path = separate_vocals(
    input_path="song.mp3",
    output_dir="output/separator",
    model="htdemucs",
    device="cuda"
)

print(f"人声: {vocals_path}")
print(f"伴奏: {acc_path}")
```

#### 人声分句

```python
from src.segmenter import segment_vocals

# 分句切分
segments = segment_vocals(
    vocals_path="vocals.wav",
    output_dir="output/segments",
    min_silence_ms=300,
    min_speech_ms=500
)

for seg in segments:
    print(f"片段 {seg.index}: {seg.start_time:.2f}s - {seg.end_time:.2f}s")
```

#### 音色转换

```python
from src.converter import VoiceConverter, convert_voice

# 方式 1: 单次转换
convert_voice(
    input_path="chunk_000.wav",
    output_path="converted_000.wav",
    model_path="models/rvc/voice.pth",
    pitch_shift=0
)

# 方式 2: 批量转换
converter = VoiceConverter("models/rvc/voice.pth")
output_paths = converter.convert_batch(
    input_dir="output/segments",
    output_dir="output/converted",
    pitch_shift=0
)
```

#### 音频混合

```python
from src.mixer import mix_audio, concatenate_audio

# 混合人声和伴奏
mix_audio(
    vocals_path="converted.wav",
    accompaniment_path="accompaniment.wav",
    output_path="final.mp3",
    vocals_db=0,
    acc_db=-2,
    normalize=True
)

# 连接多个音频片段
concatenate_audio(
    audio_files=["chunk_001.wav", "chunk_002.wav", "chunk_003.wav"],
    output_path="combined.wav",
    crossfade_ms=50
)
```

---

## 批量处理

### 批量转换多首歌曲

```python
from pathlib import Path
from src import VoiceCloner

cloner = VoiceCloner(
    converter_model="models/rvc/singer.pth"
)

# 处理目录下所有歌曲
input_dir = Path("input_songs")
output_dir = Path("output_songs")

for song in input_dir.glob("*.mp3"):
    output_path = output_dir / f"{song.stem}_converted.mp3"
    
    try:
        cloner.clone(
            song_path=str(song),
            output_path=str(output_path),
            pitch_shift=2  # 升 2 个半音
        )
        print(f"✓ 完成: {song.name}")
    except Exception as e:
        print(f"✗ 失败: {song.name} - {e}")
```

### 使用配置文件

```python
import yaml
from src import VoiceCloner

# 加载配置
with open("config/config.yaml") as f:
    config = yaml.safe_load(f)

# 创建克隆器
cloner = VoiceCloner(
    separator_model=config["separator"]["model"],
    converter_model="models/rvc/voice.pth",
    device=config["separator"]["device"]
)

# 执行克隆
cloner.clone("song.mp3", "output.mp3")
```

---

## API 服务（可选扩展）

如需部署为 API 服务，可使用 FastAPI：

```python
from fastapi import FastAPI, UploadFile, File
from src import VoiceCloner

app = FastAPI(title="MelodyClaw API")

@app.post("/clone")
async def clone_voice(
    song: UploadFile = File(...),
    voice_model: str = "default",
    pitch_shift: int = 0
):
    """歌声克隆接口"""
    
    # 保存上传文件
    song_path = f"temp/{song.filename}"
    with open(song_path, "wb") as f:
        f.write(await song.read())
    
    # 执行克隆
    output_path = f"output/{song.filename}"
    cloner = VoiceCloner(converter_model=f"models/rvc/{voice_model}.pth")
    result = cloner.clone(song_path, output_path, pitch_shift)
    
    return {"output": result}

# 运行: uvicorn api:app --host 0.0.0.0 --port 8000
```