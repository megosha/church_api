import json
import hashlib
import logging

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework import viewsets, permissions
from rest_framework.views import APIView

from api import models, serializers, tasks
from api.tasks import ViewTasks
from front.methods import send_email


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = models.Profile.objects.filter(active=True)
    serializer_class = serializers.ProfileSerializer
    permission_classes = [permissions.DjangoModelPermissions]


class NewsViewSet(viewsets.ModelViewSet):
    queryset = models.News.objects.filter(active=True, date__lte=timezone.now(), section__active=True)
    serializer_class = serializers.NewsSerializer
    permission_classes = [permissions.DjangoModelPermissions]


class FormView(APIView):
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
        text = json.dumps(data, ensure_ascii=False)
        form_obj = models.Form.objects.create(title=title, text=text, site=request.site)
        try:
            tasks.say2boss(f'{title}, {text}')
        except Exception as exc:
            print(exc)
        result = send_email(title, html, settings.FEEDBACK_EMAILS, as_html=True)
        if isinstance(result, Exception):
            return self.resp(False, f'Ошибка отправки сообщения: {result}')
        form_obj.sended = True
        form_obj.save()
        return self.resp()


class RobokassaView(APIView):
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


class LogView(APIView):
    permission_classes = [permissions.AllowAny]

    def dispatch(self, request, *args, **kwargs):
        logger = logging.getLogger('django')
        logger.info(f'{request.scheme} {request.method}:\n{request.body}')
        return HttpResponse('OK')


class AccountView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        if not request.user.is_authenticated:
            return HttpResponse(render_to_string('login_form.html'))


class TaskView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.TaskSerializer

    def post(self, request):
        profile = request.user.profile
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = ViewTasks(**serializer.validated_data, profile_id=profile.id)
        task._proceed()
        return HttpResponse('OK')
