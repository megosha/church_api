from django.contrib import admin
from django.apps import apps


apps_models = apps.get_models()
for model in apps_models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
