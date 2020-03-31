import json
import hashlib

from django.conf import settings
from django.core.mail.message import EmailMultiAlternatives
from django.http import HttpResponse
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from api import models, serializers


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = models.Profile.objects.filter(active=True)
    serializer_class = serializers.ProfileSerializer
    permission_classes = [permissions.DjangoModelPermissions]


class FormViewSet(APIView):
    permission_classes = [AllowAny]

    def resp(self, status: bool = True, msg: str = 'OK'):
        key = 'response' if status else 'error'
        return HttpResponse(json.dumps({key: msg}))

    def post(self, request):
        # formoid.js: var API_URL = ('https:' == location.protocol ? 'https:' : 'http:') + '//api.electis.ru/form/';
        try:
            form = json.loads(next(iter(request.data)))['form']
            title = form['title']
            data = form['data']
            html = f'<h2>{title}</h2>' + '<br>'.join([f"{d[0]}: {d[1]}" for d in data])
        except Exception as e:
            return self.resp(False, f'Ошибка данных: {e}')
        emails = ('andrey@ngbarnaul.ru',)
        form_obj = models.Form.objects.create(title=title, text=json.dumps(data, ensure_ascii=False))
        mail = EmailMultiAlternatives(title, html, settings.EMAIL_HOST_USER, emails)
        mail.content_subtype = "html"
        try:
            mail.send(fail_silently=False)
        except Exception as e:
            return self.resp(False, f'Ошибка отправки сообщения: {e}')
        form_obj.sended = True
        form_obj.save()
        return self.resp()


class RobokassaViewSet(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        mrh_login = settings.ROBOKASSA_LOGIN
        mrh_pass1 = settings.ROBOKASSA_PASS1
        inv_id = 1
        inv_desc = 'Добровольное пожертвование на деятельность церкви'
        def_sum = '500'
        crc = hashlib.md5(f'{mrh_login}::{inv_id}:{mrh_pass1}'.encode()).hexdigest()
        html = "<script language=JavaScript src='https://auth.robokassa.ru/Merchant/PaymentForm/FormFLS.js?"\
               f"MerchantLogin={mrh_login}&DefaultSum={def_sum}&InvoiceID={inv_id}"\
               f"&Description={inv_desc}&SignatureValue={crc}'></script>"
        return HttpResponse(html)
