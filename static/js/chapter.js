// 章节切换时的逻辑
function onChapterChange(sel) {
    const info = document.getElementById("info");
    const chapter = sel.value;

    if (!chapter) {
        info.innerText = "请选择章节";
        return;
    }

    const bookName = document.getElementById("book").options[
        document.getElementById("book").selectedIndex
    ].text;

    // info.innerText = `当前选择：${bookName} 第 ${chapter} 章`;

    loadVerses();// 重新加载经文
}