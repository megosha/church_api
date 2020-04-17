$(document).ready(function(){
    var API_URL = ('https:' == location.protocol ? 'https:' : 'http:') + '//api.electis.ru/robokassa/';
    $.ajax({
      type: "POST",
      url: API_URL,
      beforeSend: function (xhr) {
        xhr.setRequestHeader ("Authorization", "Token 1e082d63efdd498d672b7531920312157d5b4aeb");
      },
    }).done(function(data) {
      console.log('success');
      document.getElementById("robo_div").innerHTML = data;
    }).fail(function(data) {
      console.log('fail');
    });
});
