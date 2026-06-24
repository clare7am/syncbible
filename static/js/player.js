const audio = document.getElementById('audio-player');
const progress = document.getElementById('progress');
const playPauseBtn = document.getElementById('play-pause-btn');

// 暂时写死这一章（以后可以改成变量）
const AUDIO_URL = '/static/audio/Mt_1_en.m4a';

// 页面加载完就设好路径
window.addEventListener('DOMContentLoaded', () => {
    audio.src = AUDIO_URL;
});

function togglePlay() {
    if (audio.paused) {
        audio.play();
    } else {
        audio.pause();
    }
}

function stopAudio() {
    audio.pause();
    audio.currentTime = 0;
}

/* 拖动或点击进度条跳转 */
progress.addEventListener('input', () => {
    if (!audio.duration) return;
    audio.currentTime = (progress.value / 100) * audio.duration;
});

/* 播放时同步进度条 */
audio.addEventListener('timeupdate', () => {
    if (audio.duration) {
        progress.value = (audio.currentTime / audio.duration) * 100;
    }
});

/* 播放暂停按钮 */
audio.addEventListener('play', () => {
    playPauseBtn.textContent = '⏸ 暂停';
});

audio.addEventListener('pause', () => {
    playPauseBtn.textContent = '▶ 播放';
});

audio.addEventListener('ended', () => {
    playPauseBtn.textContent = '▶ 播放';
});

/* 高亮 */
audio.addEventListener('timeupdate', () => {
    const ms = Math.floor(audio.currentTime * 1000);
    highlightWordAt(ms);
});

/* 进度条 */
audio.addEventListener('timeupdate', () => {
    if (audio.duration) {
        progress.value = (audio.currentTime / audio.duration) * 100;
    }
});