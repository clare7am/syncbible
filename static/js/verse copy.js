// =====================
// 配置：阿里云 OSS JSON 基础地址
// =====================
const OSS_JSON_BASE = "https://c7-json.oss-cn-beijing.aliyuncs.com";

/**
 * 生成阿里云 OSS JSON 外链
 * 格式：{base}/{02位书卷ID}_{英文缩写}_{03位章节}.json
 */
function getOssJsonUrl(bookId, chapter) {
    const abbr = getAbbr(bookId);
    const bookStr = String(bookId).padStart(2, "0");
    const chapterStr = String(chapter).padStart(3, "0");
    return `${OSS_JSON_BASE}/${bookStr}_${abbr}_${chapterStr}.json`;
}

// =====================
// 书卷缩写映射
// =====================
function getAbbr(bookId) {
    const MAP = {
        1:"Gen",2:"Ex",3:"Lev",4:"Num",5:"Dt",
        6:"Jos",7:"Jdg",8:"Ru",9:"1S",10:"2S",
        11:"1K",12:"2K",13:"1Chr",14:"2Chr",
        15:"Ezra",16:"Ne",17:"Tb",18:"Jdt",19:"Es",
        20:"1Mac",21:"2Mac",22:"Job",23:"Ps",24:"Pro",
        25:"Ecl",26:"Song",27:"Wis",28:"Sir",29:"Is",
        30:"Jer",31:"Lm",32:"Bar",33:"Ezk",34:"Dn",
        35:"Hos",36:"Jl",37:"Am",38:"Ob",39:"Jon",
        40:"Mic",41:"Nh",42:"Hb",43:"Zep",44:"Hg",
        45:"Zec",46:"Mal",47:"Mt",48:"Mk",49:"Lk",
        50:"Jn",51:"Acts",52:"Rom",53:"1Cor",54:"2Cor",
        55:"Gal",56:"Eph",57:"Phil",58:"Col",59:"1Thes",
        60:"2Thes",61:"1Tim",62:"2Tim",63:"Tit",64:"Phlm",
        65:"Heb",66:"Jas",67:"1P",68:"2P",69:"1Jn",
        70:"2Jn",71:"3Jn",72:"Jd",73:"Rev"
    };
    return MAP[bookId] || "";
}

// =====================
// 监听书卷和章节变化
// =====================
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

    // ✅ 优先使用阿里云 OSS JSON 外链
    const ossUrl = getOssJsonUrl(bookId, chapter);
    loadJsonVerses(ossUrl, container);
}

// =====================
// 直接读取 OSS JSON 外链
// =====================
function loadJsonVerses(url, container) {
    console.log("📖 使用 OSS JSON：", url);

    fetch(url)
        .then(res => {
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return res.json();
        })
        .then(data => {
            const verses = Array.isArray(data.verses) ? data.verses : [];
            if (verses.length === 0) {
                container.innerHTML = "<p>暂无经文</p>";
                return;
            }
            renderVerses(verses, container);
        })
        .catch(err => {
            container.innerHTML = "<p>加载失败</p>";
            console.error("❌ JSON 加载错误：", err);
        });
}

// =====================
// 公共渲染函数（保持不变）
// =====================
function renderVerses(verses, container) {
    container.innerHTML = "";
    let index = 0;
    const BATCH_SIZE = 3;

    function renderBatch() {
        const fragment = document.createDocumentFragment();

        for (let i = 0; i < BATCH_SIZE && index < verses.length; i++, index++) {
            const v = verses[index];
            if (!v || !Array.isArray(v.words)) continue;

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
}