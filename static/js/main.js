window.Bible = {
    book: null,
    chapter: null
};

window.addEventListener("DOMContentLoaded", () => {
    const bookSelect = document.getElementById("book");
    const chapterSelect = document.getElementById("chapter");

    if (!bookSelect || !chapterSelect) return;

    Bible.book = bookSelect.value;
    Bible.chapter = chapterSelect.value;

    // ✅ 关键：手动触发一次，让章节列表完整加载
    onBookChange(bookSelect);
});