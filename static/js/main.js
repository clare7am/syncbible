// 页面加载完成后，自动触发一次
window.addEventListener("DOMContentLoaded", () => {
    const bookId = document.getElementById("book").value;
    const chapter = document.getElementById("chapter").value;
    if (bookId && chapter) {
        loadVerses();
    }
});