# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-22 01:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='device_token',
            field=models.TextField(max_length=200, null=True),
        ),
    ]