# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-08-04 14:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stories2', '0005_auto_20170804_1431'),
    ]

    operations = [
        migrations.AlterField(
            model_name='story',
            name='categories',
            field=models.ManyToManyField(blank=True, null=True, related_name='stories', to='stories2.Category'),
        ),
    ]
