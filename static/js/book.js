// 书卷切换时，动态加载章节
function onBookChange(sel) {
    const bookId = sel.value;
    const chapterSelect = document.getElementById("chapter");
    const info = document.getElementById("info");

    // 清空章节下拉
    chapterSelect.innerHTML = '<option value="">加载中...</option>';
    chapterSelect.disabled = true;

    if (!bookId) {
        chapterSelect.innerHTML = '<option value="">请先选书卷</option>';
        info.innerText = "请选择书卷";
        return;
    }

    // 请求后端获取章节列表
    fetch(`/chapters/${bookId}`)
        .then(res => res.json())
        .then(chapters => {
            chapterSelect.innerHTML = '';  // 不再插入 "-- 请选择章 --"
            chapters.forEach(item => {
                const option = document.createElement("option");
                option.value = item.chapter;

                // 优先使用 chapter_title
                option.innerText = item.chapter_title?.trim()
                    ? item.chapter_title
                    : item.chapter;

                chapterSelect.appendChild(option);
            });
            chapterSelect.disabled = false;

            // 默认选中第一章（数字最小）
            const firstChapter = chapters[0]?.chapter;
            chapterSelect.value = firstChapter;
            onChapterChange(chapterSelect);
        })
        .catch(err => {
            chapterSelect.innerHTML = '<option value="">加载失败</option>';
            console.error(err);
        });

    // nfo.innerText = `已选择：${sel.options[sel.selectedIndex].text}`;

    loadVerses();// 重新加载经文
}