// verse.js

// 监听书卷和章节变化，自动加载经文
function loadVerses() {
    const bookSelect = document.getElementById("book");
    const chapterSelect = document.getElementById("chapter");
    const container = document.getElementById("verses");

    const bookId = Number(bookSelect.value);
    const chapter = Number(chapterSelect.value);

    if (!bookId || !chapter) {
        container.innerHTML = "";
        return;
    }

    container.innerHTML = "<p>加载中...</p>";

    // ✅ 非 Genesis 书卷，继续走数据库判断
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
    bookId = Number(bookId);
    chapter = Number(chapter);

    container.innerHTML = '<div class="loading">正在加载经文...</div>';

    // ✅ 只要 bookId 是 1（Genesis），就直接读静态 JSON
    let url;
    if (bookId === 1) {
        const ch = String(chapter).padStart(3, "0");
        url = `/static/json/01_Gen_${ch}.json`;
    } else {
        url = `/verses_with_words/${bookId}/${chapter}`;
    }

    console.log("📖 经文来源：", url);

    fetch(url)
        .then(async res => {
            if (!res.ok) {
                throw new Error(`HTTP ${res.status}: ${url}`);
            }
            return res.json();
        })
        .then(data => {
            console.log("✅ 原始 JSON：", data);

            // ✅ 安全取值（兼容对象和数组结构）
            const verses = Array.isArray(data)
                ? data
                : (Array.isArray(data.verses) ? data.verses : []);

            console.log("✅ verses 数量：", verses.length);

            if (verses.length === 0) {
                container.innerHTML = "<p>暂无经文</p>";
                return;
            }

            container.innerHTML = "";
            let index = 0;
            const BATCH_SIZE = 3;

            function renderBatch() {
                const fragment = document.createDocumentFragment();

                for (let i = 0; i < BATCH_SIZE && index < verses.length; i++, index++) {
                    const v = verses[index];

                    // ✅ 防止 verse / words 不存在
                    if (!v || !Array.isArray(v.words)) {
                        continue;
                    }

                    const verseBlock = document.createElement("div");
                    verseBlock.className = "verse-block";

                    const verseNum = document.createElement("div");
                    verseNum.className = "verse-num";
                    verseNum.textContent = v.verse ?? "";

                    const verseText = document.createElement("div");
                    verseText.className = "verse-text";

                    v.words.forEach(w => {
                        if (!w || !w.word) return;

                        const span = document.createElement("span");
                        span.className = w.type || '';
                        span.textContent = w.word;
                        span.dataset.alignId = w.align_id || "";
                        span.dataset.start = w.start || 0;
                        span.dataset.end = w.end || 0;
                        if (w.entity_key) {
                            span.dataset.entityKey = w.entity_key;
                        }
                        verseText.appendChild(span);
                    });

                    const verseCn = document.createElement("div");
                    verseCn.className = "verse-cn";
                    verseCn.textContent = v.text_cn || "";

                    verseBlock.appendChild(verseNum);
                    verseBlock.appendChild(verseText);
                    verseBlock.appendChild(verseCn);

                    fragment.appendChild(verseBlock);
                }

                container.appendChild(fragment);

                if (index < verses.length) {
                    requestAnimationFrame(renderBatch);
                }
            }

            renderBatch();
        })
        .catch(err => {
            container.innerHTML = "<p>加载失败</p>";
            console.error("❌ 经文加载错误：", err);
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
        })
        .catch(err => {
            container.innerHTML = "<p>加载失败</p>";
            console.error(err);
        });
}