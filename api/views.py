import json
import hashlib
import logging

from django.conf import settings
from django.core.mail.message import EmailMultiAlternatives
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework import viewsets, permissions
from rest_framework.views import APIView

from api import models, serializers


def send_email(title, text, emails: iter = ('andrey@ngbarnaul.ru',), as_html: bool = False):
    mail = EmailMultiAlternatives(title, text, settings.EMAIL_HOST_USER, emails)
    if as_html:
        mail.content_subtype = "html"
    try:
        mail.send(fail_silently=False)
    except Exception as Ex:
        return Ex


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = models.Profile.objects.filter(active=True)
    serializer_class = serializers.ProfileSerializer
    permission_classes = [permissions.DjangoModelPermissions]


class NewsViewSet(viewsets.ModelViewSet):
    queryset = models.News.objects.filter(active=True, date__lte=timezone.now(), section__active=True)
    serializer_class = serializers.NewsSerializer
    permission_classes = [permissions.DjangoModelPermissions]


class FormViewSet(APIView):
    permission_classes = [permissions.AllowAny]

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
        emails = ('andrey@ngbarnaul.ru', 'artorop@mail.ru', 'elenarun@mail.ru',)
        form_obj = models.Form.objects.create(title=title, text=json.dumps(data, ensure_ascii=False))
        result = send_email(title, html, emails, as_html=True)
        if isinstance(result, Exception):
            return self.resp(False, f'Ошибка отправки сообщения: {result}')
        form_obj.sended = True
        form_obj.save()
        return self.resp()


class RobokassaViewSet(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        mrh_login = settings.ROBOKASSA_LOGIN
        mrh_pass1 = settings.ROBOKASSA_PASS1
        inv_id = 1
        inv_desc = 'Добровольное пожертвование на деятельность церкви'
        def_sum = '500'
        crc = hashlib.md5(f'{mrh_login}::{inv_id}:{mrh_pass1}'.encode()).hexdigest()
        html = "<script src='https://auth.robokassa.ru/Merchant/PaymentForm/FormFLS.js?" \
               f"MerchantLogin={mrh_login}&DefaultSum={def_sum}&InvoiceID={inv_id}" \
               f"&Description={inv_desc}&SignatureValue={crc}'></script>"
        return HttpResponse(html)


class LogViewSet(APIView):
    permission_classes = [permissions.AllowAny]

    def dispatch(self, request, *args, **kwargs):
        logger = logging.getLogger('django')
        logger.info(f'{request.scheme} {request.method}:\n{request.body}')
        return HttpResponse('OK')


class AccountViewSet(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        if not request.user.is_authenticated:
            return HttpResponse(render_to_string('login_form.html'))
