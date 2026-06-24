const audio = document.getElementById('audio-player');
const progress = document.getElementById('progress');

// 暂时写死这一章（以后可以改成变量）
const AUDIO_URL = '/static/audio/Mt_1_en.ogg';

// 页面加载完就设好路径
window.addEventListener('DOMContentLoaded', () => {
    audio.src = AUDIO_URL;
});

function playAudio() {
    audio.play();
}

function pauseAudio() {
    audio.pause();
}

function stopAudio() {
    audio.pause();
    audio.currentTime = 0;
}

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