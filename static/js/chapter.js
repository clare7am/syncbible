function onChapterChange(sel) {
    const info = document.getElementById("info");
    const chapter = sel.value;

    if (!chapter) {
        if (info) info.innerText = "请选择章节";
        return;
    }

    const bookSelect = document.getElementById("book");
    const bookName = bookSelect.options[bookSelect.selectedIndex].text;

    // 更新全局状态
    Bible.book = bookSelect.value;
    Bible.chapter = chapter;

    loadVerses();      // 经文
    updateAudio();    // 音频
}