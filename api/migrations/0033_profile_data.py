# Generated by Django 2.2.24 on 2021-09-30 02:31

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0032_auto_20210408_0921'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='data',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
    ]
