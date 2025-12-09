// EDITOR DASHBOARD
$('body').on('click', '.create_journal_btn', function (e) {
    e.preventDefault();
    let url = $('.create_journal_btn').data('url');
    $.ajax({
        type: 'GET',
        url: url,
        success: function (response) {
            $('#create_journal_div').html(response);
            $('#create_journal_modal').modal('show');
        },
        error: function (error) {
            console.log("Xatolik");
            console.log(error);
        }
    });
});

$('body').on('click', '.resultBtnUnReview', function (e) {
    e.preventDefault();
    let data = $(this).data('id');
    let article_id = parseInt(data.split(',')[0]);
    let notif_id = parseInt(data.split(',')[1]);
    let btn_number = parseInt(data.split(',')[2]);
    let csrftoken = getCookie('csrftoken');
    let text = $('#resubmit_or_reject_text').val();


    if (text.length > 0) {
        let url = $('.resultBtnUnReview').data('url');
        let reload_url = $('.resultBtnUnReview').data('action');
        $.ajax({
            type: "POST",
            url: url,
            data: {
                article_id: article_id,
                notif_id: notif_id,
                text: text,
                btn_number: btn_number,
                csrfmiddlewaretoken: csrftoken,
            },
            success: function (response) {
                setTimeout(check_editor_reload(reload_url), 1000);
            },
            error: function (error) {
                console.log(error);
            }
        });

    } else {
        alert("Izohni kiriting!");
    }

});


$('body').on('click', '.resubmit_to_reviewer_btn', function (e) {
    e.preventDefault();

    let data = $(this).data('id');
    let id = parseInt(data.split(',')[0]);

    let url = $('#editor_resubmit_to_reviewer_form' + id).data('url');
    let reload_url = $('.resultBtnUnReview').data('action');

    $.ajax({
        type: "POST",
        url: url,
        headers: {
            "X-CSRFToken": getCookie("csrftoken")  // JavaScript orqali cookie'dan token olish
        },
        data: {
            review_id: id,
        },
        success: function (response) {
            $('#resubmit_to_reviewer_btn_' + id).prop("disabled", true);
            setTimeout(check_editor_reload(reload_url), 1000);
            swal({
                title: response.message,
                timer: 1500,
            });
        },
        error: function (error) {
            console.log(error);
        }
    });

});


$('body').on('click', '.resultBtn', function (e) {
    e.preventDefault();

    let data = $(this).data('id');
    let article_id = parseInt(data.split(',')[0]);
    let notif_id = parseInt(data.split(',')[1]);
    let btn_number = parseInt(data.split(',')[2]);
    let csrftoken = getCookie('csrftoken');

    let url = $('.approve_form').data('url');

    let reload_url = $(this).data('action');


    if (btn_number === 2) {
        let text = $('#resubmit_text').val();
        if (text.length > 0) {
            $.ajax({
                type: "POST",
                url: url,
                data: {
                    article_id: article_id,
                    notif_id: notif_id,
                    text: text,
                    btn_number: btn_number,
                    csrfmiddlewaretoken: csrftoken,
                },
                success: function (response) {
                    $('#approveForPublicationBtn').prop("disabled", true);
                    setTimeout(check_editor_reload(reload_url), 1000);

                    swal({
                        title: response.message,
                        timer: 1500,
                    });

                },
                error: function (error) {
                    console.log(error);
                }
            });

        } else {
            alert("Izohni kiriting!");
        }
    }

    if (btn_number === 0 || btn_number === 1 || btn_number === 3) {
        $.ajax({
            type: "POST",
            url: url,
            data: {
                article_id: article_id,
                notif_id: notif_id,
                btn_number: btn_number,
                csrfmiddlewaretoken: csrftoken,
            },
            success: function (response) {
                $('#approveForPublicationBtn').prop("disabled", true);

                setTimeout(check_editor_reload(reload_url), 1000);

                swal({
                    title: response.message,
                    timer: 1500,
                });
            },
            error: function (error) {
                console.log(error);
            }
        });
    }

});


$('body').on('click', '#random_send_reviewer_btn', function (e) {
    e.preventDefault();

    let data = $(this).data('id');
    let id = parseInt(data.split(',')[0]);
    let notif_id = parseInt(data.split(',')[1]);
    let csrftoken = getCookie('csrftoken');

    let value = $('#reviewer_number').val();
    let url = $('.random_sending_reviewer_form').data('url');

    let reload_url = $(this).data('action');

    if (value > 0) {
        $.ajax({
            type: "POST",
            url: url,
            data: {
                value: value,
                article_id: id,
                csrfmiddlewaretoken: csrftoken,
            },
            success: function (response) {
                if (response.is_valid) {
                    $('#send_btn_to_reviewer').prop("disabled", true);
                    $('#random_send_reviewer_btn').prop("disabled", true);

                    setTimeout(check_editor_reload(reload_url), 1000);
                    swal({
                        title: response.message,
                        timer: 1500,
                    });
                } else {
                    alert(response.message);
                }
            },
            error: function (error) {
                console.log(error);
            }
        });
    } else {
        alert("Taqrizchilar sonini kiriting!")
    }
});

$('body').on('click', '#send_btn_to_reviewer', function (e) {
    e.preventDefault();

    let data = $(this).data('id');
    let article_id = parseInt(data.split(',')[0]);
    let notif_id = parseInt(data.split(',')[1]);
    let csrftoken = getCookie('csrftoken');
    let url = $('#choose_reviewer_form').data('url');
    let reload_url = $(this).data('action');

    let selected = [];
    $('#widget-todolist-body input[type=checkbox]').each(function () {
        if ($(this).is(":checked")) {
            selected.push($(this).val());
        }
    });

    let n = selected.length;

    if (n === 0) {
        alert("Taqrizchi tanlamadiz!");
    }

    if (n >= 1) {
        $.ajax({
            type: "POST",
            url: url,
            data: {
                reviewers: selected,
                csrfmiddlewaretoken: csrftoken,
                article_id: article_id
            },
            success: function (response) {
                if (response.is_valid) {
                    $('#send_btn_to_reviewer').prop("disabled", true);
                    $('#random_btn').prop("disabled", true);
                    setTimeout(check_editor_reload(reload_url), 1000);

                    swal({
                        title: response.message,
                        timer: 1500,
                    });
                } else {
                    alert(response.message);
                }
            },
            error: function (error) {
                console.log(error);
            }

        });
    }

});


$('body').on('click', '#view-article-messages-by-editor', function (e) {
    e.preventDefault();

    let url = $('#view-article-messages-by-editor').data('url');
    let id = $(this).data('id');

    $.ajax({
        type: "GET",
        url: url,
        success: function (response) {
            $('#MessageBoxEditor').css('display', 'block');
            $('#editor_chat_body').empty();

            for (let item of response.notifications) {

                let time_tz = new Date(item.created_at);
                let time_string = time_tz.toLocaleString();

                if (response.current_user_id === item.from_user__id) {

                    let temp1 = `<div class="widget-chat-item right"><div class="widget-chat-info"><div class="widget-chat-info-container">
                                        <div class="widget-chat-name text-indigo">`
                        + item.from_user__email +
                        `</div><div class="widget-chat-message">` + `<i style="color: #0a6aa1">(${item.to_user__email}).</i>`
                        + item.message +
                        `</div><div class="widget-chat-time">`
                        + time_string +`</div> <br><br><div class="widget-chat-ansewer"></div></div></div></div>`;

                    $('#editor_chat_body').append(temp1);
                }

                if (response.current_user_id === item.to_user__id) {

                    let temp2 = `<div class="widget-chat-item left"><div class="widget-chat-info"><div class="widget-chat-info-container"><div class="widget-chat-name text-indigo">`
                        + item.from_user__email +
                        `</div><div class="widget-chat-message">` + `<i style="color: #0a6aa1">(${item.to_user__email}).</i>` + item.message + `</div><div class="widget-chat-time">` + time_string + `</div><br><div class="widget-chat-ansewer">
                                                <button type="button" data-url="${response.url}${id}/${item.from_user__id}/" class="btn btn-white btn-sm editorWrite-message-btn">Ansewer</button></div></div></div></div>`;
                    $('#editor_chat_body').append(temp2);
                }
            }

        },
        error: function (response) {
            console.log(response);
        }
    });

});

$('body').on('click', '.editorWrite-message-btn', function (e) {
    e.preventDefault();

    const url = $(this).data('url');

    $.ajax({
        type: 'GET',
        url: url,
        success: function (response) {
            $('#writeeditor_message_div').html(response);
            $('#send-message-modal').modal('show');
        },
        error: function (error) {
            console.log("Xatolik");
            console.log(error);
        }
    });
});

$('body').on('click', '.article_view_editor', function (e) {
    e.preventDefault();

    let url = $(this).data('url');

    $.ajax({
        type: "GET",
        url: url,
        success: function (response) {
            $('.editor_dashboard').empty();
            $('.editor_dashboard').html(response);
        },
        error: function (response) {
        }
    });
});

$('body').on('click', '.choose_type_sumit_btn', function (e) {
    e.preventDefault();

    let btn_id = $(this).data('id');

    if (btn_id == 1) {
        $('#list_reviewers').css("display", "block");
        $('#random_btn').css("display", "none");

        let url = $('.choose_type_sumit_btn').data('url');

        $.ajax({
            type: 'GET',
            url: url,
            success: function (response) {
                $('#widget-todolist-body').empty();
                $('#count_reviewer').html("<span>" + response.reviewers.length + "</span>");


                for (let item of response.reviewers) {
                    let widget_item = `<div class="widget-todolist-item">` +
                        `<div class="widget-todolist-input"><div class="checkbox checkbox-css pt-0">` +
                        `<input type="checkbox" id="widget_todolist_${item.id}" name="reviewer_checkbox" value="${item.id}"/><label for="widget_todolist_${item.id}" class="p-l-15">&nbsp;</label></div></div>` +
                        `<div class="widget-todolist-content"><h4 class="widget-todolist-title">` + item.user__last_name + " " + item.user__first_name + " " + item.user__middle_name +
                        `</h4><p class="widget-todolist-desc"><b>Email:</b>${item.user__email}</p></div><div class="widget-todolist-icon"><p class="widget-todolist-desc">${item.scientific_degree__name}</p></div><div class="widget-todolist-icon">
											<a href="#"><i class="fa fa-question-circle"></i></a></div>`
                        + `</div>`;

                    $('#widget-todolist-body').append(widget_item);
                }
            },
            error: function (error) {
                console.log("Xatolik");
                console.log(error);
            }
        });
    }

    if (btn_id == 2) {
        $('#list_reviewers').css("display", "none");
        $('#random_btn').css("display", "block");
    }

});

function check_editor_reload(url) {
    $.ajax({
        type: "GET",
        url: url,
        success: function (response) {
            $('.editor_dashboard').empty();
            $('.editor_dashboard').html(response);
        },
        error: function (response) {
        }
    });
}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}