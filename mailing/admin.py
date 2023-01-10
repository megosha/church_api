from datetime import datetime
import locale

from django.contrib import admin
from django.utils.dateparse import parse_date
from django import forms
from import_export import resources
from import_export.fields import Field
from import_export.admin import ImportMixin
from import_export.forms import ImportForm

from api.models import Site
from mailing import models


@admin.register(models.SmsConfig)
class SmsConfigAdmin(admin.ModelAdmin):
    list_display = ["site"]


class PeopleResource(resources.ModelResource):
    fio = Field(attribute='fio', column_name='Ф.И.О.')
    phone = Field(attribute='phone', column_name='телефон')
    birthday = Field(attribute='birthday', column_name='Дата')
    site = Field(attribute='site')

    class Meta:
        model = models.People
        skip_unchanged = True
        fields = ('fio', 'phone', 'birthday', 'site')
        import_id_fields = ('fio',)
        widgets = {
            'birthday': {'format': '%d %B'},
        }

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        # skip no fio|phone, format birthday, phone
        locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
        fio_index = dataset.headers.index('Ф.И.О.')
        birthday_index = dataset.headers.index('Дата')
        phone_index = dataset.headers.index('телефон')
        delete = []
        for row_index in range(0, len(dataset)):
            row = dataset[row_index]
            if row[fio_index]:
                new_row = list()
                for col_index, col in enumerate(row):
                    col = col.strip() if isinstance(col, str) else '' if col is None else col
                    if col_index == birthday_index:
                        try:
                            col = parse_date(col) or datetime.strptime(col, '%d %B').strftime('%Y-%m-%d')
                        except Exception as exc:
                            print(exc)
                            delete.append(row_index)
                            break
                    elif col_index == phone_index:
                        col = str(col)
                        if col.startswith('+'):
                            col = col[1:]
                        if not col.isdigit():
                            # col = re.sub('\D', '', col)
                            print(row)
                            delete.append(row_index)
                            break
                        if col.startswith('8'):
                            col = '7' + col[1:]
                    new_row.append(col)
                else:
                    dataset[row_index] = new_row
            else:
                delete.append(row_index)
        for index in sorted(delete, reverse=True):
            del dataset[index]
        return dataset


class CustomImportForm(ImportForm):
    site = forms.ModelChoiceField(queryset=Site.objects.all(), required=True)


@admin.register(models.People)
class PeopleAdmin(ImportMixin, admin.ModelAdmin):
    list_display = "fio", "phone", "birthday", "site", "sent", "notify", "notify_sent",
    search_fields = 'fio', 'phone',
    list_editable = 'notify',
    resource_class = PeopleResource

    def get_import_form(self):
        return CustomImportForm

    def get_form_kwargs(self, form, *args, **kwargs):
        # TODO site empty
        if isinstance(form, CustomImportForm):
            if form.is_valid():
                site = form.cleaned_data['site']
                kwargs.update({'site': site.id})
        return kwargs
