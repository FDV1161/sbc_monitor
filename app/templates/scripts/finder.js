function search_sbc() {
    // Функция поиска одноплатника по ключевым символам из списка одноплатников
    var input, filter, li, a, i, txtValue;
    input = document.getElementById('search_sbc');
    filter = input.value.toUpperCase();
    li = document.getElementById("sidebar_list").getElementsByClassName("list_element");
    for (i = 0; i < li.length; i++) {
        a = li[i].getElementsByTagName("div")[0];
        txtValue = a.textContent || a.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            li[i].style.display = "";
        } else {
            li[i].style.display = "none";
        }
    }
}

function search_sbc_2() {
    // Функция поиска одноплатника по ключевым символам из списка одноплатников
    var input, filter, li, a, i, txtValue;
    input = document.getElementById('search_sbc2');
    filter = input.value.toUpperCase();
    li = document.getElementById("sidebar_list2").getElementsByClassName("list_element");
    for (i = 0; i < li.length; i++) {
        a = li[i].getElementsByTagName("div")[0];
        txtValue = a.textContent || a.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            li[i].style.display = "";
        } else {
            li[i].style.display = "none";
        }
    }
}


