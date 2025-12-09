$(".userModal").on("click", function (event) {
    event.preventDefault();

    $.get($(this).attr('href'), function (data) {
        $("#show_res").html(data);
        $("#UserModal").modal('toggle');
    });
});

$(".addUser").on("click", function (event) {
    event.preventDefault();

    $.get($(this).attr('href'), function (data) {
        $("#show_res").html(data);
        $("#addUser").modal('toggle');
    });
});