# 常见问题 (FAQ)

## 安装问题

### Q: pip install 失败？

**A:** 尝试以下方法：

```bash
# 方法 1: 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 方法 2: 升级 pip
pip install --upgrade pip

# 方法 3: 分步安装
pip install torch torchaudio
pip install demucs
pip install librosa soundfile pydub
```

### Q: CUDA 相关错误？

**A:** 确保 CUDA 版本匹配：

```bash
# 检查 CUDA 版本
nvidia-smi

# 安装对应版本的 PyTorch
# CUDA 11.8
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Q: 找不到模块？

**A:** 检查 Python 路径：

```bash
# 确保在项目根目录运行
cd /root/melodyclaw
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 或在代码中添加
import sys
sys.path.append("/root/melodyclaw")
```

---

## 人声分离问题

### Q: 分离效果不好？

**A:** 尝试以下方法：

1. **换模型**
```python
# 尝试不同的 Demucs 模型
separate_vocals(song, output, model="htdemucs_ft")  # 快速版
separate_vocals(song, output, model="mdx_extra")    # 高质量版
```

2. **提高质量**
```bash
# 使用 UVR5（需单独安装）
pip install uvr5-cli
uvr5 separate song.mp3 --model MDX23C --output output/
```

### Q: 内存不足？

**A:** 减小处理块大小：

```python
from demucs.apply import apply_model

# 分块处理
apply_model(model, wav, split=True, overlap=0.25)
```

### Q: 处理太慢？

**A:** 
- 使用 GPU
- 使用 htdemucs_ft 模型
- 降低采样率

---

## 分句问题

### Q: 分句不准确？

**A:** 调整 VAD 参数：

```python
segment_vocals(
    vocals_path,
    output_dir,
    min_silence_ms=500,   # 增大静音阈值
    min_speech_ms=1000,   # 增大最小语音长度
    padding_ms=100        # 增加填充
)
```

### Q: 句子被切断？

**A:** 
- 检查原始人声质量
- 调整 padding_ms
- 使用歌词文件辅助分句

---

## 音色转换问题

### Q: 找不到 RVC 模型？

**A:** 
1. **使用预训练模型**
   - 从社区下载 .pth 文件
   - 放入 `models/rvc/` 目录

2. **自己训练**
```bash
python scripts/train_rvc.py --audio your_voice.wav
```

### Q: 转换后音质差？

**A:** 
1. **调整音高检测方法**
```python
converter = VoiceConverter(
    model_path,
    config=ConversionConfig(
        pitch_detection="rmvpe"  # 尝试: crepe, pm, harvest
    )
)
```

2. **调整音高偏移**
```python
converter.convert(input, output, pitch_shift=2)  # 升 2 个半音
```

3. **检查训练数据质量**

### Q: 声音不像目标音色？

**A:** 
- 增加训练数据量
- 确保训练数据干净
- 尝试不同的 epoch 检查点
- 调整 rms_mix_rate

---

## 混合问题

### Q: 人声和伴奏对不上？

**A:** 
- 确保使用同一首歌分离出的人声和伴奏
- 检查采样率是否一致
- 使用时间对齐工具

### Q: 音量不均衡？

**A:** 调整音量：

```python
mix_audio(
    vocals_path,
    acc_path,
    output_path,
    vocals_db=2,   # 提高人声
    acc_db=-3,     # 降低伴奏
    normalize=True
)
```

### Q: 输出音质差？

**A:** 
- 使用 WAV 格式输出
- 提高采样率
- 检查原始音频质量

---

## 性能问题

### Q: GPU 利用率低？

**A:** 
- 增大 batch_size
- 检查数据加载瓶颈
- 使用多线程数据加载

### Q: 处理一首歌要多久？

**A:** 参考时间（RTX 3060, 3分钟歌曲）：

| 步骤 | 时间 |
|------|------|
| 人声分离 | 45秒 |
| 分句 | 10秒 |
| 音色转换 | 90秒 |
| 混合 | 5秒 |
| **总计** | **~2.5分钟** |

---

## 其他问题

### Q: 支持哪些音频格式？

**A:** 
- 输入: MP3, WAV, FLAC, OGG, AAC
- 输出: WAV, MP3, FLAC

### Q: 可以商用吗？

**A:** 
- MelodyClaw 代码: MIT License（可商用）
- RVC 模型: 遵循 RVC 项目许可
- 注意目标音色的版权问题

### Q: 如何报告问题？

**A:** 
1. 检查本文档
2. 搜索 Issues
3. 提交新 Issue，包含：
   - 错误信息
   - 系统环境
   - 复现步骤