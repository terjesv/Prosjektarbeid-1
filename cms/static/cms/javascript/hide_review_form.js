// Hide form at page load
hide_element(document.getElementById('review-form'));

function hide_element(object) {
    object.style.display = "none";
}

function show_element(object) {
    object.style.display = "block";
}

function show_form() {
    form = document.getElementById('review-form');
    button = document.getElementById('show-review-form-button');
    show_element(form);
    hide_element(button);
}