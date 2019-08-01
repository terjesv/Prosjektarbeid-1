function hide_element(object) {
    object.style.display = "none";
}

function show_element(object) {
    object.style.display = "block";
}

function get_dropdown_content() {
    // returns a list (of the names) of every category selected in the dropdown
    let dropdown_html_collection = $("#dropdown")[0].selectedOptions;
    let selected_categories = [];

    for (var i = 0; i < dropdown_html_collection.length; i++) {
        selected_categories.push(dropdown_html_collection[i].textContent);
    }
    return selected_categories;
}

function filterPosts() {
    let postList = $(".post-container");
    let chosen_categories = get_dropdown_content();

    for (var i = 0; i < postList.length; i++) {
        show_element(postList[i]);
        let post_categories_list = postList[i].children[2].innerText.split(" "); // [2] = placement of the categories within the posts div
        for (var j = 0; j < chosen_categories.length; j++) {
            if (! post_categories_list.includes(chosen_categories[j])) {
                hide_element(postList[i]);
                break;
            }
        }
    }
}

