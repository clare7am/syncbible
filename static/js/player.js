const audio = document.getElementById('audio-player');
const progress = document.getElementById('progress');
const playPauseBtn = document.getElementById('play-pause-btn');

/* 书卷缩写映射 */
const BOOK_ABBR = {
    12: '2K',
    47: 'Mt',
    
    52: 'Rom'
};

/* ✅ 只从全局状态读 */
function getAudioUrl() {
    console.log('🔍 [Player.js 内部] 读取到的全局状态 Bible.book:', Bible.book);
    console.log('🔍 [Player.js 内部] 读取到的全局状态 Bible.chapter:', Bible.chapter);

    const abbr = BOOK_ABBR[Bible.book];
    if (!abbr || !Bible.chapter) return null;

    return `https://clare7am-audio.oss-cn-hangzhou.aliyuncs.com/${abbr}_${Bible.chapter}_en.m4a`;
}

/* ✅ 统一入口：章节切换时调用 */
function updateAudio() {
    const url = getAudioUrl();

    console.log('🎧 当前音频地址:', url);

    if (!url) {
        audio.removeAttribute('src');
        progress.value = 0;
        console.warn('⚠️ 没有生成音频地址');
        return;
    }

    audio.pause();
    audio.currentTime = 0;
    progress.value = 0;

    audio.src = url;
    audio.load();

    audio.addEventListener('error', () => {
        console.error('❌ 音频加载失败', audio.error);
    });

    audio.addEventListener('canplay', () => {
        console.log('✅ 音频已准备好播放');
    });
}

/* 播放 / 暂停 */
function togglePlay() {
    if (!audio.src) return;
    audio.paused ? audio.play() : audio.pause();
}

function stopAudio() {
    audio.pause();
    audio.currentTime = 0;
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

    const ms = Math.floor(audio.currentTime * 1000);
    highlightWordAt(ms);
});

const iconPlay  = document.getElementById('icon-play');
const iconPause = document.getElementById('icon-pause');

/* 播放器按钮 */
audio.addEventListener('play', () => {
    if (iconPlay && iconPause) {
        iconPlay.style.display  = 'none';
        iconPause.style.display = 'block';
    }
});

audio.addEventListener('pause', () => {
    if (iconPlay && iconPause) {
        iconPlay.style.display  = 'block';
        iconPause.style.display = 'none';
    }
});

audio.addEventListener('ended', () => {
    if (iconPlay && iconPause) {
        iconPlay.style.display  = 'block';
        iconPause.style.display = 'none';
    }
});