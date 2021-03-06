$('.message span').click(function() {
    $('form').animate({
        height: "toggle",
        opacity: "toggle"
    }, "slow");
});
$('#submit_login').bind('click', function() {
    $.ajax({
        type : "POST",
        url : '/login/',
        data: JSON.stringify({'username':$('#login-form-username').val(), 'password':$('#login-form-password').val()}),
        contentType: 'application/json;charset=UTF-8',
        success: function(data) {
            var keys = Object.keys(data);
            if (keys.includes('success')) {
                window.location.href = "/dashboard/"
            }
            else{
                errors = data['error'];
                var keys = Object.keys(errors);
                if(keys.includes('username')){
                    $('#login-form-username').val('');
                    $('#login-form-username').attr('placeholder', errors['username']);
                    $('#login-form-username').addClass("formInvalid");
                    $('#login-form-password').val('');
                    $('#login-form-password').attr('placeholder', 'password');
                    $('#login-form-password').removeClass("formInvalid");
                }
                else if(keys.includes('password')){
                    $('#login-form-password').val('');
                    $('#login-form-password').attr('placeholder', errors['password']);
                    $('#login-form-password').addClass("formInvalid");
                }else{
                    $("#forms").hide();
                    $("#wait").show();
                    $('form[name="login_form"]').trigger("reset");
                }
            }
        }
    });
});
$('#submit_register').bind('click', function() {
    $.ajax({
        type : "POST",
        url : '/register/',
        data: JSON.stringify({'username':$('#register-form-username').val(),
                              'password':$('#register-form-password').val(),
                              'confirm':$('#register-form-confirm').val(),
                              'email':$('#register-form-email').val()}),
        contentType: 'application/json;charset=UTF-8',
        success: function(data) {
            var keys = Object.keys(data);
            var keys = Object.keys(data);
            if (keys.includes('success')) {
                $("#forms").hide();
                $("#info").show();
                $('form[name="register_form"]').trigger("reset");
                $('form').animate({
                    height: "toggle",
                    opacity: "toggle"
                }, "slow");
            } else {
                errors = data['error']
                keys = Object.keys(errors);
                if (keys.includes('username')){
                    $('#register-form-username').val('');
                    $('#register-form-password').val('');
                    $('#register-form-confirm').val('');
                    $('#register-form-username').attr('placeholder', errors['username']);
                    $('#register-form-username').addClass("formInvalid");
                }
                if (keys.includes('email')){
                    $('#register-form-email').val('');
                    $('#register-form-password').val('');
                    $('#register-form-confirm').val('');
                    $('#register-form-email').attr('placeholder', errors['email']);
                    $('#register-form-email').addClass("formInvalid");
                }
                if (keys.includes('password')){
                    $('#register-form-password').val('');
                    $('#register-form-confirm').val('');
                    $('#register-form-password').attr('placeholder', errors['password']);
                    $('#register-form-password').addClass("formInvalid");
                }
            }
        }
    });
});
// Inject our CSRF token into our AJAX request.
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", "{{ form.csrf_token._value() }}")
        }
    }
})
$('#btn_return').bind('click', function() {
    $("#forms").show();
    $("#info").hide();
});
$('#btn_home').bind('click', function() {
    $("#forms").show();
    $("#wait").hide();
});