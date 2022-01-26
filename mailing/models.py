from datetime import date

import csv
import requests
from requests.auth import HTTPBasicAuth
from django.db import models

from api.tasks import say2boss


class SmsConfig(models.Model):
    site = models.OneToOneField("api.Site", on_delete=models.SET_NULL, null=True, blank=True, unique=True)
    url = models.CharField(max_length=64, default='https://gate.smsaero.ru/v2/', blank=True)
    login = models.CharField(max_length=32, default='', blank=True)
    key = models.CharField(max_length=32, default='', blank=True)
    sign = models.CharField(max_length=32, default='Church22', blank=True)
    text = models.TextField(default='', blank=True)

    def __str__(self):
        return f'{self.site}'

    def mailing(self):
        now = date.today()
        peoples = People.objects.filter(site=self.site, birthday__day=now.day, birthday__month=now.month
                                        ).exclude(sent=now).exclude(phone='').values_list('pk', 'fio', 'phone')
        success = list()
        for pk, fio, phone in peoples:
            if self.send(phone, self.text):
                say2boss(f'Отправлено поздравление с др {fio}')
                success.append(pk)
        if success:
            People.objects.filter(pk__in=success).update(sent=now)

    def import_csv(self, path):
        # TODO site empty
        peoples = list()
        with open(path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('fio'):
                    birthday = row['Дата']
                    phone = ''.join(x for x in row['телефон'] if x.isdigit())
                    if phone[0] == '8':
                        phone = '7' + phone[1:]
                    fio = row['Ф.И.О.']
                    peoples.append(People(site=self.site, fio=fio, phone=phone, birthday=birthday))
        People.objects.bulk_create(peoples, ignore_conflicts=True)

    def request(self, endpoint='auth', *, answer=None, json: dict = None):
        """False | True | None | Any"""
        response = requests.post(f'{self.url}{endpoint}', json=json, auth=HTTPBasicAuth(self.login, self.key))
        if response.ok:
            if answer is True:
                return response.json()
            elif answer:
                return (response.json()['data'] or {}).get(answer)
            return True
        print(response.text)
        return False

    def send(self, phone, text):
        return self.request('sms/send', answer='id', json=dict(number=phone, text=text, sign=self.sign))

    def balance(self):
        return self.request('balance', answer='balance')

    def status(self, msg_id: int):
        return self.request('sms/status', answer='status', json=dict(id=msg_id))


class People(models.Model):
    site = models.ForeignKey("api.Site", on_delete=models.SET_NULL, null=True, blank=True)
    fio = models.CharField(max_length=255, default='')
    phone = models.CharField(max_length=16, default='', blank=True)
    birthday = models.DateField(null=True, blank=True)
    sent = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.fio} {self.site}'
