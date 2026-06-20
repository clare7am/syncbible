function showBook(sel) {
    const info = document.getElementById("info");
    if (sel.value) {
        info.innerText =
            "当前选择：" + sel.options[sel.selectedIndex].text;
    } else {
        info.innerText = "请选择书卷";
    }
}