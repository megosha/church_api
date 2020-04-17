$(document).ready(function(){
  $("#robo_btn").click(function() {
    var sum = $("#robo_sum").val(),
      API_URL = ('https:' == location.protocol ? 'https:' : 'http:') + '//api.electis.ru/robokassa/';
    $.ajax({
      type: "POST",
      url: API_URL,
      data: sum
    }).done(function(data) {
      console.log(data);
    }).fail(function(data) {
      console.log('fail');
    });
  });
});
