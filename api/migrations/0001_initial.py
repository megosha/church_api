# Generated by Django 2.2.11 on 2020-03-13 06:24

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', max_length=255)),
                ('function', models.CharField(blank=True, default='', max_length=255)),
                ('image', models.ImageField(blank=True, null=True, upload_to='')),
                ('about', models.TextField(blank=True, default='')),
                ('active', models.BooleanField(default=True)),
                ('position', models.SmallIntegerField(default=-10)),
                ('phone', models.CharField(blank=True, default='', max_length=32)),
                ('social_page', models.CharField(blank=True, default='', max_length=64)),
                ('social_vk', models.CharField(blank=True, default='', max_length=64)),
                ('social_fb', models.CharField(blank=True, default='', max_length=64)),
                ('social_ok', models.CharField(blank=True, default='', max_length=64)),
                ('social_insta', models.CharField(blank=True, default='', max_length=64)),
                ('social_youtube', models.CharField(blank=True, default='', max_length=64)),
            ],
            options={
                'ordering': ('position',),
            },
        ),
    ]