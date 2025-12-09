$('body').on('click', '.reviewerWrite-message-btn', function (e) {
    e.preventDefault();

    const url = $(this).data('url');

    $.ajax({
        type: 'GET',
        url: url,
        success: function (response) {
            $('#write_reviewer_message_div').html(response);
            $('#send-message-modal').modal('show');
        },
        error: function (error) {
            console.log("Xatolik");
            console.log(error);
        }
    });
});

$('body').on('click', '.article_view_reviewer', function (e) {
    e.preventDefault();

    let url = $(this).data('url');

    $.ajax({
        type: "GET",
        url: url,
        success: function (response) {
            $('.dashboard_reviewer').empty();
            $('.dashboard_reviewer').html(response);
        },
        error: function (response) {
        }
    });
});

$('body').on('click', '#resubmit_reviewer_btn', function (e) {
    e.preventDefault();
    const $myForm = $('.sending_editor_form');
    const $formData = $myForm.serialize();

    let url = $('#resubmit_reviewer_btn').data('url');

    let comment = $('#id_comment').val();

    $.ajax({
        type: "POST",
        url: url,
        data: $formData,
        success: function (response) {
            console.log(response.message);
            window.location.reload();
        },
        error: function (error) {
            console.log("Error");
        }
    });
});


$('body').on('click', '#reject_reviewer_btn', function (e) {
    e.preventDefault();
    const $myForm = $('.sending_editor_form');
    const $formData = $myForm.serialize();
    let url = $('#reject_reviewer_btn').data('url');

    let comment = $('#id_comment').val();

    $.ajax({
        type: "POST",
        url: url,
        data: $formData,
        success: function (response) {
            console.log(response.message);
            window.location.reload();
        },
        error: function (error) {
            console.log("Error");
        }
    });
});


$('body').on('click', '#confirm_reviewer_btn', function (e) {
    e.preventDefault();
    const $myForm = $('.sending_editor_form');
    const $formData = $myForm.serialize();

    let url = $('#confirm_reviewer_btn').data('url');

    $.ajax({
        type: "POST",
        url: url,
        data: $formData,
        success: function (response) {
            swal({
                    title: response.message,
                    timer: 1500,
                });
            if (response.result){
                window.location.reload();
            }
        },
        error: function (error) {
            console.log("Error");
        }
    });
});


$('body').on('click', '#view-article-messages-by-reviewer', function (e) {
    e.preventDefault();

    let id = $(this).data('id');
    let url = $('#view-article-messages-by-reviewer').data('url');

    $.ajax({
        type: "GET",
        url: url,
        success: function (response) {
            console.log(response);
            $('#MessageBoxReviewer').css('display', 'block');
            $('#reviewer_chat_body').empty();

            for (let item of response.notifications) {

                let time_tz = new Date(item.created_at);
                let time_string = time_tz.toLocaleString();
                console.log(time_string);

                if (response.current_user_id === item.from_user__id) {

                    let temp1 = `<div class="widget-chat-item right"><div class="widget-chat-info"><div class="widget-chat-info-container"><div class="widget-chat-name text-indigo">`
                        + item.from_user__email +
                        `</div><div class="widget-chat-message">` + `<i style="color: #0a6aa1">(${item.to_user__email}).</i>`
                        + item.message +
                        `</div><div class="widget-chat-time">` + time_string + `</div> <br><br><div class="widget-chat-ansewer"></div></div></div></div>`;

                    $('#reviewer_chat_body').append(temp1);
                }

                if (response.current_user_id === item.to_user__id) {

                    let temp2 = `<div class="widget-chat-item left">
                                        <div class="widget-chat-info">
                                            <div class="widget-chat-info-container">
                                                <div class="widget-chat-name text-indigo">`
                        + item.from_user__email +
                        `</div><div class="widget-chat-message">` + `<i style="color: #0a6aa1">(${item.to_user__email}).</i>`
                        + item.message +
                        `</div><div class="widget-chat-time">` + time_string + `</div>
                                                         <br><div class="widget-chat-ansewer">
                                                            <button type="button" data-url="${response.url}${id}/${item.from_user__id}/" class="btn btn-white btn-sm reviewerWrite-message-btn">Ansewer</button>
                                                        </div>
                                                        </div></div></div>`;
                    $('#reviewer_chat_body').append(temp2);
                }
            }

        },
        error: function (response) {
            console.log(response);
        }
    });

});
