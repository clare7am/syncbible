/**
 * 清除所有高亮
 */
function clearWordHighlight() {
    document.querySelectorAll('.word.active')
        .forEach(el => el.classList.remove('active'));
}

/**
 * 根据当前时间（毫秒）高亮单词
 * @param {number} currentTimeMs
 */
function highlightWordAt(currentTimeMs) {
    clearWordHighlight();

    document.querySelectorAll('.word').forEach(el => {
        const start = Number(el.dataset.start);
        const end   = Number(el.dataset.end);

        if (!start || !end) return;

        if (currentTimeMs >= start && currentTimeMs < end) {
            el.classList.add('active');
            el.scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });
        }
    });
}