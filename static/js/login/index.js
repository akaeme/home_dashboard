$('.message span').click(function(){
   $('form').animate({height: "toggle", opacity: "toggle"}, "slow");
});

$('#submit_login').bind('click', function() {
    $.getJSON('/login/', {
      username: $('#login-form-username').val(),
      password: $('#login-form-password').val(),
    }, function(data) {
      $("#forms").hide();
      $("#info").show();
    });
    return false;
  });
$('#submit_register').bind('click', function() {
    $.getJSON('/register/', {
      username: $('#register-form-username').val(),
      password: $('#register-form-password').val(),
      confirm: $('#register-form-confirm').val(),
      email: $('#register-form-email').val(),
    }, function(data) {
      $("#forms").hide();
      $("#info").show();
      var keys = Object.keys(data);
      console.log(keys);
    });
    return false;
  });