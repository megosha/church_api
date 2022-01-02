from datetime import date

import csv
import requests
from django.db import models


class SmsConfig(models.Model):
    site = models.OneToOneField("api.Site", on_delete=models.SET_NULL, null=True, blank=True)
    url = models.CharField(max_length=64, default='https://gate.smsaero.ru/v2/', blank=True)
    login = models.CharField(max_length=32, default='', blank=True)
    key = models.CharField(max_length=32, default='', blank=True)
    text = models.TextField(default='', blank=True)

    def __str__(self):
        return f'{self.site}'

    def mailing(self):
        now = date.today()
        peoples = People.objects.filter(birthday=now, sent__ne=now, phone__ne='').values_list('pk', 'fio', 'phone')
        success = list()
        for pk, fio, phone in peoples:
            if self.send(phone, self.text.format(fio=fio)):
                success.append(pk)
        if success:
            People.objects.filter(pk__in=success).update(sent=now)

    def send(self, phone, text):
        sign = ''
        response = requests.post(self.url + 'sms/send', params=dict(number=phone, text=text, sign=sign))
        if response.status_code == requests.status_codes.ok:
            return True

    def test(self):
        response = requests.post(self.url + 'auth')
        if response.status_code == requests.status_codes.ok:
            return True

    def import_csv(self, path):
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


class People(models.Model):
    site = models.ForeignKey("api.Site", on_delete=models.SET_NULL, null=True, blank=True)
    fio = models.CharField(max_length=255, default='')
    phone = models.CharField(max_length=16, default='', blank=True)
    birthday = models.DateField(null=True, blank=True)
    sent = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.fio} {self.site}'
