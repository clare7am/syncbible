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

    if (Bible.book && Bible.chapter) {
        loadVerses();
        if (typeof updateAudio === "function") {
            updateAudio();
        }
    }
});