from datetime import datetime
import locale

from django.contrib import admin
from django.utils.dateparse import parse_date
from import_export import resources
from import_export.fields import Field
from import_export.admin import ImportMixin

from mailing import models


@admin.register(models.SmsConfig)
class SmsConfigAdmin(admin.ModelAdmin):
    list_display = ["site"]


class PeopleResource(resources.ModelResource):
    # TODO site
    fio = Field(attribute='fio', column_name='Ф.И.О.')
    phone = Field(attribute='phone', column_name='телефон')
    birthday = Field(attribute='birthday', column_name='Дата')

    class Meta:
        model = models.People
        skip_unchanged = True
        fields = ('fio', 'phone', 'birthday',)
        import_id_fields = ('fio',)
        widgets = {
            'birthday': {'format': '%d %B'},
        }

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        # skip no fio, format birthday
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
                    col = col.strip() if isinstance(col, str) else '' if col is None else str(col)
                    if col_index == birthday_index:
                        try:
                            col = parse_date(col) or datetime.strptime(col, '%d %B').strftime('%Y-%m-%d')
                        except Exception as exc:
                            print(exc)
                            delete.append(row_index)
                            break
                    elif col_index == phone_index:
                        # if not col:
                        #     col = ''
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


@admin.register(models.People)
class PeopleAdmin(ImportMixin, admin.ModelAdmin):
    list_display = ["fio", "site", "birthday"]
    resource_class = PeopleResource
