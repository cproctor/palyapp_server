# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-08-03 18:58
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stories2', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StoryLike',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('liker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='liked_stories', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Title')),
                ('weight', models.FloatField(default=0, verbose_name='Weight')),
                ('pub_date', models.DateTimeField(verbose_name='Date published')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TopicLike',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('liker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='liked_topics', to=settings.AUTH_USER_MODEL)),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='stories2.Topic')),
            ],
        ),
        migrations.RemoveField(
            model_name='comment',
            name='anonymous',
        ),
        migrations.AddField(
            model_name='story',
            name='weight',
            field=models.FloatField(default=0, verbose_name='Weight'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='story',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='stories2.Story'),
        ),
        migrations.AddField(
            model_name='topic',
            name='stories',
            field=models.ManyToManyField(related_name='topics', to='stories2.Story'),
        ),
        migrations.AddField(
            model_name='storylike',
            name='story',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='stories2.Story'),
        ),
        migrations.AddField(
            model_name='comment',
            name='topic',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='stories2.Topic'),
        ),
    ]
