from django.contrib import admin
from django.apps import apps
from rest_framework.authtoken.models import Token


apps_models = apps.get_models()
for model in apps_models:
    if model == Token:
        continue
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
