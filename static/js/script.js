$(document).ready(function () {
    $('.dropdown-toggle').dropdown();
});


$(".dropdown-menu a ").click(function () {
    let popup = $(this).text();
    alert(popup);
});

// $( document ).ready(function() {
    // $('.dropdown').each(function (key, dropdown) {
        // var $dropdown = $(dropdown);
        // $dropdown.find('.dropdown-menu a').on('click', function () {
            // $dropdown.find('button').text($(this).text()).append(' <span class="caret"></span>');
        // });
    // });
// });