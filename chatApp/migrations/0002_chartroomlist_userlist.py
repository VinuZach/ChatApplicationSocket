# Generated by Django 4.1 on 2022-09-14 09:31

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chatApp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chartroomlist',
            name='userList',
            field=models.ManyToManyField(help_text='authorised users', to=settings.AUTH_USER_MODEL),
        ),
    ]
