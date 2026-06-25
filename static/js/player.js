const audio = document.getElementById('audio-player');
const progress = document.getElementById('progress');
const playPauseBtn = document.getElementById('play-pause-btn');

const iconPlay = document.getElementById('icon-play');
const iconPause = document.getElementById('icon-pause');

/* =========================
   书卷 → 音频文件名映射
   ========================= */
const BOOK_ABBR = {
    12: '2K',
    47: 'Mt',
    52: 'Rom'
};

/* =========================
   生成当前章节音频 URL
   ========================= */
function getAudioUrl() {
    const abbr = BOOK_ABBR[Bible.book];
    if (!abbr || !Bible.chapter) return null;
    return `https://clare7am-audio.oss-cn-hangzhou.aliyuncs.com/${abbr}_${Bible.chapter}_en.m4a`;
}

/* =========================
   同步播放按钮 SVG（唯一真理）
   ========================= */
function syncPlayButtonIcon() {
    if (!iconPlay || !iconPause) return;

    if (audio.paused || audio.ended) {
        iconPlay.style.display = 'block';
        iconPause.style.display = 'none';
    } else {
        iconPlay.style.display = 'none';
        iconPause.style.display = 'block';
    }
}

/* =========================
   启用播放器
   ========================= */
function enablePlayer() {
    playPauseBtn.disabled = false;
    progress.disabled = false;
    playPauseBtn.classList.remove('disabled');
}

/* =========================
   禁用播放器（无音频）
   ========================= */
function disablePlayer() {
    playPauseBtn.disabled = true;
    progress.disabled = true;
    playPauseBtn.classList.add('disabled');

    audio.pause();
    audio.removeAttribute('src');
    audio.load();
    // ✅ 不手动改 SVG，由 pause 事件接管
}

/* =========================
   章节切换时统一入口
   ========================= */
function updateAudio() {
    const url = getAudioUrl();

    // 清理 UI
    progress.value = 0;
    clearWordHighlight();

    // ✅ 先暂停
    audio.pause();
    audio.currentTime = 0;

    // ✅ 强制回到“播放态”图标（关键）
    if (iconPlay && iconPause) {
        iconPlay.style.display = 'block';
        iconPause.style.display = 'none';
    }

    // 无音频
    if (!url) {
        disablePlayer();
        console.warn('⚠️ 本章节无音频');
        return;
    }

    enablePlayer();
    audio.src = url;
    audio.load();

    audio.addEventListener('error', () => {
        disablePlayer();
        console.error('❌ 音频加载失败');
    }, { once: true });

    audio.addEventListener('canplay', () => {
        enablePlayer();
        console.log('✅ 音频已就绪');
    }, { once: true });
}

/* =========================
   播放 / 暂停（受保护）
   ========================= */
function togglePlay() {
    if (playPauseBtn.disabled || !audio.src) return;
    audio.paused ? audio.play() : audio.pause();
}

/* =========================
   进度条拖动
   ========================= */
progress.addEventListener('input', () => {
    if (!audio.duration) return;
    audio.currentTime = (progress.value / 100) * audio.duration;
});

/* =========================
   播放进度 + 高亮
   ========================= */
audio.addEventListener('timeupdate', () => {
    if (audio.duration) {
        progress.value = (audio.currentTime / audio.duration) * 100;
    }
    highlightWordAt(Math.floor(audio.currentTime * 1000));
});

/* =========================
   播放状态 → 按钮 SVG
   ========================= */
audio.addEventListener('play', syncPlayButtonIcon);
audio.addEventListener('pause', syncPlayButtonIcon);
audio.addEventListener('ended', () => {
    audio.currentTime = 0;
    progress.value = 0;
    syncPlayButtonIcon();
});