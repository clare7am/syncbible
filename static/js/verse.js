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

container.innerHTML = data.map(v => `
    <div class="verse-block">
        <div class="verse-num">${v.verse}</div>
        <div class="verse-text">
            ${v.words.map(w => {
                if (w.type === 'person') {
                    return `<span class="person">${w.word}</span>`;
                }
                return `<span>${w.word}</span>`;
            }).join('')}
        </div>
        <div class="verse-cn">${v.text_cn}</div>
    </div>
`).join('');
        })
        .catch(err => {
            container.innerHTML = "<p>加载失败</p>";
            console.error(err);
        });
} 