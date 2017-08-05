# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-08-05 22:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stories2', '0009_auto_20170804_2125'),
        ('profiles2', '0006_auto_20170804_1404'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='publication',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='authors', to='stories2.Publication'),
        ),
    ]
