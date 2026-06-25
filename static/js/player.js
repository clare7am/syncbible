const audio = document.getElementById('audio-player');
const progress = document.getElementById('progress');
const playPauseBtn = document.getElementById('play-pause-btn');

const iconPlay = document.getElementById('icon-play');
const iconPause = document.getElementById('icon-pause');

/* 书卷缩写映射 */
const BOOK_ABBR = {
    12: '2K',
    47: 'Mt',
    52: 'Rom'
};

/* ✅ 生成音频 URL（不动） */
function getAudioUrl() {
    const abbr = BOOK_ABBR[Bible.book];
    if (!abbr || !Bible.chapter) return null;
    return `https://clare7am-audio.oss-cn-hangzhou.aliyuncs.com/${abbr}_${Bible.chapter}_en.m4a`;
}

/* ✅ 统一入口：章节切换时调用（核心升级点） */
function updateAudio() {
    const url = getAudioUrl();

    // 重置 UI
    progress.value = 0;
    clearWordHighlight();

    // 暂停当前播放
    audio.pause();
    audio.currentTime = 0;

    // 无 URL = 无音频
    if (!url) {
        disablePlayer();
        console.warn('⚠️ 本书卷/章节无音频');
        return;
    }

    // 先假设“有音频”
    enablePlayer();

    audio.src = url;
    audio.load();

    // ✅ 关键：检测音频是否真的存在
    audio.addEventListener('error', function onError() {
        disablePlayer();
        console.error('❌ 音频加载失败（404 或无权限）');
        audio.removeEventListener('error', onError);
    }, { once: true });

    audio.addEventListener('canplay', function onCanPlay() {
        enablePlayer();
        console.log('✅ 音频已准备好播放');
        audio.removeEventListener('canplay', onCanPlay);
    }, { once: true });
}

/* ✅ 启用播放器 */
function enablePlayer() {
    playPauseBtn.disabled = false;
    progress.disabled = false;
    playPauseBtn.classList.remove('disabled');
}

/* ✅ 禁用播放器（无音频时） */
function disablePlayer() {
    playPauseBtn.disabled = true;
    progress.disabled = true;
    playPauseBtn.classList.add('disabled');

    audio.removeAttribute('src');
    audio.load();

    if (iconPlay && iconPause) {
        iconPlay.style.display = 'block';
        iconPause.style.display = 'none';
    }
}

/* 播放 / 暂停（加一层保护） */
function togglePlay() {
    if (playPauseBtn.disabled || !audio.src) return;
    audio.paused ? audio.play() : audio.pause();
}

/* 进度条拖动 */
progress.addEventListener('input', () => {
    if (!audio.duration) return;
    audio.currentTime = (progress.value / 100) * audio.duration;
});

/* 播放状态同步 + 高亮 */
audio.addEventListener('timeupdate', () => {
    if (audio.duration) {
        progress.value = (audio.currentTime / audio.duration) * 100;
    }
    highlightWordAt(Math.floor(audio.currentTime * 1000));
});

/* 播放器按钮状态 */
audio.addEventListener('play', () => {
    if (iconPlay && iconPause) {
        iconPlay.style.display = 'none';
        iconPause.style.display = 'block';
    }
});

audio.addEventListener('pause', () => {
    if (iconPlay && iconPause) {
        iconPlay.style.display = 'block';
        iconPause.style.display = 'none';
    }
});

audio.addEventListener('ended', () => {
    if (iconPlay && iconPause) {
        iconPlay.style.display = 'block';
        iconPause.style.display = 'none';
    }
});