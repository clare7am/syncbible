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
            chapterSelect.innerHTML = '<option value="">-- 请选择章 --</option>';
            chapters.forEach(ch => {
                const option = document.createElement("option");
                option.value = ch;
                option.innerText = ch;
                chapterSelect.appendChild(option);
            });
            chapterSelect.disabled = false;
        })
        .catch(err => {
            chapterSelect.innerHTML = '<option value="">加载失败</option>';
            console.error(err);
        });

    info.innerText = `已选择：${sel.options[sel.selectedIndex].text}`;
}