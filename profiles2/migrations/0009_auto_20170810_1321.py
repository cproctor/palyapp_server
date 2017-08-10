# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-08-10 13:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles2', '0008_auto_20170807_1221'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='gender',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='publication',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='authors', to='stories2.Publication'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='race_ethnicity',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='role',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
