# Generated by Django 2.2.11 on 2020-03-15 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='social_email',
            field=models.CharField(blank=True, default='', max_length=64),
        ),
    ]