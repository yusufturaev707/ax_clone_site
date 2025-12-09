function validateEmail(email) {
    let regex = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
    return regex.test(email);
}

const formValidate = array => {

    let is_validRForm = true;

    $('.text-danger').hide();

    for (let index = 0; index < array.length; index++) {
        let key = array[index].key;
        let value = array[index].value;
        let message = array[index].message;


        if (key == 'email') {
            if (value == "") {
                $('.' + key).after('<span class="text-danger"> Iltimos e-mailizni kiriting </span>');
                is_validRForm = false;
            } else if (!validateEmail(value)) {
                $('.' + key).after('<span class="text-danger"> Iltimos to\'gri e-mail kiriting</span>');
                is_validRForm = false;
            }
        } else {

            if (value == '') {
                $('.' + key).after('<span class="text-danger text-small">' + message + 'ni kiriting!</span>');
                is_validRForm = false;
            }
        }

    }

    return is_validRForm
};

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


$('body').on('click', '.change_pass_btn', function (e) {
    e.preventDefault();

    let id_old_password = $('#id_old_password').val().toString().trim();
    let id_new_password1 = $('#id_new_password1').val().toString().trim();
    let id_new_password2 = $('#id_new_password2').val().toString().trim();


    let data = [{key: 'id_old_password', value: id_old_password, message: "Eski parol"},
        {key: 'id_new_password1', value: id_new_password1, message: "Yangi parol"},
        {key: 'id_new_password2', value: id_new_password2, message: "Yangi parol"},
    ]

    let is_valid_registerForm = formValidate(data);

    if (is_valid_registerForm) {
        let url = $('#change_password_form').data('url');
        $.ajax({
            method: "POST",
            url: url,
            data: $('#change_password_form').serialize(),
            success: function (response) {
                if (response.result === 'ok') {
                    $('#change_password_form')[0].reset();
                    $('#change_password_page_info').empty();
                    $('#change_password_page_info').html(`<div class="alert alert-success forshadow" style="text-align: center">
                        <strong>Muvafaqqiyat!</strong>Sizni joriy paroliz yangisiga muvafaqqiyatli o'zgartirildi.
                    </div>`);
                } else {
                    $('#change_password_page_info').empty();
                    $('#change_password_page_info').html(`<div class="alert alert-danger forshadow" style="text-align: center">
                        <strong>Diqqat!</strong>Siz kiritgan joriy parol xato yoki yangi parol biri ikkinchisiga mos emas.
                    </div>`);
                }
            },
        });
    }
});

$('body').on('click', '.loginBtn', function (e) {
    e.preventDefault();

    let is_valid_form = formValidateLogin();
    if (is_valid_form) {
        let url = $('.loginForm').data('url');
        $.ajax({
            method: "POST",
            url: url,
            data: $('.loginForm').serialize(),
            success: function (response) {
                if (response.message) {
                    if (response['is_captcha'] === false){
                         $('#loginFormError').html("<span class='text-danger text-center'>" + response.message + "</span>");
                    }
                    if (response['is_captcha'] === true) {
                        $('#id_captcha_1').after('<br><span class="text-danger">' + response.message +'</span>');
                    }
                } else {
                    window.location.reload();
                }
            },
        });
    }

    function formValidateLogin() {

        let username = $('.usernameLogin').val();
        let password = $('.passwordLogin').val();

        let inputValue = new Array(username, password);

        let inputMessage = new Array("Login", "Parol");

        let is_valid = true;

        $('.text-danger').hide();

        if (inputValue[0] == "") {
            $('.usernameLogin').after('<span class="text-danger">' + inputMessage[0] + 'ni kiritng</span>');
            is_valid = false;
        }

        if (inputValue[1] == "") {
            $('.passwordLogin').after('<span class="text-danger">' + inputMessage[1] + 'ni kiritng</span>');
            is_valid = false
        }

        return is_valid;
    }
});

$('body').on('click', '.captcha', function (e) {
    e.preventDefault();
    $.getJSON("/captcha/refresh/", function (result) {
        $('.captcha').attr('src', result['image_url']);
        $('#id_captcha_0').val(result['key']);
    });
});


$('body').on('submit', '.editProfileForm', function (e) {
    e.preventDefault();

    // let last_name = $('.last_name').val();
    // let first_name = $('.first_name').val();
    // let middle_name = $('.middle_name').val();
    let username = $('.username').val();
    // let email = $('.email').val();
    // let birthday = $('.birthday').val();
    // let region = $('.region').val();
    // let gender = $('.gender').val();
    let phone = $('.phone').val();
    // let pser = $('.pser').val();
    // let pnum = $('.pnum').val();
    let work = $('.work').val();
    // let jshshr = $('.jshshr').val();
    let sc_degree = $('.sc_degree').val();

    let dataEdit = [
        // {key: 'last_name', value: last_name, message: "Familiya"},
        // {key: 'first_name', value: first_name, message: "Ism"},
        // {key: 'middle_name', value: middle_name, message: "Otangizning ismi"},
        {key: 'username', value: username, message: "Login"},
        // {key: 'email', value: email, message: ""},
        // {key: 'birthday', value: birthday, message: "Tug'ilgan kun"},
        // {key: 'region', value: region, message: "Viloyat"},
        // {key: 'gender', value: gender, message: "Jins"},
        {key: 'phone', value: phone, message: "Telefon nomer"},
        // {key: 'pser', value: pser, message: "Pasport seriya"},
        // {key: 'pnum', value: pnum, message: "Pasport nomer"},
        {key: 'work', value: work, message: "Ish joyingiz"},
        // {key: 'jshshr', value: jshshr, message: "JSHSHIR"},
        {key: 'sc_degree', value: sc_degree, message: "Ilmiy darajangiz"},
    ];


    let is_valid_form = formValidate(dataEdit);

    if (is_valid_form) {

        const $myProfileForm = $('.editProfileForm');
        const $formData = $myProfileForm.serialize();
        const $thisURL = $myProfileForm.attr('data-url')
        let formData = new FormData(this);

        $.ajax({
            method: "POST",
            url: $thisURL,
            data: formData,
            cache: false,
            contentType: false,
            processData: false,
            success: function (response) {
                swal({
                    title: response.message,
                    timer: 1500,
                });
                if (response.status) {
                    window.location.reload();
                }
            },
        });
    }
});

$('body').on('click', '#choose-role-reviewer-btn', function (e) {
    e.preventDefault();

    let url = $('#choose-role-reviewer-btn').data('url');

    $.ajax({
        type: 'GET',
        url: url,
        success: function (response) {
            $('#choosen_reviewer_role_div').html(response);
            $('#choosen_reviewerRole').modal('show');
        },
        error: function (error) {
            alert(error);
        },
    });
});

$('body').on('submit', '#choosen_reviewerRole_form', function (e) {
    e.preventDefault();
    let formData = new FormData(this);
    let url = $('#choosen_reviewerRole_form').data('url');
    $.ajax({
        type: 'POST',
        url: url,
        data: formData,
        contentType: false,
        processData: false,
        success: function (response) {
            swal({
                title: response.message,
                timer: 1500,
            });
            if (response.result) {
                window.location.reload();
            }
        },
        error: function (error) {
            alert("Error");
        },
    });
});
