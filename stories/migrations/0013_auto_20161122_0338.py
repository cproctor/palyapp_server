# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-22 03:38
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stories', '0012_auto_20161121_2022'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentUpvote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='upvotes', to=settings.AUTH_USER_MODEL)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='upvotes', to='stories.Comment')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='commentupvote',
            unique_together=set([('comment', 'author')]),
        ),
    ]
