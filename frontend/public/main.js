/**
 * MelodyClaw - 歌声小龙虾前端交互
 * 
 * 功能：
 * 1. 歌词滚动显示
 * 2. 小龙虾动画（根据歌词/节奏反应）
 * 3. 音频播放控制
 * 4. 响应式适配
 */

// ==========================================
// 配置
// ==========================================
const CONFIG = {
    // 歌词显示配置
    lyrics: {
        visibleLines: 5,          // 可见歌词行数
        scrollDuration: 500,       // 滚动动画时长 (ms)
        highlightScale: 1.05,      // 高亮行缩放
    },
    // 小龙虾动画配置
    lobster: {
        bubbleInterval: 500,       // 气泡生成间隔 (ms)
        noteInterval: 800,         // 音符生成间隔 (ms)
        singingClass: 'singing',
        happyClass: 'happy',
    },
    // 动画配置
    animation: {
        idleFloat: true,           // 空闲时浮动
        reactionDelay: 100,        // 反应延迟 (ms)
    }
};

// ==========================================
// 全局状态
// ==========================================
const state = {
    audioFile: null,
    clonedAudioFile: null,
    lyrics: [],
    currentLyricIndex: -1,
    isPlaying: false,
    audioContext: null,
    analyser: null,
    dataArray: null,
};

// ==========================================
// DOM 元素
// ==========================================
const elements = {
    // 音频
    audioPlayer: document.getElementById('audioPlayer'),
    clonedAudioPlayer: document.getElementById('clonedAudioPlayer'),
    
    // 文件输入
    audioFile: document.getElementById('audioFile'),
    lyricsFile: document.getElementById('lyricsFile'),
    clonedAudioFile: document.getElementById('clonedAudioFile'),
    
    // 按钮
    playBtn: document.getElementById('playBtn'),
    pauseBtn: document.getElementById('pauseBtn'),
    stopBtn: document.getElementById('stopBtn'),
    
    // 进度
    progressFill: document.getElementById('progressFill'),
    currentTime: document.getElementById('currentTime'),
    totalTime: document.getElementById('totalTime'),
    volumeSlider: document.getElementById('volumeSlider'),
    
    // 歌词
    lyricsContainer: document.getElementById('lyricsContainer'),
    lyricsScroll: document.getElementById('lyricsScroll'),
    currentLyric: document.getElementById('currentLyric'),
    
    // 小龙虾
    lobster: document.getElementById('lobster'),
    lobsterStage: document.getElementById('lobsterStage'),
    bubbles: document.getElementById('bubbles'),
};

// ==========================================
// 歌词解析器
// ==========================================
class LyricsParser {
    /**
     * 解析 LRC 格式歌词
     * @param {string} lrcContent - LRC 文件内容
     * @returns {Array} 歌词数组 [{time, text}]
     */
    static parse(lrcContent) {
        const lines = lrcContent.split('\n');
        const lyrics = [];
        
        // LRC 时间格式: [mm:ss.xx] 或 [mm:ss:xx]
        const timeRegex = /\[(\d{2}):(\d{2})[.:](\d{2,3})\]/g;
        
        for (const line of lines) {
            // 跳过元数据行
            if (line.startsWith('[ti:') || line.startsWith('[ar:') || 
                line.startsWith('[al:') || line.startsWith('[by:') ||
                line.trim() === '') {
                continue;
            }
            
            // 提取时间标签
            const matches = [...line.matchAll(timeRegex)];
            
            if (matches.length > 0) {
                // 提取歌词文本（移除时间标签）
                const text = line.replace(timeRegex, '').trim();
                
                // 一个时间标签对应一句歌词
                for (const match of matches) {
                    const minutes = parseInt(match[1], 10);
                    const seconds = parseInt(match[2], 10);
                    const milliseconds = parseInt(match[3].padEnd(3, '0'), 10);
                    
                    // 转换为秒
                    const time = minutes * 60 + seconds + milliseconds / 1000;
                    
                    if (text) {
                        lyrics.push({ time, text });
                    }
                }
            }
        }
        
        // 按时间排序
        lyrics.sort((a, b) => a.time - b.time);
        
        return lyrics;
    }
    
    /**
     * 根据时间获取当前歌词索引
     * @param {Array} lyrics - 歌词数组
     * @param {number} currentTime - 当前时间（秒）
     * @returns {number} 歌词索引
     */
    static getCurrentIndex(lyrics, currentTime) {
        if (!lyrics.length) return -1;
        
        // 二分查找
        let left = 0;
        let right = lyrics.length - 1;
        
        while (left <= right) {
            const mid = Math.floor((left + right) / 2);
            
            if (lyrics[mid].time <= currentTime) {
                if (mid === lyrics.length - 1 || lyrics[mid + 1].time > currentTime) {
                    return mid;
                }
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        
        return -1;
    }
}

// ==========================================
// 歌词显示控制器
// ==========================================
class LyricsController {
    constructor(container, scrollElement) {
        this.container = container;
        this.scrollElement = scrollElement;
        this.lyrics = [];
        this.currentIndex = -1;
        this.lyricElements = [];
    }
    
    /**
     * 设置歌词
     * @param {Array} lyrics - 歌词数组
     */
    setLyrics(lyrics) {
        this.lyrics = lyrics;
        this.currentIndex = -1;
        this.lyricElements = [];
        
        // 清空容器
        this.scrollElement.innerHTML = '';
        
        // 创建歌词元素
        for (let i = 0; i < lyrics.length; i++) {
            const line = document.createElement('div');
            line.className = 'lyric-line future';
            line.textContent = lyrics[i].text;
            line.dataset.index = i;
            
            // 点击歌词跳转
            line.addEventListener('click', () => {
                if (elements.audioPlayer.src) {
                    elements.audioPlayer.currentTime = lyrics[i].time;
                }
            });
            
            this.scrollElement.appendChild(line);
            this.lyricElements.push(line);
        }
    }
    
    /**
     * 更新歌词显示
     * @param {number} currentTime - 当前时间（秒）
     */
    update(currentTime) {
        const newIndex = LyricsParser.getCurrentIndex(this.lyrics, currentTime);
        
        if (newIndex !== this.currentIndex) {
            this.currentIndex = newIndex;
            this.highlightLyric(newIndex);
        }
    }
    
    /**
     * 高亮指定歌词
     * @param {number} index - 歌词索引
     */
    highlightLyric(index) {
        // 移除所有高亮
        this.lyricElements.forEach((el, i) => {
            el.classList.remove('active', 'past', 'future');
            
            if (i < index) {
                el.classList.add('past');
            } else if (i === index) {
                el.classList.add('active');
            } else {
                el.classList.add('future');
            }
        });
        
        // 滚动到当前歌词
        if (index >= 0 && this.lyricElements[index]) {
            const element = this.lyricElements[index];
            const containerHeight = this.container.clientHeight;
            const elementTop = element.offsetTop;
            const elementHeight = element.clientHeight;
            
            // 计算滚动位置（将当前歌词居中）
            const scrollTop = elementTop - containerHeight / 2 + elementHeight / 2;
            
            this.scrollElement.style.transform = `translateY(-${scrollTop}px)`;
            
            // 更新底部当前歌词显示
            elements.currentLyric.textContent = this.lyrics[index].text;
            elements.currentLyric.classList.add('visible');
        } else {
            elements.currentLyric.classList.remove('visible');
        }
    }
    
    /**
     * 重置歌词显示
     */
    reset() {
        this.currentIndex = -1;
        this.lyricElements.forEach(el => {
            el.classList.remove('active', 'past');
            el.classList.add('future');
        });
        this.scrollElement.style.transform = 'translateY(0)';
        elements.currentLyric.classList.remove('visible');
    }
}

// ==========================================
// 小龙虾动画控制器
// ==========================================
class LobsterController {
    constructor(lobsterElement, stageElement, bubblesElement) {
        this.lobster = lobsterElement;
        this.stage = stageElement;
        this.bubbles = bubblesElement;
        this.isSinging = false;
        this.bubbleTimer = null;
        this.noteTimer = null;
    }
    
    /**
     * 开始唱歌动画
     */
    startSinging() {
        if (this.isSinging) return;
        this.isSinging = true;
        
        this.lobster.classList.add(CONFIG.lobster.singingClass);
        
        // 开始生成气泡
        this.startBubbles();
        
        // 开始生成音符
        this.startNotes();
    }
    
    /**
     * 停止唱歌动画
     */
    stopSinging() {
        if (!this.isSinging) return;
        this.isSinging = false;
        
        this.lobster.classList.remove(CONFIG.lobster.singingClass);
        this.lobster.classList.remove(CONFIG.lobster.happyClass);
        
        // 停止气泡
        if (this.bubbleTimer) {
            clearInterval(this.bubbleTimer);
            this.bubbleTimer = null;
        }
        
        // 停止音符
        if (this.noteTimer) {
            clearInterval(this.noteTimer);
            this.noteTimer = null;
        }
    }
    
    /**
     * 开始生成气泡
     */
    startBubbles() {
        this.bubbleTimer = setInterval(() => {
            this.createBubble();
        }, CONFIG.lobster.bubbleInterval);
    }
    
    /**
     * 创建单个气泡
     */
    createBubble() {
        const bubble = document.createElement('div');
        bubble.className = 'bubble';
        
        // 随机位置和大小
        const size = 5 + Math.random() * 10;
        const left = -30 + Math.random() * 60;
        
        bubble.style.width = `${size}px`;
        bubble.style.height = `${size}px`;
        bubble.style.left = `${left}%`;
        
        this.bubbles.appendChild(bubble);
        
        // 动画结束后移除
        setTimeout(() => {
            bubble.remove();
        }, 2000);
    }
    
    /**
     * 开始生成音符
     */
    startNotes() {
        this.noteTimer = setInterval(() => {
            this.createNote();
        }, CONFIG.lobster.noteInterval);
    }
    
    /**
     * 创建单个音符
     */
    createNote() {
        const notes = ['♪', '♫', '♬', '♩'];
        const note = document.createElement('div');
        note.className = 'music-note';
        note.textContent = notes[Math.floor(Math.random() * notes.length)];
        
        // 随机位置
        const left = 30 + Math.random() * 40;
        note.style.left = `${left}%`;
        note.style.top = '30%';
        
        this.stage.appendChild(note);
        
        // 动画结束后移除
        setTimeout(() => {
            note.remove();
        }, 2000);
    }
    
    /**
     * 设置高兴状态
     */
    setHappy(isHappy) {
        if (isHappy) {
            this.lobster.classList.add(CONFIG.lobster.happyClass);
        } else {
            this.lobster.classList.remove(CONFIG.lobster.happyClass);
        }
    }
    
    /**
     * 点击互动
     */
    onClick() {
        this.setHappy(true);
        setTimeout(() => {
            this.setHappy(false);
        }, 1000);
    }
}

// ==========================================
// 音频分析器
// ==========================================
class AudioAnalyzer {
    constructor() {
        this.audioContext = null;
        this.analyser = null;
        this.dataArray = null;
        this.source = null;
    }
    
    /**
     * 初始化音频分析
     * @param {HTMLAudioElement} audioElement - 音频元素
     */
    init(audioElement) {
        // 创建音频上下文
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        
        // 创建分析器
        this.analyser = this.audioContext.createAnalyser();
        this.analyser.fftSize = 256;
        
        // 创建数据数组
        this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);
        
        // 连接音频源
        this.source = this.audioContext.createMediaElementSource(audioElement);
        this.source.connect(this.analyser);
        this.analyser.connect(this.audioContext.destination);
    }
    
    /**
     * 获取频率数据
     * @returns {Uint8Array} 频率数据
     */
    getFrequencyData() {
        if (!this.analyser) return null;
        this.analyser.getByteFrequencyData(this.dataArray);
        return this.dataArray;
    }
    
    /**
     * 获取平均音量
     * @returns {number} 平均音量 (0-255)
     */
    getAverageVolume() {
        const data = this.getFrequencyData();
        if (!data) return 0;
        
        let sum = 0;
        for (let i = 0; i < data.length; i++) {
            sum += data[i];
        }
        return sum / data.length;
    }
    
    /**
     * 获取节奏强度（低频部分）
     * @returns {number} 节奏强度 (0-255)
     */
    getBeatIntensity() {
        const data = this.getFrequencyData();
        if (!data) return 0;
        
        // 只取低频部分（约前 1/4）
        let sum = 0;
        const beatRange = Math.floor(data.length / 4);
        for (let i = 0; i < beatRange; i++) {
            sum += data[i];
        }
        return sum / beatRange;
    }
}

// ==========================================
// 主控制器
// ==========================================
class MelodyClawApp {
    constructor() {
        this.lyricsController = new LyricsController(
            elements.lyricsContainer,
            elements.lyricsScroll
        );
        
        this.lobsterController = new LobsterController(
            elements.lobster,
            elements.lobsterStage,
            elements.bubbles
        );
        
        this.audioAnalyzer = new AudioAnalyzer();
        
        this.init();
    }
    
    /**
     * 初始化应用
     */
    init() {
        this.bindEvents();
        this.initVolume();
        
        // 小龙虾点击互动
        elements.lobster.addEventListener('click', () => {
            this.lobsterController.onClick();
        });
        
        console.log('🦞 MelodyClaw 初始化完成');
    }
    
    /**
     * 绑定事件
     */
    bindEvents() {
        // 文件选择
        elements.audioFile.addEventListener('change', (e) => this.handleAudioFile(e));
        elements.lyricsFile.addEventListener('change', (e) => this.handleLyricsFile(e));
        elements.clonedAudioFile.addEventListener('change', (e) => this.handleClonedAudioFile(e));
        
        // 播放控制
        elements.playBtn.addEventListener('click', () => this.play());
        elements.pauseBtn.addEventListener('click', () => this.pause());
        elements.stopBtn.addEventListener('click', () => this.stop());
        
        // 音频事件
        elements.audioPlayer.addEventListener('timeupdate', () => this.updateProgress());
        elements.audioPlayer.addEventListener('loadedmetadata', () => this.updateDuration());
        elements.audioPlayer.addEventListener('ended', () => this.handleEnded());
        elements.audioPlayer.addEventListener('play', () => this.handlePlay());
        elements.audioPlayer.addEventListener('pause', () => this.handlePause());
        
        // 进度条点击
        document.querySelector('.progress-bar').addEventListener('click', (e) => this.seek(e));
        
        // 音量控制
        elements.volumeSlider.addEventListener('input', (e) => this.setVolume(e.target.value));
        
        // 键盘控制
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
    }
    
    /**
     * 处理音频文件
     */
    handleAudioFile(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        state.audioFile = file;
        
        // 创建 URL
        const url = URL.createObjectURL(file);
        elements.audioPlayer.src = url;
        
        // 启用播放按钮
        this.enableControls();
        
        console.log('🎵 加载音频:', file.name);
    }
    
    /**
     * 处理歌词文件
     */
    handleLyricsFile(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = (e) => {
            const content = e.target.result;
            const lyrics = LyricsParser.parse(content);
            
            state.lyrics = lyrics;
            this.lyricsController.setLyrics(lyrics);
            
            console.log('📝 加载歌词:', lyrics.length, '行');
        };
        reader.readAsText(file);
    }
    
    /**
     * 处理克隆音频文件
     */
    handleClonedAudioFile(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        state.clonedAudioFile = file;
        const url = URL.createObjectURL(file);
        elements.clonedAudioPlayer.src = url;
        
        console.log('🎤 加载克隆音频:', file.name);
    }
    
    /**
     * 播放
     */
    play() {
        if (!elements.audioPlayer.src) return;
        
        // 首次播放时初始化音频分析
        if (!this.audioAnalyzer.analyser) {
            this.audioAnalyzer.init(elements.audioPlayer);
        }
        
        elements.audioPlayer.play();
        
        // 同时播放克隆音频（如果有）
        if (elements.clonedAudioPlayer.src) {
            elements.clonedAudioPlayer.currentTime = elements.audioPlayer.currentTime;
            elements.clonedAudioPlayer.play();
        }
    }
    
    /**
     * 暂停
     */
    pause() {
        elements.audioPlayer.pause();
        
        if (elements.clonedAudioPlayer.src) {
            elements.clonedAudioPlayer.pause();
        }
    }
    
    /**
     * 停止
     */
    stop() {
        elements.audioPlayer.pause();
        elements.audioPlayer.currentTime = 0;
        
        if (elements.clonedAudioPlayer.src) {
            elements.clonedAudioPlayer.pause();
            elements.clonedAudioPlayer.currentTime = 0;
        }
        
        this.lyricsController.reset();
    }
    
    /**
     * 处理播放开始
     */
    handlePlay() {
        state.isPlaying = true;
        elements.playBtn.disabled = true;
        elements.pauseBtn.disabled = false;
        elements.stopBtn.disabled = false;
        
        // 开始小龙虾动画
        this.lobsterController.startSinging();
        
        // 开始音频分析循环
        this.startAnalysisLoop();
    }
    
    /**
     * 处理暂停
     */
    handlePause() {
        state.isPlaying = false;
        elements.playBtn.disabled = false;
        elements.pauseBtn.disabled = true;
        
        // 停止小龙虾动画
        this.lobsterController.stopSinging();
    }
    
    /**
     * 处理播放结束
     */
    handleEnded() {
        state.isPlaying = false;
        elements.playBtn.disabled = false;
        elements.pauseBtn.disabled = true;
        
        this.lobsterController.stopSinging();
        this.lyricsController.reset();
    }
    
    /**
     * 更新进度
     */
    updateProgress() {
        const currentTime = elements.audioPlayer.currentTime;
        const duration = elements.audioPlayer.duration;
        
        if (duration) {
            const progress = (currentTime / duration) * 100;
            elements.progressFill.style.width = `${progress}%`;
            elements.currentTime.textContent = this.formatTime(currentTime);
            
            // 更新歌词
            if (state.lyrics.length > 0) {
                this.lyricsController.update(currentTime);
            }
        }
    }
    
    /**
     * 更新总时长
     */
    updateDuration() {
        elements.totalTime.textContent = this.formatTime(elements.audioPlayer.duration);
    }
    
    /**
     * 跳转
     */
    seek(event) {
        if (!elements.audioPlayer.duration) return;
        
        const rect = event.target.getBoundingClientRect();
        const percent = (event.clientX - rect.left) / rect.width;
        const time = percent * elements.audioPlayer.duration;
        
        elements.audioPlayer.currentTime = time;
        
        if (elements.clonedAudioPlayer.src) {
            elements.clonedAudioPlayer.currentTime = time;
        }
    }
    
    /**
     * 设置音量
     */
    setVolume(value) {
        const volume = value / 100;
        elements.audioPlayer.volume = volume;
        
        if (elements.clonedAudioPlayer.src) {
            elements.clonedAudioPlayer.volume = volume;
        }
    }
    
    /**
     * 初始化音量
     */
    initVolume() {
        this.setVolume(elements.volumeSlider.value);
    }
    
    /**
     * 启用控制
     */
    enableControls() {
        elements.playBtn.disabled = false;
    }
    
    /**
     * 开始音频分析循环
     */
    startAnalysisLoop() {
        const analyze = () => {
            if (!state.isPlaying) return;
            
            // 获取节奏强度
            const beatIntensity = this.audioAnalyzer.getBeatIntensity();
            
            // 根据节奏调整小龙虾动画
            if (beatIntensity > 100) {
                this.lobsterController.setHappy(true);
            } else {
                this.lobsterController.setHappy(false);
            }
            
            requestAnimationFrame(analyze);
        };
        
        analyze();
    }
    
    /**
     * 键盘控制
     */
    handleKeyboard(event) {
        switch (event.code) {
            case 'Space':
                event.preventDefault();
                if (state.isPlaying) {
                    this.pause();
                } else {
                    this.play();
                }
                break;
            case 'ArrowLeft':
                elements.audioPlayer.currentTime -= 5;
                break;
            case 'ArrowRight':
                elements.audioPlayer.currentTime += 5;
                break;
            case 'ArrowUp':
                const volUp = Math.min(100, parseInt(elements.volumeSlider.value) + 10);
                elements.volumeSlider.value = volUp;
                this.setVolume(volUp);
                break;
            case 'ArrowDown':
                const volDown = Math.max(0, parseInt(elements.volumeSlider.value) - 10);
                elements.volumeSlider.value = volDown;
                this.setVolume(volDown);
                break;
        }
    }
    
    /**
     * 格式化时间
     */
    formatTime(seconds) {
        if (!isFinite(seconds)) return '0:00';
        
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
}

// ==========================================
// 初始化应用
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    window.app = new MelodyClawApp();
});

// ==========================================
// 服务工作者注册（可选，用于 PWA）
// ==========================================
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // navigator.serviceWorker.register('/sw.js')
        //     .then(reg => console.log('SW registered'))
        //     .catch(err => console.log('SW registration failed'));
    });
}