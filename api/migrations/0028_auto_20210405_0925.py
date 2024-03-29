# Generated by Django 2.2.17 on 2021-04-05 02:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0027_site_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='main',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.Profile'),
        ),
        migrations.AlterField(
            model_name='site',
            name='path_prefix',
            field=models.CharField(blank=True, default='', help_text='biysk/', max_length=64),
        ),
    ]
