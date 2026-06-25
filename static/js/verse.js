// 监听书卷和章节变化，自动加载经文
function loadVerses() {
    const bookId = document.getElementById("book").value;
    const chapter = document.getElementById("chapter").value;
    const container = document.getElementById("verses");

    if (!bookId || !chapter) {
        container.innerHTML = "";
        return;
    }

    container.innerHTML = "<p>加载中...</p>";

    fetch(`/verses_with_words/${bookId}/${chapter}`)
        .then(res => res.json())
        .then(data => {
            if (data.length === 0) {
                container.innerHTML = "<p>暂无经文</p>";
                return;
            }

container.innerHTML = data.map(v => {
    const wordsHtml = v.words.map(w =>
        `<span class="${w.type||''}"
            data-align-id="${w.align_id}"
            data-start="${w.start}"
            data-end="${w.end}"
            ${w.entity_key ? `data-entity-key="${w.entity_key}"` : ''}
        >${w.word}</span>`
    ).join('');

    return `
    <div class="verse-block">
        <div class="verse-num">${v.verse}</div>
        <div class="verse-text">${wordsHtml}</div>
        <div class="verse-cn">${v.text_cn}</div>
    </div>
    `;
}).join('');
            if (typeof applyEntityStyles === "function") {
                applyEntityStyles();
            }
        })
        .catch(err => {
            container.innerHTML = "<p>加载失败</p>";
            console.error(err);
        });
} 