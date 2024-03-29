# Generated by Django 2.2.17 on 2021-04-08 02:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0031_main_all_command'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='profile',
            options={'ordering': ('position', 'site', 'name')},
        ),
        migrations.AddField(
            model_name='botcontact',
            name='rights',
            field=models.SmallIntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='bot_user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.BotContact'),
        ),
        migrations.AlterField(
            model_name='botcontact',
            name='username',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
