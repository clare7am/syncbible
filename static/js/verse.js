// verse.js

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

    // 先判断是否有分词数据
    fetch(`/has_tokens/${bookId}/${chapter}`)
        .then(res => res.json())
        .then(flag => {
            if (flag.has_tokens) {
                loadTokenVerses(bookId, chapter, container);
            } else {
                loadPlainVerses(bookId, chapter, container);
            }
        })
        .catch(err => {
            container.innerHTML = "<p>加载失败</p>";
            console.error(err);
        });
}

/* ================= 有分词：流式渲染优化版 ================= */
function loadTokenVerses(bookId, chapter, container) {
    container.innerHTML = '<div class="loading">正在加载经文...</div>';

    fetch(`/verses_with_words/${bookId}/${chapter}`)
        .then(res => res.json())
        .then(data => {
            if (data.length === 0) {
                container.innerHTML = "<p>暂无经文</p>";
                return;
            }

            container.innerHTML = "";
            let index = 0;
            const BATCH_SIZE = 3; 

            function renderBatch() {
                const fragment = document.createDocumentFragment();
                console.log(`正在渲染第 ${index + 1} 到 ${index + BATCH_SIZE} 节`);

                for (let i = 0; i < BATCH_SIZE && index < data.length; i++, index++) {
                    const v = data[index];

                    const verseBlock = document.createElement("div");
                    verseBlock.className = "verse-block";

                    const verseNum = document.createElement("div");
                    verseNum.className = "verse-num";
                    verseNum.textContent = v.verse;

                    const verseText = document.createElement("div");
                    verseText.className = "verse-text";

                    // ✅ 生成单词
                    v.words.forEach(w => {
                        const span = document.createElement("span");
                        span.className = w.type || '';
                        span.textContent = w.word; // 重点：恢复单词内容
                        span.dataset.alignId = w.align_id;
                        span.dataset.start = w.start;
                        span.dataset.end = w.end;
                        if (w.entity_key) {
                            span.dataset.entityKey = w.entity_key;
                        }
                        verseText.appendChild(span);
                    });

                    const verseCn = document.createElement("div");
                    verseCn.className = "verse-cn";
                    verseCn.textContent = v.text_cn;

                    verseBlock.appendChild(verseNum);
                    verseBlock.appendChild(verseText);
                    verseBlock.appendChild(verseCn);
                    
                    fragment.appendChild(verseBlock);
                }

                container.appendChild(fragment);

                if (index < data.length) {
                    requestAnimationFrame(renderBatch);
                }
            }
            renderBatch();
        });
}

/* ================= 无分词：兜底逻辑 ================= */
function loadPlainVerses(bookId, chapter, container) {
    fetch(`/verses/${bookId}/${chapter}`)
        .then(res => res.json())
        .then(data => {
            if (data.length === 0) {
                container.innerHTML = "<p>暂无经文</p>";
                return;
            }

            container.innerHTML = data.map(v => `
                <div class="verse-block">
                    <div class="verse-num">${v.verse}</div>
                    <div class="verse-text">${v.text_en}</div>
                    <div class="verse-cn">${v.text_cn}</div>
                </div>
            `).join('');
        });
}