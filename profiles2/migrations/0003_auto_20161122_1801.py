# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-22 18:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_profile_device_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='device_token',
            field=models.TextField(blank=True, default='', max_length=200),
            preserve_default=False,
        ),
    ]
