import json

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

    def post(self, request):
        # formoid.js: var API_URL = ('https:' == location.protocol ? 'https:' : 'http:') + '//api.electis.ru/form/';
        try:
            form = json.loads(next(iter(request.data)))['form']
            title = form['title']
            data = form['data']
        except Exception as e:
            return HttpResponse('{"error": "Ошибка данных: {e}"}'.format(e=str(e)))
        emails = ('andrey@ngbarnaul.ru',)
        form_obj = models.Form.objects.create(title=title, text=json.dumps(data, ensure_ascii=False))
        html = f'<h2>{title}</h2>' + '<br>'.join([f"{d[0]}: {d[1]}" for d in data])
        mail = EmailMultiAlternatives(title, html, settings.EMAIL_HOST_USER, emails)
        mail.content_subtype = "html"
        try:
            mail.send(fail_silently=False)
        except Exception as e:
            return HttpResponse('{"error": "Ошибка отправки сообщения: {e}"}'.format(e=str(e)))
        form_obj.sended = True
        form_obj.save()
        return HttpResponse('{"response": "OK"}')
