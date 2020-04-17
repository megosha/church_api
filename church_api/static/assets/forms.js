//        var API_URL = ('https:' == location.protocol ? 'https:' : 'http:') + '//api.church22.ru/api/form/';
//        var API_URL = ('https:' == location.protocol ? 'https:' : 'http:') + '//api.electis.ru/api/form/';
$(function() {
      $('form').submit(function(e) {
        var form,
            $this = $(this),
            $form = $this.is('form') ? $this : $this.find('form'),
            $submit = $this.find('[type="submit"]');
        if ($submit.hasClass('btn-loading')) return;
        $.ajax({
          type: $form.attr('method'),
          url: $form.attr('action'),
          data: $form.serialize()
        }).done(function(data) {
          console.log('success');
        }).fail(function(data) {
          console.log('fail');
          $alert.html(data.message);
          $alert.removeClass('alert-success').addClass('alert-danger');
          $alert.removeAttr('hidden');
        });
        //отмена действия по умолчанию для кнопки submit
        e.preventDefault(); 
      });
    });

