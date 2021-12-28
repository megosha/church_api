from django.contrib import admin

from mailing import models


@admin.register(models.SmsConfig)
class SmsConfigAdmin(admin.ModelAdmin):
    list_display = ["site"]


@admin.register(models.People)
class PeopleAdmin(admin.ModelAdmin):
    list_display = ["fio", "site", "birthday"]
